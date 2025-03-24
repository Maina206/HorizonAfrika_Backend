from Config.config import create_app
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()  # This will load environment variables from .env file


app = create_app()

jwt = JWTManager(app)

# Blueprints
from auth import auth_bp;
app.register_blueprint(auth_bp)

from routes import routes_bp
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    app.run(debug=True)