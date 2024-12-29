import sqlite3 as sq


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

    def duplicate_username_check(self, username):
        cur = self.con.cursor()
        cur.execute("SELECT email FROM authwithemail")
        usernames = cur.fetchall()
        usernames = [i[0] for i in usernames]
        return username in usernames


class ProtoBaseAuthentication(Helpers):

    def signup_with_email(self, username, password, email):
        cur = self.con.cursor()
        if not self.duplicate_email_check(email):
            cur.execute("INSERT INTO authwithemail VALUES (?,?,?)", (username, password, email))
            self.con.commit()
            self.con.close()
            return 200
        else:
            return 400

    def signup_with_username(self, username, password):
        cur = self.con.cursor()
        if not self.duplicate_username_check(username):
            cur.execute("INSERT INTO authwithoutemail VALUES (?,?)", (username, password))
            self.con.commit()
            self.con.close()
            return 200
        else:
            return 400

    def signin_with_email(self, username, password, email):
        cur = self.con.cursor()
        cur.execute(f"SELECT password, email FROM authwithemail WHERE username=?", (username, ))
        details = cur.fetchone()
        return (password, email, ) == details

    def signin_with_username(self, username, password):
        cur = self.con.cursor()
        cur.execute(f"SELECT password FROM authwithoutemail WHERE username=?", (username,))
        details = cur.fetchone()
        return (password,) == details


