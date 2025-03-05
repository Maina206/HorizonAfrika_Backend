from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from Models import db, Billing, Package, Booking, Review,Photo,User
from datetime import datetime,timedelta
from auth import  Agency
from cloudinary_config import upload_photo
from Mpesa import MpesaAPI


routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/packages/all', methods=['GET'])
def get_all_packages():
    try:
        packages = Package.query.all()
        
        return jsonify([package.to_json() for package in packages]), 200

    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500



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
    try:
        current_user_id = get_jwt_identity()
        agency = Agency.query.get(current_user_id)

        if not agency:
            return jsonify({"error": "Only agencies can create packages"}), 403

        # Handle both form data and JSON data
        data = request.form.to_dict() if request.form else request.get_json()
        
        if not data:
            return jsonify({"message": "No data provided"}), 400

        required_fields = ['package_name', 'price', 'day_count', 'location', 'package_type', 'inclusions', 'exclusions']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Missing required fields"}), 400

        if Package.query.filter_by(package_name=data['package_name']).first():
            return jsonify({"message": "Package already exists"}), 400

        # Create new package
        new_package = Package(
            package_name=data['package_name'],
            price=float(data['price']),
            day_count=int(data['day_count']),
            location=data['location'],
            package_type=data['package_type'],
            inclusions=data['inclusions'],
            exclusions=data['exclusions'],
            agency_id=agency.id
        )

        db.session.add(new_package)
        # db.session.flush()
        db.session.commit()  

        # Handle photo uploads if present
        uploaded_photos = []
        if 'photos' in request.files:
            photos = request.files.getlist('photos') # This handles receiving of photos
            print(request.files.getlist('photos'))

            for photo_file in photos:
                if photo_file.filename != '':
                    # Upload to Cloudinary
                    upload_result = upload_photo(photo_file)
                    print(upload_result)
                    
                    if upload_result['success']:
                        # Save photo URL to database
                        new_photo = Photo(
                            package_id=new_package.id,
                            photo_url=upload_result['url']
                        )
                        db.session.add(new_photo)
                        uploaded_photos.append({
                            'url': upload_result['url']
                        })

        db.session.commit()

        response_data = {
            "message": "Package created successfully",
            "package": new_package.to_json()
        }

        if uploaded_photos:
            response_data["uploaded_photos"] = uploaded_photos

        return jsonify(response_data), 201

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
            'customer_message': 'You currently have a booking',
            'status': 'Already booked'
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

   
        for billing in package.billings:
            db.session.delete(billing)

       
        db.session.delete(package)
        db.session.commit()
        return jsonify({"message": "Package and associated records deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to delete package: {str(e)}"}), 500

        
@routes_bp.route('/package/update', methods=['PUT'])
@jwt_required()
def update_package():
    try:
        current_user_id = get_jwt_identity()
        agency = Agency.query.get(current_user_id)

        if not agency:
            return jsonify({'message': 'Only agencies can access this information'}), 403

        # Handle both form data and JSON data
        package_id = request.form.get('package_id') or request.json.get('package_id')
        package_name = request.form.get('package_name') or request.json.get('package_name')
        price = request.form.get('price') or request.json.get('price')
        location = request.form.get('location') or request.json.get('location')
        day_count = request.form.get('day_count') or request.json.get('day_count')
        package_type = request.form.get('package_type') or request.json.get('package_type')
        inclusions = request.form.get('inclusions') or request.json.get('inclusions')
        exclusions = request.form.get('exclusions') or request.json.get('exclusions')

        if not package_id:
            return jsonify({'message': 'Package ID is required'}), 400

        try:
            package_id = int(package_id)
        except ValueError:
            return jsonify({'message': 'Valid Package ID is required'}), 400

        package = Package.query.filter_by(id=package_id, agency_id=agency.id).first()

        if not package:
            return jsonify({"message": "Package not found or doesn't belong to your agency"}), 404

        # Update text fields if provided
        if package_name:
            package.package_name = package_name
        if price:
            package.price = float(price)
        if location:
            package.location = location
        if day_count:
            package.day_count = int(day_count)
        if package_type:
            package.package_type = package_type
        if inclusions:
            package.inclusions = inclusions
        if exclusions:
            package.exclusions = exclusions

        # Handle photo uploads if present
        uploaded_photos = []
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo_file in photos:
                if photo_file.filename != '':
                    # Upload to Cloudinary
                    upload_result = upload_photo(photo_file)
                    
                    if upload_result['success']:
                        # Save photo URL to database
                        new_photo = Photo(
                            package_id=package_id,
                            photo_url=upload_result['url']
                        )
                        db.session.add(new_photo)
                        uploaded_photos.append({
                            'url': upload_result['url']
                        })

        db.session.commit()

        response_data = {
            "message": "Package updated successfully",
            "package": package.to_json()
        }
        
        if uploaded_photos:
            response_data["uploaded_photos"] = uploaded_photos

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating the package", "error": str(e)}), 500

