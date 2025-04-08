from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pyodbc
from db_config import get_connection_string
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')
JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt_dev_secret')

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

# ------------------- Authentication -------------------
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Missing username or password'}), 400
            
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        if user:
            # Generate JWT token
            token = jwt.encode({
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, JWT_SECRET, algorithm="HS256")
            
            return jsonify({
                'success': True, 
                'token': token,
                'username': username
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error: {str(e)}"}), 500

# ------------------- Customer Routes -------------------
@app.route('/api/customers', methods=['GET'])
@token_required
def get_customers(current_user):
    try:
        page = int(request.args.get('page', 1))
        rows_per_page = int(request.args.get('rows', 10))
        offset = (page - 1) * rows_per_page
        
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM customers")
        total = cursor.fetchone()[0]
        
        # Get paginated data
        query = """
            SELECT * FROM customers
            ORDER BY id
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """
        cursor.execute(query, (offset, rows_per_page))
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return jsonify({
            "success": True,
            "total": total,
            "customers": rows
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Database error: {str(e)}"
        }), 500

@app.route('/api/customers', methods=['POST'])
@token_required
def create_customer(current_user):
    try:
        data = request.get_json()
        required_fields = ['name', 'mobile', 'email']
        
        if not all(data.get(f) for f in required_fields):
            return jsonify({"success": False, "message": "Name, Mobile, and Email are required."}), 400
        
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (name, mobile, email, gstin, address, pincode, contact_person, company, state, country, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data['name'], data['mobile'], data['email'], 
            data.get('gstin', ''), data.get('address', ''),
            data.get('pincode', ''), data.get('contact_person', ''), 
            data.get('company', ''), data.get('state', ''), 
            data.get('country', ''), data.get('status', 'Active'))
        conn.commit()
        
        # Get the ID of the newly inserted customer
        cursor.execute("SELECT @@IDENTITY")
        customer_id = cursor.fetchone()[0]
        
        return jsonify({'success': True, 'id': customer_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(current_user, customer_id):
    try:
        data = request.get_json()
        required_fields = ['name', 'mobile', 'email']
        
        if not all(data.get(f) for f in required_fields):
            return jsonify({"success": False, "message": "Name, Mobile, and Email are required."}), 400
        
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers SET name=?, mobile=?, email=?, gstin=?, address=?, pincode=?, 
            contact_person=?, company=?, state=?, country=?, status=?
            WHERE id=?""",
            data['name'], data['mobile'], data['email'], 
            data.get('gstin', ''), data.get('address', ''),
            data.get('pincode', ''), data.get('contact_person', ''), 
            data.get('company', ''), data.get('state', ''), 
            data.get('country', ''), data.get('status', 'Active'),
            customer_id)
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(current_user, customer_id):
    try:
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id=?", customer_id)
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clients', methods=['GET'])
@token_required
def get_clients(current_user):
    try:
        page = int(request.args.get('page', 1))
        rows_per_page = int(request.args.get('rows', 10))
        offset = (page - 1) * rows_per_page
        
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM clients")
        total = cursor.fetchone()[0]
        
        # Get paginated data
        query = """
            SELECT * FROM clients
            ORDER BY id
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """
        cursor.execute(query, (offset, rows_per_page))
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return jsonify({
            "success": True,
            "total": total,
            "clients": rows
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Database error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)