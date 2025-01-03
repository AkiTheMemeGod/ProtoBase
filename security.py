import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import random as rd


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

    def send_mail(self, email):
        otp = self.generate_otp()
        subject = "Your Protobase Signup OTP Code"
        body = (
            f"Dear User,\n\n"
            f"Thank you for signing up with Protobase. To complete your registration, please use the following One-Time Password (OTP):\n\n"
            f"    {otp}\n\n"
            f"This OTP is valid for the next 10 minutes. Please do not share this code with anyone.\n\n"
            f"If you did not request this code, please ignore this email or contact our support team immediately.\n\n"
            f"Best regards,\n"
            f"The Protobase Team"
        )

        sender_email = "akis.pwdchecker@gmail.com"
        sender_password = "tjjqhaifdobuluhg"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            # Connecting to the server
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            # print("Email sent successfully.")
            return True, otp
        except Exception as e:
            # print(f"Failed to send email: {e}")
            return False, None

