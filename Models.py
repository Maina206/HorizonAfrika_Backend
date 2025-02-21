from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from Config.config import db




class Package(db.Model):
    __tablename__ = 'package'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    package_name = db.Column(db.String, nullable=False) 
    photos = db.Column(db.String, nullable=False)  
    price = db.Column(db.Float, nullable=False)  
    location = db.Column(db.String, nullable=False)
    day_count = db.Column(db.Integer, nullable=False)
    package_type = db.Column(db.String, nullable=False)
    inclusions = db.Column(db.Text, nullable=False)
    exclusions = db.Column(db.Text, nullable=False)  
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=False)

class Agency(db.Model):
    __tablename__ = 'agency'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agency_name = db.Column(db.String, nullable=False)
    agency_email = db.Column(db.String, unique=True, nullable=False)
    agency_phone_number = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    agency_password = db.Column(db.String, nullable=False)  

    # Relationship with Package
    packages = db.relationship('Package', backref='agency', lazy=True)

    def set_password(self, password):
        self.agency_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.agency_password, password)


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    amount = db.Column(db.Float, nullable=True)  
    billing_id = db.Column(db.Integer, db.ForeignKey('billing.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref='bookings', lazy=True)
    package = db.relationship('Package', backref='bookings', lazy=True)
    billing = db.relationship('Billing', backref='bookings', lazy=True)

class Billing(db.Model):
    __tablename__ = 'billings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    checkoutID = db.Column(db.BigInteger, nullable=True) 
    phone_number = db.Column(db.String, nullable=False)  
    response_description = db.Column(db.Text, nullable=True)  
    customer_message = db.Column(db.Text, nullable=True)  

    # Relationship with Booking
    bookings = db.relationship('Booking', backref='billing', lazy=True)

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
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    image = db.Column(db.String, nullable=True)
    rating = db.Column(db.Integer, nullable=False)  
    review_texts = db.Column(db.Text, nullable=False)  
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  

    # # Relationships
    user = db.relationship('User', backref='reviews', lazy=True)
    package = db.relationship('Package', backref='reviews', lazy=True)
