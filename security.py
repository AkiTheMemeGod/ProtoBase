import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random as rd
from cred import *


class ProtobaseSecurity:

    @staticmethod
    def custom_poly_math(char_value: int, length_factor: int) -> int:
        """
        Custom polynomial mathematical transformation on a character's ASCII value.

        :param char_value: The ASCII value of the character.
        :param length_factor: A factor based on the length of username and email.
        :return: Transformed integer.
        """
        transformed_value = (char_value ** 4 - 5 * char_value ** 3 + 3 * char_value ** 2 - char_value +
                             length_factor + int(math.sin(char_value) * 100) + int(math.cos(length_factor) * 100)) % 256
        return transformed_value

    def encrypt(self, username: str, password: str, email: str = "example@gmail.com") -> str:
        """
        Encrypt the password by transforming each character's ASCII value.

        :param username: The username for length-based transformation.
        :param password: The password to be encrypted.
        :param email: The email for length-based transformation.
        :return: A list of encrypted values representing the password.
        """
        length_factor = len(username) * len(email)
        encrypted_values = []

        for char in password:
            enc_value = self.custom_poly_math(ord(char), length_factor)
            encrypted_values.append(hex(enc_value))

        return "".join(encrypted_values)


class Protobase2FA:
    @staticmethod
    def generate_otp():
        otp = rd.randint(100000, 999999)
        return otp

    def send_mail(self, email, username):
        otp = self.generate_otp()
        subject = "Your Protobase Signup OTP Code"
        with open('static/otp.html', 'r') as file:
            body = file.read()

        # Replace placeholders with actual values
        body = body.replace("{username}", username).replace("{otp}", str(otp))
        sender_email = SENDER_EMAIL
        sender_password = SENDER_PASSWORD

        message = MIMEMultipart()
        message["From"] = "ProtoBase"
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(message)
            return True, otp
        except Exception as e:
            return False, None

    @staticmethod
    def send_reset_password_email(email, username, reset_link):
        subject = "Protobase Password Reset Request"

        with open('static/reset_password_template.html', 'r') as file:
            body = file.read()

        body = body.replace("{username}", username).replace("{reset_link}", reset_link)

        sender_email = SENDER_EMAIL
        sender_password = SENDER_PASSWORD

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

