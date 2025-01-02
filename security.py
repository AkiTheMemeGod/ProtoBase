import math


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
