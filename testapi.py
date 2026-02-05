from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory storage for users
users = []

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    phone = data.get('phone')
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({"error": "Phone and password are required"}), 400
    
    # Check if user already exists
    for user in users:
        if user['phone'] == phone:
            return jsonify({"error": "User already exists"}), 409
    
    # Add user
    new_user = {
        "phone": phone,
        "password": password
    }
    users.append(new_user)
    
    print(f"New user registered: {phone}")
    return jsonify(new_user), 201

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

if __name__ == '__main__':
    print("Starting test API server on http://localhost:5000")
    app.run(debug=True, port=5000)