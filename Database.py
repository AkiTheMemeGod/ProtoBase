import os
import sqlite3 as sq
import secrets as st
from security import ProtobaseSecurity, Protobase2FA
import ast
import platform as p
from paths import *
if p.system() == 'Linux':
    path = linux
    static_path = static_lin
else:
    path = windows
    static_path = static_win

print(f"Starting Up in {p.system()} taking database path as : {path}")


class Helpers:
    def __init__(self, con=None):
        """
        Initialize the Helpers class with a database connection.

        :param con: Optional database connection object.
        """
        if con:
            self.con = con
        else:
            self.con = sq.connect(path, check_same_thread=False)
        self.sec = ProtobaseSecurity()
        self.auth = Protobase2FA()

    def duplicate_email_check(self, email):
        """
        Check if the given email already exists in the database.

        :param email: Email to check for duplication.
        :return: True if email exists, False otherwise.
        """
        cur = self.con.cursor()
        cur.execute("SELECT email FROM authwithemail")
        emails = cur.fetchall()
        emails = [i[0] for i in emails]
        return email in emails

    def duplicate_username_check(self, username, table):
        """
        Check if the given username already exists in the specified table.

        :param username: Username to check for duplication.
        :param table: Table name to check in.
        :return: True if username exists, False otherwise.
        """
        cur = self.con.cursor()
        cur.execute(f"SELECT username FROM {table}")
        usernames = cur.fetchall()
        usernames = [i[0] for i in usernames]
        return username in usernames


class ApiToken(Helpers):

    @staticmethod
    def generate_api_token():
        """
        Generate a secure API token.

        :return: Generated API token.
        """
        token = st.token_urlsafe(64)
        return token

    def add_project(self, username, project_name):
        """
        Add a new project for the given username.

        :param username: Username of the developer.
        :param project_name: Name of the project to add.
        :return: Generated token for the project or None if project already exists.
        """
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
        """
        Delete a project for the given username.

        :param username: Username of the developer.
        :param project_name: Name of the project to delete.
        :return: True if project was deleted, False otherwise.
        """
        cur = self.con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens WHERE username=?", (username,))
        projects = cur.fetchone()[0]
        projects_dict = eval(projects)
        if project_name in projects_dict:
            del projects_dict[project_name]
            cur.execute("UPDATE dev_api_tokens SET token=? WHERE username=?", (str(projects_dict), username))
            db_path = f'databases/{username}/{project_name}.db'
            os.remove(db_path)
            self.con.commit()
            return True
        return False

    def get_projects(self, username):
        """
        Get all projects for the given username.

        :param username: Username of the developer.
        :return: List of tuples containing project name, token, and usage count.
        """
        try:
            cur = self.con.cursor()
            cur.execute("SELECT token, uses FROM dev_api_tokens WHERE username=?", (username,))
            projects, uses = cur.fetchone()
            projects_dict = eval(projects)
            return [(project, token, uses) for project, token in projects_dict.items()]
        except TypeError:
            return []

    def get_project_names(self, username):
        """
        Get all project names for the given username.

        :param username: Username of the developer.
        :return: List of project names.
        """
        try:
            cur = self.con.cursor()
            cur.execute("SELECT token FROM dev_api_tokens WHERE username=?", (username,))
            projects = cur.fetchone()
            if projects:
                projects_dict = ast.literal_eval(projects[0])
                return list(projects_dict.keys())
            return []
        except TypeError:
            return []

    def validate_token(self, token):
        """
        Validate if the given token exists in the database.

        :param token: Token to validate.
        :return: True if token is valid, False otherwise.
        """
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

    def update_token_usage(self, token):
        """
        Update the usage count of the given token.

        :param token: Token to update usage for.
        """
        cur = self.con.cursor()
        cur.execute("UPDATE dev_api_tokens SET uses = uses + 1 WHERE token=?", (token,))
        self.con.commit()

    def get_project_name_by_token(self, token):
        """
        Get the project name associated with the given token.

        :param token: API token to search for.
        :return: Project name if token is found, None otherwise.
        """
        cur = self.con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens")
        projects = cur.fetchall()  # Fetch all rows

        for row in projects:
            projects_dict = ast.literal_eval(row[0])  # Safely parse string to dictionary
            for project_name, project_token in projects_dict.items():
                if project_token == token:
                    return project_name
        return None


