from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from Models import db, User, Agency
import re

auth_bp = Blueprint('auth', __name__)

# validate email and password
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_password(password):
    return len(password) >= 6

# Registering our client
@auth_bp.route('/register/client', methods=['POST'])
def register_client():
    try:
        data = request.get_json()
        
        # make sure user enters all fields
        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        email = data['email'].strip()
        password = data['password'].strip()
        # confirm_password = data['confirm_password'].strip()

        # Validate email and password
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        if not is_valid_password(password):
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        # if password != confirm_password:
        #     return jsonify({"error": "Passwords do not match"}), 400

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        # Create a new client record
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=email,
            phone_number=data['phone_number'],
            gender=data['gender'],
            password=password
        )
        
        # Hash the password
        new_user.set_password(password)

        # Add new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "Registration successful",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "phone_number": new_user.phone_number,
                "gender": new_user.gender
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Agency Register
@auth_bp.route('/register/agency', methods=['POST'])
def register_agency():
    try:
        data = request.get_json()
        
        # make sure user enters all fields
        required_fields = ['agency_name', 'agency_email', 'agency_phone_number', 'description', 'agency_password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        agency_email = data['agency_email'].strip()
        agency_password = data['agency_password'].strip()
        # confirm_password = data['confirm_password'].strip()

        # Validate email and password
        if not is_valid_email(agency_email):
            return jsonify({"error": "Invalid email format"}), 400
        if not is_valid_password(agency_password):
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        # Check if email already exists
        if Agency.query.filter_by(agency_email=agency_email).first():
            return jsonify({"error": "Email already registered"}), 400

        # Create a new client record
        new_agency = Agency(
            agency_name=data['agency_name'],
            agency_email=agency_email,
            agency_phone_number=data['agency_phone_number'],
            description=data['description'],
            agency_password=agency_password
        )
        
        # Hash the password
        new_agency.set_password(agency_password)

        # Add new user to the database
        db.session.add(new_agency)
        db.session.commit()

        return jsonify({
            "message": "Agency Registration successful",
            "user": {
                "id": new_agency.id,
                "agency_email": new_agency.agency_email,
                "agency_name": new_agency.agency_name,
                "agency_phone_number": new_agency.agency_phone_number,
                "description": new_agency.description,
                "agency_password": new_agency.agency_password
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Client Login Route
@auth_bp.route('/login/client', methods=['POST'])
def client_login():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        # Fetch the client from the database
        client = User.query.filter_by(email=email).first()

        # return error if the client is not found or password does not match
        if not client or not client.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create access token
        access_token = create_access_token(identity=client.id, expires_delta=timedelta(days=3))

        # Return successful login response
        return jsonify({
            'message': 'Client Login successful!',
            'access_token': access_token,
            'user': {
                "id": client.id,
                "email": client.email,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "phone_number": client.phone_number,
                "gender": client.gender
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Agency Login Route
@auth_bp.route('/login/agency', methods=['POST'])
def agency_login():
    try:
        data = request.get_json()

        agency_email = data.get('agency_email')
        agency_password = data.get('agency_password')

        # Fetch the agency from the database
        agency = Agency.query.filter_by(agency_email=agency_email).first()

        # return error if the agency is not found or password does not match, 
        if not agency or not agency.check_password(agency_password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create access token
        access_token = create_access_token(identity=agency.id, expires_delta=timedelta(days=3))

        # Return successful login response
        return jsonify({
            'message': 'Agency Login successful!',
            'access_token': access_token,
            'agency': {
                "id": agency.id,
                "agency_name": agency.agency_name,
                "agency_email": agency.agency_email,
                "agency_phone_number": agency.agency_phone_number
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Protected route
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    
    # Check if the current user is a client or an agency
    user = User.query.get(current_user_id) or Agency.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "id": user.id,
        "email": user.email if isinstance(user, User) else user.agency_email,
        "first_name": user.first_name if isinstance(user, User) else None,
        "last_name": user.last_name if isinstance(user, User) else None,
        "phone_number": user.phone_number if isinstance(user, User) else user.agency_phone_number,
        "user_type": "client" if isinstance(user, User) else "agency"
    }

    if isinstance(user, Agency):
        user_data["agency_name"] = user.agency_name

    return jsonify(user_data), 200
