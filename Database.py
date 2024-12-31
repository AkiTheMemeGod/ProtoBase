import sqlite3 as sq
import secrets as st


class Helpers:
    def __init__(self, con=None):
        if con:
            self.con = con
        else:
            self.con = sq.connect("Authentication.db", check_same_thread=False)

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

    def assign_api_token(self, username, password):
        cur = self.con.cursor()
        if not self.duplicate_username_check(username, "dev_api_tokens"):
            token = self.generate_api_token()
            try:
                cur.execute("INSERT INTO dev_api_tokens VALUES (?, ?, ?, ?)", (username, password, token, 0))
                self.con.commit()
                return True, token
            except sq.IntegrityError:
                return False, "Database error while assigning token."
        else:
            cur.execute('SELECT token FROM dev_api_tokens WHERE username=?', (username,))
            token = cur.fetchone()[0]
            return True, token

    def retrieve_token(self, username, password):
        cur = self.con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens WHERE username=? AND password=?", (username, password))
        return cur.fetchone()


    def validate_token(self, token):
        cur = self.con.cursor()
        cur.execute("SELECT token FROM dev_api_tokens")
        tokens = cur.fetchall()
        tokens = [i[0] for i in tokens]
        return token in tokens

    def update_token_usage(self, token):
        cur = self.con.cursor()
        cur.execute("UPDATE dev_api_tokens SET uses = uses + 1 WHERE token=?", (token,))
        self.con.commit()


class ProtoBaseAuthentication(ApiToken):

    def signup_with_email(self, username, password, email, token):
        if self.validate_token(token):

            cur = self.con.cursor()
            if not self.duplicate_email_check(email):
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
