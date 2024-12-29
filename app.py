from flask import *
import sqlite3 as sq
from Database import ProtoBaseAuthentication
app = Flask(__name__)


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


@app.route("/auth_api/email-signup/")
def signup_email():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    email = request.args.get('email')
    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd and email:
        s = db.signup_with_email(usr, pwd, email)

        if s == 200:
            return jsonify({"message": "User Successfully SignedUp", "status-code": 400})
        else:
            return jsonify({"message": "Username Already Exists", "status-code": 400})
    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


@app.route("/auth_api/user-signup/")
def signup_username():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd:
        s = db.signup_with_username(usr, pwd)
        if s == 200:
            return jsonify({"message": "User Successfully SignedUp", "status-code": 200})
        else:
            return jsonify({"message": "Username Already Exists", "status-code": 400})

    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


@app.route("/auth_api/email-signin/")
def signin_email():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    email = request.args.get('email')
    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd and email:
        status, code = db.signin_with_email(usr, pwd, email)
        if status:
            if code == 200:
                return jsonify({"message": "User Successfully Logged in", "status-code": 200})
            elif code == 400:
                return jsonify({"message": "User Not Found", "status-code": 400})
        else:
            return jsonify({"message": "Incorrect Credentials", "status-code": 400})
    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


@app.route("/auth_api/user-signin/")
def signin_username():
    usr = request.args.get('usr')
    pwd = request.args.get('pwd')
    con = get_db()
    db = ProtoBaseAuthentication(con)
    if usr and pwd:
        status, code = db.signin_with_username(usr, pwd)
        if status:
            if code == 200:
                return jsonify({"message": "User Successfully Logged in", "status-code": 200})
            elif code == 400:
                return jsonify({"message": "User Not Found", "status-code": 400})
        else:
            return jsonify({"message": "Incorrect Credentials", "status-code": 400})
    else:
        return jsonify({"message": "Invalid input parameters", "status-code": 400})


if __name__ == '__main__':
    app.run()
