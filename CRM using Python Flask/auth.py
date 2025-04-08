from flask import Flask, session, redirect, request, url_for, make_response

app = Flask(__name__)
app.secret_key = 'your-secret-key' 

@app.before_request
def check_authentication():
    allowed_routes = ['login']  
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect(url_for('login'))

    if 'user' in session and 'user_session' not in request.cookies:
        resp = make_response()
        resp.set_cookie('user_session', session.sid, max_age=3600)
        return resp

@app.route('/login')
def login():
    return "Login Page"

@app.route('/dashboard')
def dashboard():
    return "Welcome to dashboard!"
