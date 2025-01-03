import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random as rd
from dotenv import load_dotenv
load_dotenv()


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
        body = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100%;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
        }}
        .header {{
            background: linear-gradient(90deg, #6a00ff, #9e2fff);
            color: white;
            padding: 10px 0;
            text-align: center;
        }}
        .content {{
            padding: 20px;
        }}
        .otp {{
            font-size: 24px;
            font-weight: bold;
            color: #6a00ff;
            text-align: center;
        }}
        .name {{
            font-size: 24px;
            font-weight: bold;
            color: #6a00ff;
        }}
        .footer {{
            background: linear-gradient(90deg, #9e2fff, #6a00ff);

            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Protobase</h1>
        </div>
        <div class="content">
            <p class="name">Dear {username},</p>
            <p>Thank you for signing up with Protobase. To complete your registration, please use the following One-Time Password (OTP):</p>
            <p class="otp">{otp}</p>
            <p>This OTP is valid for the next 10 minutes. Please do not share this code with anyone.</p>
            <p>If you did not request this code, please ignore this email or contact our support team immediately.</p>
            <p>Best regards,<br>The Protobase Team</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Protobase. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

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

