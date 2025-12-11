from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo 
from datetime import datetime
from bson.objectid import ObjectId 
from flask_cors import CORS 
import qrcode 
import base64 
from io import BytesIO  
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MONGO_URI'] = "mongodb://localhost:27017/kisanmarket"  # MongoDB Database

mongo = PyMongo(app)
CORS(app, supports_credentials=True)



# ------------------- SIGNUP -------------------
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([name, email, password, confirm_password]):
        return jsonify({"error": "Missing fields"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Check existing user
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    mongo.db.users.insert_one({
        "name": name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "created_at": datetime.utcnow()
    })

    return jsonify({"message": "User registered successfully"}), 201


# ------------------- LOGIN -------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Missing fields"}), 400

    user = mongo.db.users.find_one({"email": email})

    if user and check_password_hash(user["password_hash"], password):
        session['user_id'] = str(user["_id"])
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


# ------------------- LOGOUT -------------------
# @app.route('/api/logout', methods=['POST'])
# def logout():
#     session.pop('user_id', None)
#     return jsonify({"message": "Logged out"}), 200


# ------------------- CREATE FARMER PASS -------------------
@app.route('/api/farmerpass', methods=['POST'])
def create_farmer_pass():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    try:
        farmer_pass = {
            "user_id": session['user_id'],
            "village": data["village"],
            "crop": data["crop"],
            "season": data["season"],
            "area": float(data["area"]),
            "valid_till": datetime.strptime(data["valid_till"], '%Y-%m-%d'),
            "custom_id": data.get("custom_id"),
            "qr_text": data["qr_text"],
            "created_at": datetime.utcnow()
        }
    except:
        return jsonify({"error": "Invalid or missing fields"}), 400

    result = mongo.db.farmer_pass.insert_one(farmer_pass)

    return jsonify({"message": "Farmer pass created", "id": str(result.inserted_id)}), 201


# ------------------- GET FARMER PASS -------------------
# @app.route('/api/farmerpass/<string:pass_id>', methods=['GET'])
# def get_farmer_pass(pass_id):
    
#     if 'user_id' not in session:
#         return jsonify({"error":"Unauthorized"}), 401

#     fp = mongo.db.farmer_pass.find_one({"_id": ObjectId(pass_id)})

#     if not fp or fp["user_id"] != session["user_id"]:
#         return jsonify({"error": "Unauthorized & Not Found"}), 404

#     return jsonify({
#         "id": str(fp["_id"]),
#         "village": fp["village"],
#         "crop": fp["crop"],
#         "season": fp["season"],
#         "area": fp["area"],
#         "valid_till": fp["valid_till"].strftime('%Y-%m-%d'),
#         "custom_id": fp.get("custom_id"),
#         "qr_text": fp["qr_text"]
#     })

@app.route('/api/farmerpass', methods=['POST'])
def create_pass():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.json
    qr_data = data["qr_text"]

    # QR Generate
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    farmer = {
        "user_id": session["user_id"],
        "village": data["village"],
        "crop": data["crop"],
        "season": data["season"],
        "area": float(data["area"]),
        "valid_till": datetime.strptime(data["valid_till"], "%Y-%m-%d"),
        "custom_id": data.get("custom_id"),
        "qr_image": qr_base64,
        "qr_text": data["qr_text"],
        "created_at": datetime.utcnow()
    }

    mongo.db.farmer_pass.insert_one(farmer)

    return jsonify({
        "message": "Farmer Pass Created Successfully",
        "qr_image": qr_base64
    }), 201


# ------------------- CONTACT FORM -------------------
@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json

    if not all([data.get('name'), data.get('email'), data.get('message')]):
        return jsonify({"error": "Missing fields"}), 400

    mongo.db.contact_messages.insert_one({
        "name": data["name"],
        "email": data["email"],
        "message": data["message"],
        "created_at": datetime.utcnow()
    })

    return jsonify({"message": "Message received. We will reply within 24 hours."}), 201


# ------------------- PRODUCT LIST (STATIC) -------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    products = [
        {"name": "Wheat", "description": "Grade A • 50kg bags", "price": 2150},
        {"name": "Tomato", "description": "Fresh • Crate", "price": 1200},
        {"name": "Potato", "description": "Washed • Sack", "price": 1000},
        {"name": "Rice", "description": "Polished • 25kg bags", "price": 2400},
        {"name": "Onion", "description": "Red • 50kg bag", "price": 1500},
        {"name": "Spinach", "description": "Fresh • 5kg bundle", "price": 2200},
    ]
    return jsonify(products)


# ------------------- RUN SERVER -------------------
if __name__ == "__main__":
    app.run(debug=True , port=5000)


# from flask import Flask, request, jsonify, session
# from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_cors import CORS
# from datetime import datetime

# app = Flask(__name__)

# # Secret Key for session handling
# app.config['SECRET_KEY'] = "MY_SECRET_KEY"

# # Your MongoDB connection
# app.config['MONGO_URI'] = "mongodb://localhost:27017/kisanmarket"

# mongo = PyMongo(app)

# # Allow frontend to access backend
# CORS(app, supports_credentials=True)


# # ------------------- SIGNUP API -------------------
# @app.route('/api/signup', methods=['POST'])
# def signup():
#     data = request.json
#     name = data.get("name")
#     email = data.get("email")
#     password = data.get("password")
#     confirm_password = data.get("confirm_password")

#     if not all([name, email, password, confirm_password]):
#         return jsonify({"error": "All fields required"}), 400

#     if password != confirm_password:
#         return jsonify({"error": "Passwords do not match"}), 400

#     if mongo.db.users.find_one({"email": email}):
#         return jsonify({"error": "Email already exists"}), 400

#     hashed_pass = generate_password_hash(password)

#     mongo.db.users.insert_one({
#         "name": name,
#         "email": email,
#         "password_hash": hashed_pass,
#         "created_at": datetime.utcnow()
#     })

#     return jsonify({"message": "Signup successful"}), 201


# # ------------------- LOGIN API -------------------
# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     if not all([email, password]):
#         return jsonify({"error": "Missing email or password"}), 400

#     user = mongo.db.users.find_one({"email": email})

#     if user and check_password_hash(user["password_hash"], password):
#         session['user_id'] = str(user["_id"])
#         return jsonify({"message": "Login successful"}), 200

#     return jsonify({"error": "Invalid credentials"}), 401


# # ------------------- SERVER RUN -------------------
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
