import sqlite3 as sq
import secrets as st
from security import ProtobaseSecurity, Protobase2FA
import ast


class Helpers:
    def __init__(self, con=None):
        if con:
            self.con = con
        else:
            self.con = sq.connect("Authentication.db", check_same_thread=False)
        self.sec = ProtobaseSecurity()
        self.auth = Protobase2FA()

    def duplicate_email_check(self, email):
        cur = self.con.cursor()
        cur.execute("SELECT email FROM authwithemail")
        emails = cur.fetchall()
        emails = [i[0] for i in emails]
        return email in emails

    def duplicate_username_check(self, username, table):
        cur = self.con.cursor()
        cur.execute(f"SELECT username FROM {table}")
        usernames = cur.fetchall()
        usernames = [i[0] for i in usernames]
        return username in usernames


class ApiToken(Helpers):

    @staticmethod
    def generate_api_token():
        token = st.token_urlsafe(64)
        return token

    def add_project(self, username, project_name):
        cur = self.con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens WHERE username=?", (username,))
        projects = cur.fetchone()[0]
        projects_dict = eval(projects)
        if project_name in projects_dict:
            return None
        token = self.generate_api_token()
        projects_dict[project_name] = token
        cur.execute("UPDATE dev_api_tokens SET token=? WHERE username=?", (str(projects_dict), username))
        self.con.commit()
        return token

    def delete_project(self, username, project_name):
        cur = self.con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens WHERE username=?", (username,))
        projects = cur.fetchone()[0]
        projects_dict = eval(projects)
        if project_name in projects_dict:
            del projects_dict[project_name]
            cur.execute("UPDATE dev_api_tokens SET token=? WHERE username=?", (str(projects_dict), username))
            self.con.commit()
            return True
        return False

    def get_projects(self, username):
        try:
            cur = self.con.cursor()
            cur.execute("SELECT token, uses FROM dev_api_tokens WHERE username=?", (username,))
            projects, uses = cur.fetchone()
            projects_dict = eval(projects)
            return [(project, token, uses) for project, token in projects_dict.items()]
        except TypeError:
            return []

    def validate_token(self, token):
        cur = self.con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens")
        projects = cur.fetchall()  # Fetch all rows

        # Parse each dictionary string and extract values
        tokens = []
        for row in projects:
            # The dictionary string is the first (and only) element in each tuple
            dict_str = row[0]
            parsed_dict = ast.literal_eval(dict_str)  # Safely parse string to dictionary
            tokens.extend(parsed_dict.values())  # Add all dictionary values to the list

        return token in tokens

    # TODO: Implement it ASAP
    def update_token_usage(self, token):
        cur = self.con.cursor()
        cur.execute("UPDATE dev_api_tokens SET uses = uses + 1 WHERE token=?", (token,))
        self.con.commit()


class DevDashboard(ApiToken):

    def validate_developer(self, username, password):
        cur = self.con.cursor()
        password = self.sec.encrypt(username=username, password=password)

        data = (username, password)
        cur.execute("SELECT username, password FROM dev_api_tokens")
        creds = cur.fetchall()
        return data in creds

    def signup_developer(self, username, password, email, user_otp):
        try:
            cur = self.con.cursor()
            password = self.sec.encrypt(username=username, password=password, email=email)
            data = (username, password, "{}", 0, email)
            cur.execute("INSERT INTO dev_api_tokens VALUES (?,?,?,?,?)", data)
            self.con.commit()
            return True

        except sq.IntegrityError:
            return False

        finally:
            self.con.close()


class ProtoBaseAuthentication(DevDashboard):

    def signup_with_email(self, username, password, email, token):
        if self.validate_token(token):

            cur = self.con.cursor()
            if not self.duplicate_email_check(email):
                password = self.sec.encrypt(username, password, email)

                cur.execute("INSERT INTO authwithemail VALUES (?,?,?)", (username, password, email))
                self.update_token_usage(token)
                self.con.commit()
                self.con.close()
                return 200
            else:
                return 400
        else:
            return 500

    def signup_with_username(self, username, password, token):
        if self.validate_token(token):
            cur = self.con.cursor()
            if not self.duplicate_username_check(username, "authwithoutemail"):
                password = self.sec.encrypt(username, password)

                cur.execute("INSERT INTO authwithoutemail VALUES (?,?)", (username, password))
                self.update_token_usage(token)

                self.con.commit()
                self.con.close()
                return 200
            else:
                return 400
        else:
            return 500

    def signin_with_email(self, username, password, email, token):
        if self.validate_token(token):
            password = self.sec.encrypt(username, password, email)
            cur = self.con.cursor()
            cur.execute(f"SELECT password, email FROM authwithemail WHERE username=?", (username, ))
            details = cur.fetchone()
            if not details:
                return True, 400
            elif (password, email, ) == details:
                self.update_token_usage(token)

                return True, 200
            else:
                return False, 400
        else:
            return True, 500

    def signin_with_username(self, username, password, token):
        if self.validate_token(token):
            password = self.sec.encrypt(username, password)
            cur = self.con.cursor()
            cur.execute(f"SELECT password FROM authwithoutemail WHERE username=?", (username,))
            details = cur.fetchone()
            if not details:
                return True, 400
            elif (password, ) == details:
                self.update_token_usage(token)

                return True, 200
            else:
                return False, 400
        else:
            return True, 500
