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

    # TODO: add a field for getting an image file
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
    
    
    client = User.query.get(current_client_id)
    if not client:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'Failed request',
            'status': 'Failed'
        }), 400
    
    
    travel_package = Package.query.get(package_id)
    if not travel_package:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'Package has not been found',
            'status': 'Failed'
        }), 404
    
  
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
    
    
    agency = Agency.query.get(travel_package.agency_id)
    if not agency:
        return jsonify({
            'message': 'Failed',
            'customer_message': 'Package is not associated with any agency',
            'status': 'Failed'
        }), 400
    
    
    first_name = client.first_name  
    email = client.email  
    price = travel_package.price  
 
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
    
   
    new_booking = Booking(
        user_id=current_client_id,
        package_id=package_id,
        booking_date=datetime.utcnow(),
        status='Successful',  
        billing_id=new_billing.id,
        agency_id=agency.id  
    )
    db.session.add(new_booking)
    db.session.commit()
    
   
    return jsonify({
        'message': 'Successful',
        'customer_message': 'You have successfully booked',
        'status': 'Successful',
        'booking_id': new_booking.id,
        'billing_id': new_billing.id,
        'first_name': first_name,
        'email': email,
        'price': price,
        'agency_name': agency.agency_name,  
        'agency_id': agency.id       
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
        return jsonify({
            'message': 'Only agencies can access this information',
            'status': 'Failed'
        }), 400

    
    data = request.get_json()
    if not data or 'package_id' not in data:
        return jsonify({
            'message': 'Package ID is required in the request body',
            'status': 'Failed'
        }), 400

    package_id = data['package_id']

    
    package = Package.query.filter_by(id=package_id, agency_id=agency.id).first()
    if not package:
        return jsonify({
            'message': 'Package not found or does not belong to this agency',
            'status': 'Failed'
        }), 404

    
    reviews = Review.query.filter_by(package_id=package.id).all()

   
    if not reviews:
        return jsonify({
            'message': 'No reviews found for this package',
            'status': 'Failed'
        }), 404

    
    return jsonify({
        'message': 'Reviews retrieved successfully',
        'status': 'Successful',
        'reviews': [review.to_json() for review in reviews]
    }), 200

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

   
    agency = Agency.query.get(current_user_id)

    if not agency:
        return jsonify({
            'message': "Only agencies can access this information",
            'customer_message': "You are not authorized to access this info",
            'status': "Failed"
        }), 400

    
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

    
    if not bookings:
        return jsonify({
            'message': "No bookings found",
            'customer_message': "This agency does not have any bookings",
            'status': "Failed"
        }), 404

    
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

    
    agency = Agency.query.get(current_user_id)

    if not agency:
        return jsonify({'message': 'Only agencies can access this information'}), 400

    
    package_id = request.json.get('package_id')

    if not package_id:
        return jsonify({'message': 'Package ID is required'}), 400

    
    package = Package.query.filter_by(id=package_id, agency_id=agency.id).first()

    if not package:
        return jsonify({"message": "Package not found or doesn't belong to your agency"}), 400

    try:
        
        for booking in package.bookings:
            db.session.delete(booking)

        
        for review in package.reviews:
            db.session.delete(review)

        
        for photo in package.photos:
            db.session.delete(photo)

@routes_bp.route('/package/update', methods=['PUT'])
@jwt_required()
def update_package():
    try:
        current_user_id = get_jwt_identity()
        agency = Agency.query.get(current_user_id)

        if not agency:
            return jsonify({'message': 'Only agencies can access this information'}), 403

        package_id = request.json.get('package_id')
        package_name = request.json.get('package_name')
        price = request.json.get('price')
        location = request.json.get('location')
        day_count = request.json.get('day_count')
        package_type = request.json.get('package_type')
        inclusions = request.json.get('inclusions')
        exclusions = request.json.get('exclusions')

        if not package_id or not isinstance(package_id, int):
            return jsonify({'message': 'Valid Package ID is required'}), 400

        package = Package.query.filter_by(id=package_id, agency_id=agency.id).first()

        if not package:
            return jsonify({"message": "Package not found or doesn't belong to your agency"}), 404

        # Update only the fields provided in the request
        if package_name:
            package.package_name = package_name
        if price:
            package.price = price
        if location:
            package.location = location
        if day_count:
            package.day_count = day_count
        if package_type:
            package.package_type = package_type
        if inclusions:
            package.inclusions = inclusions
        if exclusions:
            package.exclusions = exclusions

        db.session.commit()

        return jsonify({"message": "Package updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating the package", "error": str(e)}), 500