class DevDashboard(ApiToken):

    def validate_developer(self, username, password, email):
        """
        Validate developer credentials.

        :param username: Username of the developer.
        :param password: Password of the developer.
        :param email: email of the developer.

        :return: True if credentials are valid, False otherwise.
        """
        cur = self.con.cursor()
        password = self.sec.encrypt(username=username, password=password, email=email)

        data = (username, password)
        cur.execute("SELECT username, password FROM dev_api_tokens")
        creds = cur.fetchall()
        return data in creds

    def signup_developer(self, username, password, email, user_otp, c_otp):

        """
        Sign up a new developer.

        :param username: Username of the developer.
        :param password: Password of the developer.
        :param email: Email of the developer.
        :param user_otp: OTP for verification.
        :return: True if signup was successful, False otherwise.
        """
        try:
            if int(c_otp) == int(user_otp):
                cur = self.con.cursor()
                password = self.sec.encrypt(username=username, password=password, email=email)
                data = (username, password, "{}", 0, email, open(f'{static_path}/img.png', 'rb').read())
                cur.execute("INSERT INTO dev_api_tokens VALUES (?,?,?,?,?,?)", data)
                self.con.commit()
                return True

            else:
                return False
        except sq.IntegrityError:
            return False

        finally:
            self.con.close()

    def get_username(self, email):
        """
        Get the username associated with the given email.

        :param email: Email to get the username for.
        :return: Username associated with the email.
        """
        cur = self.con.cursor()
        cur.execute("SELECT username FROM dev_api_tokens WHERE email=?", (email, ))
        username = cur.fetchone()[0]
        return username

    def get_email(self, username):
        """
        Get the email associated with the given username.

        :param username: Username to get the email for.
        :return: Email associated with the username.
        """
        cur = self.con.cursor()
        cur.execute("SELECT email FROM dev_api_tokens WHERE username=?", (username,))
        email = cur.fetchone()[0]
        return email

    def reset_password(self, username, password, email):
        """
        Reset the password for the given username.

        :param username: Username of the developer.
        :param password: New password to set.
        :param email: Email of the developer.
        :return: True if password reset was successful, False otherwise.
        """
        password = self.sec.encrypt(username, password, email)
        cur = self.con.cursor()
        try:
            cur.execute("UPDATE dev_api_tokens SET password=? WHERE username=?", (password, username))
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.con.commit()

    def edit_pfp(self, usr, pfp):
        data = (pfp, usr)
        cursor = self.con.cursor()
        cursor.execute("Update dev_api_tokens set pfp=? where username=?", data)
        self.con.commit()

    def pfp(self, usr):
        usr = (usr, )
        cursor = self.con.cursor()
        cursor.execute("SElECT pfp FROM dev_api_tokens where username=?", usr)
        pfps = cursor.fetchone()[0]
        # pfps = [i[0] for i in pfps]
        return pfps


class ProtoBaseAuthentication(DevDashboard):

    def signup_with_email(self, username, password, email, token):
        """
        Sign up a new user with email.

        :param username: Username of the user.
        :param password: Password of the user.
        :param email: Email of the user.
        :param token: API token for validation.
        :return: Status code indicating the result of the signup.
        """
        if self.validate_token(token):

            cur = self.con.cursor()
            if not self.duplicate_email_check(email):
                password = self.sec.encrypt(username, password, email)
                project_name = self.get_project_name_by_token(token)
                cur.execute("INSERT INTO authwithemail VALUES (?,?,?,?)", (username, password, email, project_name))
                self.update_token_usage(token)

                self.con.commit()
                self.con.close()
                return 200
            else:
                return 400
        else:
            return 500

    def signup_with_username(self, username, password, token):
        """
        Sign up a new user with username.

        :param username: Username of the user.
        :param password: Password of the user.
        :param token: API token for validation.
        :return: Status code indicating the result of the signup.
        """
        if self.validate_token(token):
            cur = self.con.cursor()
            if not self.duplicate_username_check(username, "authwithoutemail"):
                password = self.sec.encrypt(username, password)
                project_name = self.get_project_name_by_token(token)

                cur.execute("INSERT INTO authwithoutemail VALUES (?,?,?)", (username, password, project_name))
                self.update_token_usage(token)

                self.con.commit()
                self.con.close()
                return 200
            else:
                return 400
        else:
            return 500

    def signin_with_email(self, username, password, email, token):
        """
        Sign in a user with email.

        :param username: Username of the user.
        :param password: Password of the user.
        :param email: Email of the user.
        :param token: API token for validation.
        :return: Tuple indicating success status and status code.
        """
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
        """
        Sign in a user with username.

        :param username: Username of the user.
        :param password: Password of the user.
        :param token: API token for validation.
        :return: Tuple indicating success status and status code.
        """
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
