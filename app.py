from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import random
from flask_mail import Mail, Message
import smtplib

app = Flask(__name__)

# Configure session for OTP storage
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

email_address = 'cloudvaultapp@gmail.com'  # Your email address
email_password = 'dkuj jtof xpnz htpa' 


@app.route("/")
def home_page():
    return render_template('index.html')

@app.route('/signup', methods=["POST", "GET"])
def signup():
    error_message = None

    if request.method == 'POST':

        user_name = request.form.get('uname')
        email_id = request.form.get('emailid')
        password = request.form.get('pass')
        conf_password = request.form.get('confpass')
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')

        session['first_name'] = first_name
        session['last_name'] =  last_name
        session['user_name'] =  user_name
        session['email_id'] =  email_id
        session['password'] = password

        # Check if the username already exists
        conn = psycopg2.connect(
            dbname='signup',
            user='postgres',
            password='Anuj@2000',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()
    

        username_exists_query = "SELECT * FROM details WHERE user_name = %s"
        cur.execute(username_exists_query, (user_name,))
        existing_username = cur.fetchone()

        email_exists_query = "SELECT * FROM details WHERE email = %s"
        cur.execute(email_exists_query, (email_id,))
        existing_email = cur.fetchone()

        cur.close()
        conn.close()

        if existing_username:
            error_message = "This username is already taken. Please try a different one."
        elif existing_email:
            error_message = "This email address is already registered. Please try to login or use a different email."

        # Check if password and confirm password match
        elif password != conf_password:
            error_message = "Passwords do not match. Please correct your password."
        else:
            try:
                # Generate OTP
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

                # Store OTP in session for verification
                session['otp'] = otp

                # Send OTP to the user's email address (you can add this logic)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_address, email_password)
                subject = 'SignUp for Cloud Vault'
                message = f'Your SignUp code for Cloud Vault is: {otp}'
                server.sendmail(email_address, email_id, f'Subject: {subject}\n\n{message}')
                server.quit()

                # Redirect to the OTP verification page
                return redirect(url_for('otp_verification'))

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"

    return render_template("signup.html", error_message=error_message)

@app.route('/otp_verification', methods=["POST", "GET"])
def otp_verification():
    error_message = None

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_otp = session.get('otp')

        if entered_otp == stored_otp:
            try:
                # Insert data into the database after OTP validation
                first_name = session.get('first_name')
                last_name = session.get('last_name')
                user_name = session.get('user_name')
                email_id = session.get('email_id')
                password = session.get('password')

                conn = psycopg2.connect(
                    dbname='signup',
                    user='postgres',
                    password='Anuj@2000',
                    host='localhost',
                    port='5432'
                )
                cur = conn.cursor()
            
                insert_query = """INSERT INTO details(first_name, last_name, user_name, passwd, email) VALUES (%s, %s, %s, %s, %s)"""
                cur.execute(insert_query, (first_name, last_name, user_name, password, email_id))
                conn.commit()
                cur.close()
                conn.close()

                # Clear the OTP from the session
                session.pop('otp', None)
                session.pop('first_name', None)
                session.pop('last_name', None)
                session.pop('user_name', None)
                session.pop('email_id', None)
                session.pop('password', None)

                flash('Signup successful! You can now log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f"An error occurred while signing up: {str(e)}", 'danger')
        else:
            flash('Invalid OTP. Please try again.', 'danger')

    return render_template('otp_verification.html', error_message=error_message)

@app.route('/login', methods=['POST', 'GET'])
def login():
    error_message = None

    if request.method == 'POST':
        email_address_id = request.form.get('email_address')
        password = request.form.get('password')

        conn = psycopg2.connect(
            dbname='signup',
            user='postgres',
            password='Anuj@2000',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()

        # Query to check if the email and password combination exists
        login_query = "SELECT * FROM details WHERE email = %s AND passwd = %s"
        cur.execute(login_query, (email_address_id, password))
        user_data = cur.fetchone()

        if user_data:
            try:
                # Generate OTP
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

                # Store OTP in session for verification
                session['otp'] = otp
                session['username'] = user_data[2]  # Store the username for later use

                # Send OTP to the user's email address (you can add this logic)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_address, email_password)
                subject = 'Login for Cloud Vault'
                message = f'Your Login code for Cloud Vault is: {otp}'
                server.sendmail(email_address, email_address_id, f'Subject: {subject}\n\n{message}')
                server.quit()

                # Redirect to the OTP verification page
                return redirect(url_for('otp_verification_login'))

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
        else:
            error_message = "Invalid email address or password."

    return render_template('login.html', error_message=error_message)

@app.route('/otp_verification_login', methods=["POST", "GET"])
def otp_verification_login():
    error_message = None

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_otp = session.get('otp')

        if entered_otp == stored_otp:
            # OTP validation successful, log in the user
            username = session.get('username')
            # Implement your login logic here, e.g., set a session variable to indicate the user is logged in

            flash('Login successful!', 'success')
            session.pop('otp', None)
            return redirect(url_for('dashboard'))  # Redirect to the dashboard or home page after login
        else:
            error_message = 'Invalid OTP. Please try again.'

    return render_template('otp_verification_login.html', error_message=error_message)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)
