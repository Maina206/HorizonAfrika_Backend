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
    agency = db.relationship('Agency', back_populates='packages')
    bookings = db.relationship('Booking', back_populates='package')
    reviews = db.relationship('Review', back_populates='package')
    photos = db.relationship('Photo', back_populates='package')
    billings = db.relationship('Billing', back_populates='package')

    # Return as JSON
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
            'agency': {
                'id': self.agency.id,
                'agency_name': self.agency.agency_name,
                'agency_email': self.agency.agency_email,
                'agency_phone_number': self.agency.agency_phone_number,
                'description': self.agency.description,
            } if self.agency else None,
            'bookings': [{
            'id': booking.id,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': booking.status
        } for booking in self.bookings] if self.bookings else [],
        'reviews': [{
            'id': review.id,
            'rating': review.rating,
            'review_texts': review.review_texts,
            'date': review.date.strftime('%Y-%m-%d %H:%M:%S')
        } for review in self.reviews] if self.reviews else [],
        'photos': [{
            'id': photo.id,
            'photo_url': photo.photo_url
        } for photo in self.photos] if self.photos else []
    }

class Agency(db.Model):
    __tablename__ = 'agency'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agency_name = db.Column(db.String, nullable=False)
    agency_email = db.Column(db.String, unique=True, nullable=False)
    agency_phone_number = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    agency_password = db.Column(db.String, nullable=False)

    # Relationships
    packages = db.relationship('Package', back_populates='agency', lazy=True)
    bookings = db.relationship('Booking', back_populates='agency', lazy=True)

    def set_password(self, password):
        self.agency_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.agency_password, password)

    # Return as JSON
    def to_json(self):
        return {
        'id': self.id,
        'agency_name': self.agency_name,
        'agency_email': self.agency_email,
        'agency_phone_number': self.agency_phone_number,
        'description': self.description,
        'packages': [{
            'id': package.id,
            'package_name': package.package_name,
            'price': package.price,
            'location': package.location,
            'day_count': package.day_count
        } for package in self.packages] if self.packages else [],
        'bookings': [{
            'id': booking.id,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': booking.status
        } for booking in self.bookings] if self.bookings else []
    }


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=True)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String, nullable=False, default='Pending')
    billing_id = db.Column(db.Integer, db.ForeignKey('billings.id'), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='bookings')
    package = db.relationship('Package', back_populates='bookings')
    billing = db.relationship('Billing', back_populates='booking', uselist=False)
    agency = db.relationship('Agency', back_populates='bookings')

    # Return as JSON
    def to_json(self):
        return {
        'id': self.id,
        'user_id': self.user_id,
        'package_id': self.package_id,
        'agency_id': self.agency_id,
        'booking_date': self.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
        'status': self.status,
        'billing_id': self.billing_id,
        'package': {
            'id': self.package.id,
            'name': self.package.name
        } if self.package else None,
        'billing': {
            'id': self.billing.id,
            'amount': self.billing.amount
        } if self.billing else None,
        'agency': {
            'id': self.agency.id,
            'name': self.agency.name
        } if self.agency else None
    }


class Billing(db.Model):
    __tablename__ = 'billings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    checkoutID = db.Column(db.BigInteger, nullable=True)
    phone_number = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=True)
    response_description = db.Column(db.Text, nullable=True)
    customer_message = db.Column(db.Text, nullable=True)
    payment_status = db.Column(db.String, nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    package = db.relationship('Package', back_populates='billings')
    user = db.relationship('User', back_populates='billings')
    booking = db.relationship('Booking', back_populates='billing', uselist=False)

    # Return as JSON
def to_json(self):
    return {
        'id': self.id,
        'checkoutID': self.checkoutID,
        'phone_number': self.phone_number,
        'amount': self.amount,
        'response_description': self.response_description,
        'customer_message': self.customer_message,
        'payment_status': self.payment_status,
        'package_id': self.package_id,
        'user_id': self.user_id,
        'booking': {
            'id': self.booking.id,
            'booking_date': self.booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.booking.status
        } if self.booking else None
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

    # Relationships
    bookings = db.relationship('Booking', back_populates='user', lazy=True)
    reviews = db.relationship('Review', back_populates='user', lazy=True)
    billings = db.relationship('Billing', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Return as JSON
    def to_json(self):
        return {
        'id': self.id,
        'first_name': self.first_name,
        'last_name': self.last_name,
        'email': self.email,
        'phone_number': self.phone_number,
        'gender': self.gender,
        'image_url': self.image_url,
        'bookings': [{
            'id': booking.id,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': booking.status
        } for booking in self.bookings] if self.bookings else [],
        'reviews': [{
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment
        } for review in self.reviews] if self.reviews else [],
        'billings': [{
            'id': billing.id,
            'amount': billing.amount,
            'payment_status': billing.payment_status
        } for billing in self.billings] if self.billings else []
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
    user = db.relationship('User', back_populates='reviews')
    package = db.relationship('Package', back_populates='reviews')

    # Return as JSON
    def to_json(self):
        return {
        'id': self.id,
        'user_id': self.user_id,
        'package_id': self.package_id,
        'image': self.image,
        'rating': self.rating,
        'review_texts': self.review_texts,
        'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
        'user': {
            'id': self.user.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email
        } if self.user else None,
        'package': {
            'id': self.package.id,
            'name': self.package.name,
            'price': self.package.price
        } if self.package else None
    }


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    photo_url = db.Column(db.String, nullable=False)

    package = db.relationship('Package', back_populates='photos')

    # Return as JSON
    def to_json(self):
        return {
        'id': self.id,
        'package_id': self.package_id,
        'photo_url': self.photo_url,
        'package': {
            'id': self.package.id,
            'name': self.package.name,
            'price': self.package.price
        } if self.package else None
    }
