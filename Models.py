from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from Config.config import db

class Package(db.Model):
    __tablename__ = 'package'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    package_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String, nullable=False)
    day_count = db.Column(db.Integer, nullable=False)
    package_type = db.Column(db.String, nullable=False)
    inclusions = db.Column(db.Text, nullable=False)
    exclusions = db.Column(db.Text, nullable=False)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=False)

    # Relationships
    agency = db.relationship('Agency', back_populates='packages', lazy=True)
    bookings = db.relationship('Booking', back_populates='package', lazy=True)
    reviews = db.relationship('Review', back_populates='package', lazy=True)
    photos = db.relationship('Photo', back_populates='package', lazy=True)
    
    # return as json
    def to_json(self):
        return {
            'id': self.id,
            'package_name': self.package_name,
            'price': self.price,
            'location': self.location,
            'day_count': self.day_count,
            'package_type': self.package_type,
            'inclusions': self.inclusions,
            'exclusions': self.exclusions,
            'agency_id': self.agency_id,
            'agency': self.agency.to_json(),
            'bookings': [booking.to_json() for booking in self.bookings],
           'reviews': [review.to_json() for review in self.reviews],
            'photos': [photo.to_json() for photo in self.photos]
        }

class Agency(db.Model):
    __tablename__ = 'agency'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agency_name = db.Column(db.String, nullable=False)
    agency_email = db.Column(db.String, unique=True, nullable=False)
    agency_phone_number = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    agency_password = db.Column(db.String, nullable=False)

    # Relationship with Package
    packages = db.relationship('Package', back_populates='agency', lazy=True)

    def set_password(self, password):
        self.agency_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.agency_password, password)
    
    # return as json
    def to_json(self):
        return {
            'id': self.id,
            'agency_name': self.agency_name,
            'agency_email': self.agency_email,
            'agency_phone_number': self.agency_phone_number,
            'description': self.description,
            'packages': [package.to_json() for package in self.packages],
            'agency_password': self.agency_password
        }

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    amount = db.Column(db.Float, nullable=True)
    billing_id = db.Column(db.Integer, db.ForeignKey('billings.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='bookings', lazy=True)
    package = db.relationship('Package', back_populates='bookings', lazy=True)
    billing = db.relationship('Billing', back_populates='bookings', lazy=True, foreign_keys=[billing_id])
    
    # return as json
    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'package_id': self.package_id,
            'amount': self.amount,
            'billing_id': self.billing_id,
            'package': self.package.to_json(),
            'billing': self.billing.to_json()
        }

class Billing(db.Model):
    __tablename__ = 'billings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    checkoutID = db.Column(db.BigInteger, nullable=True)
    phone_number = db.Column(db.String, nullable=False)
    response_description = db.Column(db.Text, nullable=True)
    customer_message = db.Column(db.Text, nullable=True)
    payment_status = db.Column(db.String, nullable=False)

    # Relationship with Booking
    bookings = db.relationship('Booking', back_populates='billing', lazy=True, foreign_keys='Booking.billing_id')
    
    # return as data
    def to_json(self):
        return {
            'id': self.id,
            'checkoutID': self.checkoutID,
            'phone_number': self.phone_number,
           'response_description': self.response_description,
            'customer_message': self.customer_message,
            'payment_status': self.payment_status,
            'bookings': [booking.to_json() for booking in self.bookings]
        }

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String, nullable=False)

    # Relationship with Booking
    bookings = db.relationship('Booking', back_populates='user', lazy=True)
    reviews = db.relationship('Review', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # return data as json
    def to_json(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'gender': self.gender,
            'image_url': self.image_url,
            "password":self.password
        }
    
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    image = db.Column(db.String, nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    review_texts = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='reviews', lazy=True)
    package = db.relationship('Package', back_populates='reviews', lazy=True)
    
    # return data as json
    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'package_id': self.package_id,
            'image': self.image,
            'rating': self.rating,
           'review_texts': self.review_texts,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S')
        }

class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    photo_url = db.Column(db.String, nullable=False)

    package = db.relationship('Package', back_populates='photos', lazy=True)
    
    # return data as json
    def to_json(self):
        return {
            'id': self.id,
            'package_id': self.package_id,
            'photo_url': self.photo_url
        }
