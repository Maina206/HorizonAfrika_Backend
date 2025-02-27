from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from Models import db, Billing, Package, Booking, Review,Photo,User
from datetime import datetime,timedelta
from auth import  Agency


routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/packages', methods=['GET'])
@jwt_required()
def get_packages():
    current_user_id = get_jwt_identity()  
    agency= Agency.query.get(current_user_id) 

    if not agency:
        return jsonify({'error': 'Unauthorized access'}), 403

       
    packages = Package.query.filter_by(agency=agency).all() 
    return jsonify([package.to_json() for package in packages])

@routes_bp.route('/packages', methods=['POST'])
@jwt_required()
def create_package():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    agency = Agency.query.get(current_user_id)

    if not agency:
        return jsonify({"error": "Only agencies can create packages"}), 403

    
    required_fields = ['package_name', 'price', 'day_count', 'location', 'package_type', 'inclusions', 'exclusions']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    
    if Package.query.filter_by(package_name=data['package_name']).first():
        return jsonify({"message": "Package already exists"}), 400

    
    new_package = Package(
        package_name=data['package_name'],
        price=data['price'],
        day_count=data['day_count'],
        location=data['location'],
        package_type=data['package_type'],
        inclusions=data['inclusions'],
        exclusions=data['exclusions'],
        agency_id=agency.id  
    )

    try:
        db.session.add(new_package)
        db.session.commit()

        
        return jsonify({
            "message": "Package created successfully",
            "package": {
                "id": new_package.id,
                "package_name": new_package.package_name,
                "price": new_package.price,
                "day_count": new_package.day_count,
                "location": new_package.location,
                "package_type": new_package.package_type,
                "inclusions": new_package.inclusions,
                "exclusions": new_package.exclusions,
                "agency_id": new_package.agency_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    


@routes_bp.route('/packages/book', methods=['POST'])
@jwt_required()
def book_now():
    current_client_id = get_jwt_identity()

    data = request.get_json()
    if not data or 'package_id' not in data:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'Failed request',
            'status': 'Failed'
        }), 400
    
    package_id = data['package_id']
    
    # Get the client information
    client = User.query.get(current_client_id)
    if not client:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'Failed request',
            'status': 'Failed'
        }), 400
    
    # Get the travel package information
    travel_package = Package.query.get(package_id)
    if not travel_package:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'Package has not been found',
            'status': 'Failed'
        }), 404
    
    # Check if the current user has already made a booking for the same package and is still pending
    existing_booking = Booking.query.filter_by(
        user_id=current_client_id,
        package_id=package_id,
        status='Pending'
    ).first()
    
    if existing_booking:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'You have not paid the full amount',
            'status': 'Pending'
        }), 400
    
    # Fetch the agency associated with the travel package
    agency = Agency.query.get(travel_package.agency_id)
    if not agency:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'Package is not associated with any agency',
            'status': 'Failed'
        }), 400
    
    # Additional information
    first_name = client.first_name  
    email = client.email  
    price = travel_package.price  
    
    # Create new billing entry
    new_billing = Billing(
        package_id=package_id,
        user_id=current_client_id,
        amount=price,
        payment_status='Pending',  
        phone_number=client.phone_number,  
        checkoutID=None, 
        response_description=None,
        customer_message='You have successfully booked' 
    )
    db.session.add(new_billing)
    db.session.commit()
    
    # Create a new booking entry, including the agency_id in the booking
    new_booking = Booking(
        user_id=current_client_id,
        package_id=package_id,
        booking_date=datetime.utcnow(),
        status='Successful',  
        billing_id=new_billing.id,
        agency_id=agency.id  # Here we are assigning the correct agency_id to the booking
    )
    db.session.add(new_booking)
    db.session.commit()
    
    # Return the booking confirmation and agency details
    return jsonify({
        'message': 'Successful',
        'customer_message': 'You have successfully booked',
        'status': 'Successful',
        'booking_id': new_booking.id,
        'billing_id': new_billing.id,
        'first_name': first_name,
        'email': email,
        'price': price,
        'agency_name': agency.agency_name,  # Agency name (optional)
        'agency_id': agency.id       # Agency id (mandatory)
    }), 201

@routes_bp.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    
    if not data or 'rating' not in data or 'review_texts' not in data or 'package_id' not in data:
        return jsonify({'error': 'must put all the credentials '}), 400

    package_id = data['package_id']

    
    client = User.query.get(current_user_id)
    if not client:
        return jsonify({'error': 'Only users can make reviews'}), 400


    travel_package = Package.query.get(package_id)
    if not travel_package:
        return jsonify({'error': 'Package does not exist'}), 400


    existant_review = Review.query.filter_by(
        user_id=current_user_id,
        package_id=package_id
    ).first()
    if existant_review:
        return jsonify({'error': 'You have already reviewed this package'}), 400

    
    new_review = Review(
        user_id=current_user_id,
        package_id=package_id,
        rating=data['rating'],
        review_texts=data['review_texts'],
        date=datetime.utcnow(),
        image=data.get('image')  
    )

    db.session.add(new_review)
    db.session.commit()

    
    return jsonify({
        'message': 'You have successfully reviewed this package',
        'user_id': current_user_id,
        'package_id': package_id,
        'rating': data['rating'],
        'review_texts': data['review_texts'],
        'first_name': client.first_name,
        'email': client.email,
        'image': data.get('image')
    }), 201


