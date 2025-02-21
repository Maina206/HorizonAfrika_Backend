from Config.config import create_app
from flask_jwt_extended import JWTManager

app = create_app()

jwt = JWTManager(app)



if __name__ == '__main__':
    app.run(debug=True)