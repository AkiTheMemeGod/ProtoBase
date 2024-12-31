from flask import *
from flask_cors import CORS
import sqlite3 as sq
from Database import ProtoBaseAuthentication
from schemas import openapi_schema
app = Flask(__name__)
CORS(app)


def get_db():
    if "db" not in g:
        g.db = sq.connect("Authentication.db")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route('/')
def homepage():
    return render_template("index.html")


@app.route('/get-started')
def get_started():
    return render_template('get-started.html')


@app.route('/openapi.json')
def openapi():
    """Serve the OpenAPI schema."""
    return jsonify(openapi_schema)


@app.route('/docs')
def swagger_ui():
    """Serve the Swagger UI."""
    return render_template('swagger.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        con = get_db()
        db = ProtoBaseAuthentication(con)
        status, token = db.assign_api_token(username, password)
        if status:
            return jsonify(success=True, api_token=token)
        else:
            return jsonify(success=False, message="Signup failed. User may already exist.")


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        con = get_db()
        db = ProtoBaseAuthentication(con)
        cur = con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens WHERE username=? AND password=?", (username, password))
        result = cur.fetchone()
        if result:
            return jsonify(success=True, api_token=result[0])
        else:
            return jsonify(success=False, message="Signin failed. Incorrect credentials.")


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
            return jsonify({"message": "User Successfully SignedUp", "status-code": 400})
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


if __name__ == '__main__':
    app.run()
