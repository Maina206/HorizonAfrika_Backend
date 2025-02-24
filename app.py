from Config.config import create_app
from flask_jwt_extended import JWTManager

app = create_app()

jwt = JWTManager(app)

# Blueprints
from auth import auth_bp;
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)