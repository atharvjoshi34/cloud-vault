from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import random
from flask_mail import Mail, Message
import smtplib
from google.cloud import secretmanager
from google.cloud import storage
from flask import send_file
from io import BytesIO

app = Flask(__name__)

# Configure session for OTP storage
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
client = secretmanager.SecretManagerServiceClient()

project_id = "steel-ace-399104"

#accessing the secret payload from secret manager
email_password_response = client.access_secret_version(request={"name": f"projects/{project_id}/secrets/emailer-password/versions/latest"})
db_password_response = client.access_secret_version(request={"name": f"projects/{project_id}/secrets/db-password/versions/latest"})
email_address_response= client.access_secret_version(request={"name": f"projects/{project_id}/secrets/emailer-address/versions/latest"})
db_user_response = client.access_secret_version(request={"name": f"projects/{project_id}/secrets/db-user-name/versions/latest"})
db_ip_response = client.access_secret_version(request={"name": f"projects/{project_id}/secrets/db-instance-ip/versions/latest"})

#decoding the payload of access manager
email_address = email_address_response.payload.data.decode("UTF-8") 
email_password = email_password_response.payload.data.decode("UTF-8") 
db_password = db_password_response.payload.data.decode("UTF-8")
db_user = db_user_response.payload.data.decode("UTF-8")
db_ip = db_ip_response.payload.data.decode("UTF-8")


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

        # using the session functionality which can help you store stuff and user in other routes
        session['first_name'] = first_name
        session['last_name'] =  last_name
        session['user_name'] =  user_name
        session['email_id'] =  email_id
        session['password'] = password

        # making the database connection -> to secure it gcp secret manager is used
        conn = psycopg2.connect(
            dbname='signup',
            user= db_user,
            password= db_password,
            host= db_ip,
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
                server.login(email_address, email_password) #to keep the email address password cofidential again secret manager is used
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
                     user= db_user,
                     password= db_password,
                     host=db_ip,
                     port='5432'
                )
                cur = conn.cursor()
            
                insert_query = """INSERT INTO details(first_name, last_name, user_name, passwd, email) VALUES (%s, %s, %s, %s, %s)"""
                cur.execute(insert_query, (first_name, last_name, user_name, password, email_id))

                user_bucket = create_user_bucket(user_name)
                # Grant Storage Object Admin role to the user
                grant_object_admin_role(user_bucket, email_id)

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
                return redirect(url_for('login')) #redirect url takes you the functon mentioned
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
            user=db_user,
            password= db_password,
            host= db_ip,
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
                session['username'] = user_data[3]  # Store the username for later use

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
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session.get('username')
    user_bucket = get_user_bucket(username)
    
    if user_bucket:
        # Fetch the list of files and their details
        blobs = list(user_bucket.list_blobs())
        file_list = []
        for blob in blobs:
            file_info = {
                'name': blob.name,
                'size': blob.size,
                'created': blob.time_created.strftime('%Y-%m-%d %H:%M:%S')
            }
            file_list.append(file_info)
    else:
        file_list = []

    return render_template('dashboard.html', username=username, file_list=file_list)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session.get('username')
    uploaded_file = request.files['file']

    if uploaded_file.filename != '':
        try:
            # Authenticate the user and retrieve their bucket
            user_bucket = get_user_bucket(username)
            if user_bucket is None:
                return "User's bucket not found. Please contact support."

            # Upload the file to the user's bucket
            blob = user_bucket.blob(uploaded_file.filename)
            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.content_type
            )

            return redirect(url_for('dashboard'))
        except Exception as e:
            # Log the error for debugging
            print(f'An error occurred during file upload: {str(e)}')
            return f'An error occurred: {str(e)}'
    else:
        return 'No file selected.'
    
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Retrieve the user's bucket
    username = session.get('username')
    user_bucket = get_user_bucket(username)

    if user_bucket:
        blob = user_bucket.blob(filename)
        if blob.exists():
            # Read the file data into a BytesIO object
            file_data = blob.download_as_bytes()
            
            # Create a BytesIO object to wrap the file data
            file_stream = BytesIO(file_data)

            # Send the file for download as an attachment
            return send_file(file_stream, as_attachment=True, download_name=filename)
        else:
            flash('File not found.', 'danger')
    else:
        flash("User's bucket not found. Please contact support.", 'danger')

    return redirect(url_for('dashboard'))

@app.route('/delete/<filename>', methods=['GET'])
def delete_file(filename):
    # Retrieve the user's bucket
    username = session.get('username')
    user_bucket = get_user_bucket(username)

    if user_bucket:
        blob = user_bucket.blob(filename)
        if blob.exists():
            blob.delete()
            flash(f'File "{filename}" deleted successfully!', 'success')
        else:
            flash('File not found.', 'danger')
    else:
        flash("User's bucket not found. Please contact support.", 'danger')

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    # Clear the user session
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home_page'))

def get_user_bucket(username):
    # Check if the user's bucket exists
    storage_client = storage.Client()
    bucket_name = f"cloud-vault-{username}"
    user_bucket = storage_client.get_bucket(bucket_name)
    if not user_bucket.exists():
        return None
    return user_bucket


# Utility Functions
def create_user_bucket(username):
    storage_client = storage.Client()
    bucket_name = f"cloud-vault-{username}"  # Unique bucket name
    bucket = storage_client.create_bucket(bucket_name)
    return bucket

def grant_object_admin_role(bucket, email):
    # Grant the Storage Object Admin role to the user
    policy = bucket.get_iam_policy(requested_policy_version=3)
    policy.bindings.append(
        {"role": "roles/storage.objectAdmin", "members": [f"user:{email}"]}
    )
    bucket.set_iam_policy(policy)


if __name__ == "__main__":
    app.run(debug=False)