@routes_bp.route('/reviews', methods=['GET'])
@jwt_required()

def get_reviews():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message":"only users can access their reviews"}),400
    
    reviews = Review.query.filter_by(user=user).all()

    return jsonify([review.to_json() for review in reviews])


@routes_bp.route('/reviews/agency', methods=['POST'])
@jwt_required()
def get_package_reviews_for_agency():
    
    current_user_id = get_jwt_identity()
    
    agency = Agency.query.get(current_user_id)

    if not agency:
        return jsonify({'message': 'Only agencies can access this info'}), 400
    
    
    packages = Package.query.filter_by(agency_id=agency.id).all()  
    
    if not packages:
        return jsonify({"message": "No packages found for this agency"}), 404
    
    
    reviews = []
    for package in packages:
        package_reviews = Review.query.filter_by(package_id=package.id).all() 
        reviews.extend(package_reviews)

    if not reviews:
        return jsonify({"message": "No reviews found for the agency's packages"}), 404
    
    # Return the reviews as JSON
    return jsonify([review.to_json() for review in reviews])  # Assuming review has a to_json method


# @routes_bp.route('/bookings', methods=['GET'])
# @jwt_required()

# def get_bookings():
#     current_user_id = get_jwt_identity()

#     agency = Agency.query.get(current_user_id)

#     if not agency:
#         return jsonify({'message':"only agencies can access this info"}),400
    

#     bookings = Booking.query.filter_by(agency=agency).all()

#     return jsonify([booking.to_json() for booking in bookings])
    

@routes_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    current_user_id = get_jwt_identity()

    # Check if the current user is an agency
    agency = Agency.query.get(current_user_id)

    if not agency:
        return jsonify({
            'message': "Only agencies can access this information",
            'customer_message': "You are not authorized to access this info",
            'status': "Failed"
        }), 400

    # Query all bookings for the agency and join the necessary tables
    bookings = db.session.query(
        Booking,
        User.first_name,
        User.email,
        Package.price,
        Package.location,
        Package.package_name.label('package_name')
    ).join(User, Booking.user_id == User.id) \
     .join(Package, Booking.package_id == Package.id) \
     .filter(Booking.agency_id == current_user_id) \
     .all()

    # If no bookings found
    if not bookings:
        return jsonify({
            'message': "No bookings found",
            'customer_message': "This agency does not have any bookings",
            'status': "Failed"
        }), 404

    # Format the results to return the requested data
    booking_data = []
    for booking, first_name, email, price, location, package_name in bookings:
        booking_data.append({
            
            'user_first_name': first_name,
            'user_email': email,
            'price_paid': price,
            'location': location,
            'package_name': package_name
        })

    return jsonify({
        'message': 'Successful',
        'customer_message': 'Bookings retrieved successfully',
        'status': 'Successful',
        'bookings': booking_data
    }), 200

# @routes_bp.route('/package/delete', methods=['DELETE'])
# @jwt_required()

# def delete_package():
#     current_user_id = get_jwt_identity()

#     agency = Agency.query.get(current_user_id)

#     if not agency:
#         return jsonify({'message':'only agencies can access info'}),400
    
#     package = Package.query.filter_by(agency=agency).all()

#     if not package:
#         return jsonify({"message":"package not found"}),400
    
    
  

@routes_bp.route('/package/delete', methods=['DELETE'])
@jwt_required()
def delete_package():
    current_user_id = get_jwt_identity()

    # Get the agency object corresponding to the current logged-in user
    agency = Agency.query.get(current_user_id)

    if not agency:
        return jsonify({'message': 'Only agencies can access this information'}), 400

    # Get the package ID from the request
    package_id = request.json.get('package_id')

    if not package_id:
        return jsonify({'message': 'Package ID is required'}), 400

    # Find the package that belongs to the agency
    package = Package.query.filter_by(id=package_id, agency_id=agency.id).first()

    if not package:
        return jsonify({"message": "Package not found or doesn't belong to your agency"}), 400

    try:
        # Manually delete associated records (e.g., bookings, reviews, photos, billings)
        # Example: Delete bookings associated with the package
        for booking in package.bookings:
            db.session.delete(booking)

        # Example: Delete reviews associated with the package
        for review in package.reviews:
            db.session.delete(review)

        # Example: Delete photos associated with the package
        for photo in package.photos:
            db.session.delete(photo)

        # Example: Delete billings associated with the package
        for billing in package.billings:
            db.session.delete(billing)

        # Now delete the package
        db.session.delete(package)
        db.session.commit()
        return jsonify({"message": "Package and associated records deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to delete package: {str(e)}"}), 500