@routes_bp.route('/packages/upload-photo', methods=['POST'])
@jwt_required()
def upload_package_photo():
    try:
        current_user_id = get_jwt_identity()
        agency = Agency.query.get(current_user_id)

        if not agency:
            return jsonify({'message': 'Only agencies can upload photos'}), 403

        if 'photo' not in request.files:
            return jsonify({'message': 'No photo file provided'}), 400

        package_id = request.form.get('package_id')
        if not package_id:
            return jsonify({'message': 'Package ID is required'}), 400

        package = Package.query.filter_by(id=package_id, agency_id=agency.id).first()
        if not package:
            return jsonify({'message': 'Package not found or does not belong to your agency'}), 404

        photo_file = request.files['photo']
        if photo_file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        # Upload to Cloudinary
        upload_result = upload_photo(photo_file)
        
        if not upload_result['success']:
            return jsonify({'message': 'Failed to upload photo', 'error': upload_result['error']}), 500

        # Save photo URL to database
        new_photo = Photo(
            package_id=package_id,
            photo_url=upload_result['url']
        )
        
        db.session.add(new_photo)
        db.session.commit()

        return jsonify({
            'message': 'Photo uploaded successfully',
            'photo': {
                'id': new_photo.id,
                'url': new_photo.photo_url,
                'package_id': new_photo.package_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    
#M-Pesa Routes
@routes_bp.route('/packages/initiate-payment', methods=['POST'])
@jwt_required()
def initiate_payment():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        data = request.get_json()

        if not data or 'package_id' not in data or 'phone_number' not in data:
            return jsonify({'message': 'Package ID and phone number are required'}), 400

        package = Package.query.get(data['package_id'])
        if not package:
            return jsonify({'message': 'Package not found'}), 404

        # Format phone number (remove leading 0 and add country code if necessary)
        phone_number = data['phone_number']
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number

        # Validate phone number format
        if not phone_number.isdigit() or len(phone_number) != 12:
            return jsonify({'message': 'Invalid phone number format. Use format: 0712345678 or 254712345678'}), 400

        # Create a reference number
        reference = f"PKG{package.id}USR{user.id}{datetime.now().strftime('%Y%m%d%H%M')}"

        # Initialize M-Pesa API
        mpesa = MpesaAPI()
        
        # Create billing record
        billing = Billing(
            package_id=package.id,
            user_id=user.id,
            amount=1,
            payment_status='Pending',
            phone_number=phone_number,
            customer_message='Payment initiated'
        )
        db.session.add(billing)
        db.session.flush()

        # Initiate STK Push
        result = mpesa.initiate_stk_push(
            phone_number=phone_number,
            amount=1,
            reference=reference
        )

        if result['success']:
            # Update billing record with M-Pesa details
            billing.checkoutID = result['checkout_request_id']
            billing.response_description = result['message']
            db.session.commit()

            response_data = {
                'message': 'Payment initiated successfully',
                'checkout_request_id': result['checkout_request_id'],
                'merchant_request_id': result['merchant_request_id'],
                'billing_id': billing.id,
                'amount': package.price,
                'phone_number': phone_number
            }
            return jsonify(response_data), 200
        else:
            db.session.rollback()
            return jsonify({
                'message': 'Failed to initiate payment',
                'error': result['message']
            }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@routes_bp.route('/api/mpesa-callback', methods=['POST'])
def mpesa_callback():
    try:
        # Get the callback data
        callback_data = request.get_json()
        
        # Extract relevant information from callback
        result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        
        # Find the corresponding billing record
        billing = Billing.query.filter_by(checkoutID=checkout_request_id).first()
        
        if not billing:
            return jsonify({'message': 'Billing record not found'}), 404
        
        if result_code == 0:  # Successful payment
            # Update billing status
            billing.payment_status = 'Completed'
            billing.response_description = 'Payment completed successfully'
            billing.customer_message = 'Your payment has been received'
            
            # Create booking
            new_booking = Booking(
                user_id=billing.user_id,
                package_id=billing.package_id,
                booking_date=datetime.utcnow(),
                status='Successful',
                billing_id=billing.id,
                agency_id=Package.query.get(billing.package_id).agency_id
            )
            
            db.session.add(new_booking)
            db.session.commit()
            
        else:  # Failed payment
            billing.payment_status = 'Failed'
            billing.response_description = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultDesc', 'Payment failed')
            billing.customer_message = 'Your payment was not successful'
            db.session.commit()
        
        return jsonify({'message': 'Callback processed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error processing callback', 'error': str(e)}), 500