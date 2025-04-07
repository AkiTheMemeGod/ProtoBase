from flask import *
from flask_cors import CORS
from Database import ProtoBaseAuthentication, DevDashboard, ApiToken, ProtoBaseWebhooks
from schemas import openapi_schema
import sqlite3 as sq
import platform as p
from paths import *
import base64
from discord import *

# push to github
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)
from datetime import timedelta

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "k3h45k3hb6k4hb6k3b6k4bkj3523jbkralkfsldfs"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.secret_key = "#$TL#$T#4MH3l3h4o8jkwbfdo8ho8234jbsdf"

if p.system() == 'Linux':
    path = linux
else:
    path = windows
print(f"Starting Up in {p.system()} taking database path as : {path}")
CORS(app)


def get_db():
    if "db" not in g:
        g.db = sq.connect(path)
    return g.db


@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')


"""
__________________________
APP DEFAULT ROUTES
__________________________
"""


@app.before_request
def make_session_permanent():
    session.permanent = False


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route('/')
def homepage():
    # downloads = pub_dev_downloads()
    return render_template("index.html")


@app.route('/get-started')
def get_started():
    if not session.get("user_signed_in"):
        return render_template("get-started.html")
    return redirect(url_for("dashboard"))


jwt = JWTManager(app)


@app.route('/auth_api/login/', methods=['POST'])
def login():
    """
    Login route for authenticating the users with JWT tokens.
    """
    data = request.json
    usr = data.get('usr')
    pwd = data.get('pwd')
    email = data.get('email', None)
    token = data.get('token')
    print(usr, pwd, email)

    if not usr or not pwd or not token:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})

    con = get_db()
    db = ProtoBaseAuthentication(con)

    if email:
        status, code = db.signin_with_email(usr, pwd, email, token)
    else:
        status, code = db.signin_with_username(usr, pwd, token)

    if status and code == 200:
        access_token = create_access_token(identity=usr)
        refresh_token = create_refresh_token(identity=usr)
        return jsonify({
            "message": "Login successful",
            "status-code": 200,
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    elif code == 400:
        return jsonify({"message": "User not found or invalid credentials", "status-code": 400})
    elif code == 500:
        return jsonify({"message": "Invalid API token", "status-code": 500})
    else:
        return jsonify({"message": "Incorrect credentials", "status-code": 400})


@app.route('/auth_api/refresh/', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh the access token using a valid refresh token.
    """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({
        "message": "Token refreshed",
        "access_token": new_access_token
    })


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"logged_in_as": current_user})


"""
__________________________
DOCUMENTATION ROUTES
__________________________
"""


@app.route('/openapi.json')
def openapi():
    """Serve the OpenAPI schema."""
    return jsonify(openapi_schema)


@app.route('/docs')
def swagger_ui():
    """Serve the Swagger UI."""
    return render_template('swagger.html')


"""
__________________________
DEV AUTHENTICATION ROUTES
__________________________
"""


@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")

    con = get_db()
    db = DevDashboard(con)

    if not db.duplicate_email_check(email) and not db.duplicate_username_check(username, "dev_api_tokens"):
        success, session['c_otp'] = db.auth.send_otp(email=email, username=username)

        if success:
            return jsonify(success=True)
        else:
            return jsonify(success=False, message="Failed to send OTP. Please try again.")
    else:
        return jsonify(success=False, message="Email or Username already exists.")


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    otp = data.get("otp")

    con = get_db()
    db = ProtoBaseAuthentication(con)

    status = db.signup_developer(username, password, email, otp, session.get('c_otp'))
    if status:
        session["user_signed_in"] = True
        session["username"] = username
        session.pop('c_otp', None)
        send_discord_notification(username,email)
        return jsonify(success=True)

    else:
        return jsonify(success=False, message="Signup failed. User may already exist.")


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    con = get_db()
    db = DevDashboard(con)
    email = db.get_email(username)
    result = db.validate_developer(username, password, email)
    if result:
        session["user_signed_in"] = True
        session["username"] = username
        # session["token"] = db.retrieve_token(username, password)[0]
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Signin failed. Incorrect credentials.")


@app.route("/logout")
def logout():
    session.pop("user_signed_in", None)
    session.pop("username", None)
    # session.pop("token", None)

    return redirect(url_for("get_started"))


"""
__________________________
PROJECT ROUTES
__________________________
"""


@app.route("/new_project")
def new_project():
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    con = get_db()
    db = DevDashboard(con)
    proj = db.get_projects(username)
    return render_template("new_project.html", username=username, projects=proj)


@app.route('/delete_project', methods=['POST'])
def delete_project():
    project_name = request.form.get('project_name')
    username = session.get('username')
    con = get_db()
    db = DevDashboard(con)
    db.delete_project(username, project_name)
    return redirect(url_for('new_project'))


@app.route('/add_project', methods=['POST'])
def add_project():
    project_name = request.form.get('project_name')
    username = session.get('username')
    con = get_db()
    db = DevDashboard(con)
    db.add_project(username, project_name)
    return redirect(url_for('new_project'))


@app.route("/manage_project/<project_name>", methods=['POST', 'GET'])
def manage_project(project_name):
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    con = get_db()
    db = DevDashboard(con)

    # Fetch auth with email information
    cur = con.cursor()
    cur.execute("SELECT username, email, password FROM authwithemail WHERE project=?", (project_name,))
    auth_with_email = cur.fetchall()

    # Fetch auth without email information
    cur.execute("SELECT username, password FROM authwithoutemail WHERE project=?", (project_name,))
    auth_without_email = cur.fetchall()
    print(auth_with_email)
    print(auth_without_email)
    return render_template('manage_project.html', project_name=project_name, auth_with_email=auth_with_email,
                           auth_without_email=auth_without_email)


"""
__________________________
    WEBHOOK ROUTES
__________________________
"""
@app.route('/enable_webhook', methods=['POST'])
def enable_webhook():
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    project_name = request.form.get('project_name')
    webhook_url = request.form.get('webhook_url')
    con = get_db()
    db = ProtoBaseWebhooks(con)
    db.enable_webhooks(project_name,username,webhook_url)

    return redirect(url_for('manage_project', project_name=project_name))

@app.route('/disable_webhook', methods=['POST'])
def disable_webhook():
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    project_name = request.form.get('project_name')
    con = get_db()
    db = ProtoBaseWebhooks(con)
    db.disable_webhooks(project_name, username)

    return redirect(url_for('manage_project', project_name=project_name))

"""
__________________________
    DASHBOARD ROUTES
__________________________
"""


@app.route("/dashboard")
def dashboard():
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    return render_template("dashboard.html", username=username)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))

    username = session.get("username")
    con = get_db()
    db = DevDashboard(con)

    if request.method == 'POST':
        # Handle password change
        data = request.form
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password and confirm_password:
            if new_password == confirm_password:
                email = db.get_email(username)
                success = db.reset_password(username, new_password, email)
                if success:
                    flash("Password changed successfully.", "success")
                else:
                    flash("Failed to change password.", "danger")
            else:
                flash("Passwords do not match!", "danger")

        if 'pfp' in request.files:
            pfp = request.files['pfp']
            pfp_data = pfp.read()
            db.edit_pfp(username, pfp_data)
            flash("Profile picture updated successfully.", "success")

    # Retrieve user information
    cur = con.cursor()
    cur.execute("SELECT username, email, pfp FROM dev_api_tokens WHERE username=?", (username,))
    user_info = cur.fetchone()

    user_info = (user_info[0], user_info[1], user_info[2])

    return render_template('profile.html', user_info=user_info, username=username)


@app.route('/databases')
def databases():
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    con = get_db()
    db = DevDashboard(con)
    proj = db.get_project_names(username)
    return render_template("databases.html", projects=proj, username=username)


@app.route('/projects')
def projects():
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    con = get_db()
    db = DevDashboard(con)
    proj = db.get_project_names(username)
    return render_template("projects.html", projects=proj, username=username)


"""
__________________________
API ROUTES
__________________________
"""


@app.route("/auth_api/email-signup/")
def signup_email():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    email = request.args.get('email')
    token = request.args.get('token')
    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd and email:
        s = db.signup_with_email(usr, pwd, email, token)

        if s == 200:
            return jsonify({"message": "User Successfully SignedUp", "status-code": 200})
        elif s == 500:
            return jsonify({"message": "INVALID API TOKEN", "status-code": 500})
        else:
            return jsonify({"message": "Username Already Exists", "status-code": 400})
    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


@app.route("/auth_api/user-signup/")
def signup_username():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    token = request.args.get('token')

    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd:
        s = db.signup_with_username(usr, pwd, token)
        if s == 200:
            return jsonify({"message": "User Successfully SignedUp", "status-code": 200})
        elif s == 500:
            return jsonify({"message": "INVALID API TOKEN", "status-code": 500})
        else:
            return jsonify({"message": "Username Already Exists", "status-code": 400})

    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


@app.route("/auth_api/email-signin/")
def signin_email():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    email = request.args.get('email')
    token = request.args.get('token')

    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd and email:
        status, code = db.signin_with_email(usr, pwd, email, token)
        if status:
            if code == 200:
                return jsonify({"message": "User Successfully Logged in", "status-code": 200})
            elif code == 400:
                return jsonify({"message": "User Not Found", "status-code": 400})
            elif code == 500:
                return jsonify({"message": "INVALID API TOKEN", "status-code": 500})

        else:
            return jsonify({"message": "Incorrect Credentials", "status-code": 400})
    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


@app.route("/auth_api/user-signin/")
def signin_username():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    token = request.args.get('token')

    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd:
        status, code = db.signin_with_username(usr, pwd, token)
        if status:
            if code == 200:
                return jsonify({"message": "User Successfully Logged in", "status-code": 200})
            elif code == 400:
                return jsonify({"message": "User Not Found", "status-code": 400})
            elif code == 500:
                return jsonify({"message": "INVALID API TOKEN", "status-code": 500})

        else:
            return jsonify({"message": "Incorrect Credentials", "status-code": 400})
    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


"""
__________________________
PASSWORD ROUTES
__________________________
"""


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    con = get_db()
    db = DevDashboard(con)
    if request.method == 'GET':
        return render_template("forgot_password.html")
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        username = db.get_username(email)

        reset_link = f'https://protobase.pythonanywhere.com/reset_password/{username}'

        success = db.auth.send_reset_password_email(email, username, reset_link)

        if success:
            return jsonify(success=True, message="Reset email sent successfully.")
        else:
            return jsonify(success=False, message="Failed to send reset email.")


@app.route("/reset_password/<username>", methods=['GET', 'POST'])
def reset_password(username):
    con = get_db()
    db = DevDashboard(con)
    if request.method == 'GET':
        return render_template("reset_password.html", username=username)
    elif request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        confirm_password = data.get('cnf_password')
        if password == confirm_password:
            email = db.get_email(username)
            success = db.reset_password(username, password, email)
            if success:
                return jsonify(success=True, message="Password reset successfully.")

            else:
                return jsonify(success=False, message="Failed to reset password.")
        else:
            return jsonify(success=False, message="Passwords do not match!")


"""
__________________________
DATABASE CRUD ROUTES
__________________________
"""


def get_databases(username, project_name):
    db_path = f'databases/{username}/{project_name}.db'
    conn = sq.connect(db_path)
    return conn


@app.route('/create_table', methods=['POST'])
def create_table():
    username = session.get("username")
    project_name = request.form['project_name']
    table_name = request.form['table_name']
    columns = request.form.getlist('column_name[]')
    column_types = request.form.getlist('column_type[]')

    if not table_name or not columns or not column_types:
        return "Invalid input", 400

    column_definitions = ', '.join(f"{name} {dtype}" for name, dtype in zip(columns, column_types))
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"

    conn = get_databases(username, project_name)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

    return "Table created successfully", 200


@app.route('/insert_data', methods=['POST'])
def insert_data():
    username = session.get("username")
    project_name = request.form['project_name']
    table = request.form['table']
    data = {key: request.form[key] for key in request.form if key not in ['table', 'project_name']}

    if not data:
        return "No data provided", 400
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' for _ in data)
    values = tuple(data.values())

    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    try:
        conn = get_databases(username, project_name)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return "Data inserted successfully", 200
    except sq.OperationalError as e:
        return f"An error occurred: {e}", 500


@app.route('/read_data', methods=['POST'])
def read_data():
    username = session.get("username")
    project_name = request.form['project_name']
    table = request.form['table']
    query = f"SELECT * FROM {table}"

    conn = get_databases(username, project_name)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()

    data = [dict(zip(columns, row)) for row in rows]
    if data:
        return render_template('read_data.html', project_name=project_name, table=table, rows=data)
    else:
        return render_template("empty.html", table=table, project_name=project_name)


@app.route('/update_data', methods=['POST'])
def update_data():
    username = session.get("username")
    project_name = request.args.get('project_name')
    table = request.args.get('table')
    where_clause = request.args.get('where')

    if not project_name or not table or not where_clause:
        return "Missing parameters", 400
    set_clause = ', '.join(f"{key} = ?" for key in request.form if key != "where")
    values = tuple(request.form[key] for key in request.form)

    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    try:
        conn = get_databases(username, project_name)
        cursor = conn.cursor()
        cursor.execute(query, values[:-1])
        conn.commit()
        conn.close()
        return "Data updated successfully", 200
    except sq.OperationalError as e:
        return f"An error occurred: {e}", 500


@app.route('/delete_data', methods=['GET'])
def delete_data():
    username = session.get("username")
    project_name = request.args.get('project_name')
    table = request.args.get('table')
    where_clause = request.args.get('condition')
    if not project_name or not table or not where_clause:
        return "Missing parameters", 400

    query = f"DELETE FROM {table} WHERE {where_clause}"

    try:
        conn = get_databases(username, project_name)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return "Data deleted successfully", 200
    except sq.OperationalError as e:
        return f"An error occurred: {e}", 500


@app.route('/get_tables', methods=['GET'])
def get_tables():
    username = session.get("username")
    project_name = request.args.get('project_name')
    if not project_name:
        app.logger.error("Project name is missing in the request")
        return jsonify({"error": "Project name is required"}), 400

    app.logger.info(f"Received project_name: {project_name}")
    conn = get_databases(username, project_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(tables)


@app.route('/db_crud/<project_name>')
def db_crud(project_name):
    if not session.get("user_signed_in"):
        return redirect(url_for("get_started"))
    username = session.get("username")
    db_path = f"databases/{username}/{project_name}.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if not os.path.exists(db_path):
        conn = sq.connect(db_path)
        conn.close()
    return render_template("DB_CRUD.html", project_name=project_name)


"""
__________________________
DATABASE CRUD API ROUTES
__________________________
"""


def validate_api_token(token):
    con = get_db()
    db = ApiToken(con)
    return db.validate_token(token)


@app.before_request
def require_api_token():
    if request.endpoint in ['api_create_table', 'api_insert_data', 'api_read_data', 'api_update_data',
                            'api_delete_data']:
        token = request.headers.get('Authorization')
        if not token or not validate_api_token(token):
            return jsonify({"message": "Invalid or missing API token"}), 403


@app.route('/db_api/create_table', methods=['POST'])
def api_create_table():
    data = request.get_json()
    username = data.get('username')
    project_name = data.get('project_name')
    table_name = data.get('table_name')
    columns = data.get('columns')
    column_types = data.get('column_types')

    if not table_name or not columns or not column_types:
        return jsonify({"message": "Invalid input"}), 400

    column_definitions = ', '.join(f"{name} {dtype}" for name, dtype in zip(columns, column_types))
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"

    conn = get_databases(username, project_name)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

    return jsonify({"message": "Table created successfully"}), 200


@app.route('/db_api/insert_data', methods=['POST'])
def api_insert_data():
    data = request.get_json()
    username = data.get('username')
    project_name = data.get('project_name')
    table = data.get('table')
    row_data = data.get('data')

    if not row_data:
        return jsonify({"message": "No data provided"}), 400

    columns = ', '.join(row_data.keys())
    placeholders = ', '.join('?' for _ in row_data)
    values = tuple(row_data.values())

    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    try:
        conn = get_databases(username, project_name)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return jsonify({"message": "Data inserted successfully"}), 200
    except sq.OperationalError as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500


@app.route('/db_api/read_data', methods=['POST'])
def api_read_data():
    data = request.get_json()
    username = data.get('username')
    project_name = data.get('project_name')
    table = data.get('table')
    query = f"SELECT * FROM {table}"

    conn = get_databases(username, project_name)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()

    data = [dict(zip(columns, row)) for row in rows]
    return jsonify(data), 200


@app.route('/db_api/update_data', methods=['POST'])
def api_update_data():
    data = request.get_json()
    username = data.get('username')
    project_name = data.get('project_name')
    table = data.get('table')
    where_clause = data.get('where')
    update_data = data.get('data')
    column, data = tuple(where_clause.split("="))

    if not project_name or not table or not where_clause or not update_data:
        return jsonify({"message": "Missing parameters"}), 400

    set_clause = ', '.join(f"{key} = ?" for key in update_data)
    values = list(update_data.values())
    values.append(data)

    query = f"UPDATE {table} SET {set_clause} WHERE {column} = ?"
    try:
        conn = get_databases(username, project_name)
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        return jsonify({"message": "Data updated successfully"}), 200
    except sq.OperationalError as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500


@app.route('/db_api/delete_data', methods=['POST'])
def api_delete_data():
    data = request.get_json()
    username = data.get('username')
    project_name = data.get('project_name')
    table = data.get('table')
    where_clause = data.get('condition')
    column, data = tuple(where_clause.split("="))
    print(data)
    if not project_name or not table or not where_clause:
        return jsonify({"message": "Missing parameters"}), 400

    query = f"DELETE FROM {table} WHERE {column} = ?"

    try:
        conn = get_databases(username, project_name)
        cursor = conn.cursor()
        cursor.execute(query, (data,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Data deleted successfully"}), 200
    except sq.OperationalError as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500


if __name__ == '__main__':
    app.run()
