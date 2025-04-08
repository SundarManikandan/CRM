from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
import pyodbc
from db_config import get_connection_string

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# ------------------- Authentication -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = pyodbc.connect(get_connection_string())
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()

            if user:
                session['user'] = username
                resp = make_response(redirect(url_for('customer_page')))
                resp.set_cookie('user_session', session.sid, max_age=3600)
                return resp
            else:
                error = 'Invalid username or password.'
        except Exception as e:
            error = f"Database error: {str(e)}"

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('user_session', '', expires=0)
    return resp

@app.before_request
def check_login():
    if request.endpoint not in ('login', 'static') and 'user' not in session:
        return redirect(url_for('login'))

# ------------------- Routes -------------------
@app.route('/')
def customer_page():
    return render_template('customers.html')

@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/save_user', methods=['POST'])
def save_user():
    try:
        data = request.form
        required_fields = ['name', 'mobile', 'email']
        if not all(data.get(f) for f in required_fields):
            return jsonify({"errorMsg": "Name, Mobile, and Email are required."})

        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clients (name, mobile, email, gstin, address, pincode, contact_person, company, state, country, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data['name'], data['mobile'], data['email'], data.get('gstin', ''), data.get('address', ''),
            data.get('pincode', ''), data.get('contact_person', ''), data.get('company', ''),
            data.get('state', ''), data.get('country', ''), data.get('status', ''))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'errorMsg': str(e)})

@app.route('/update_user', methods=['POST'])
def update_user():
    try:
        data = request.form
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers SET name=?, mobile=?, email=?, gstin=?, address=?, pincode=?, contact_person=?, company=?, state=?, country=?, status=?
            WHERE id=?""",
            data['name'], data['mobile'], data['email'], data['gstin'], data['address'],
            data['pincode'], data['contact_person'], data['company'], data['state'], data['country'], data['status'], data['id'])
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'errorMsg': str(e)})

@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        user_id = request.form['id']
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id=?", user_id)
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'errorMsg': str(e)})

@app.route('/get_clients_paginated', methods=['GET'])
def get_clients_paginated():
    try:
        page = int(request.args.get('page', 1))
        rows_per_page = int(request.args.get('rows', 10))
        offset = (page - 1) * rows_per_page

        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        total = cursor.fetchone()[0]

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
            "total": total,
            "rows": rows
        })
    except Exception as e:
        return jsonify({
            "total": 0,
            "rows": [],
            "errorMsg": f"Database error: {str(e)}"
        })

if __name__ == '__main__':
    app.run(debug=True)
