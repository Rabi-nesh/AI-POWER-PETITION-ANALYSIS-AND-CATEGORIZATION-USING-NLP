from flask_jwt_extended import create_access_token

def generate_token(user_id):
    # Convert user_id to string
    return create_access_token(identity=str(user_id))