import random

from faker import Faker

faker = Faker()


class RandomData:
    @staticmethod
    def get_username(length: int = random.randint(3, 15)) -> str:
        return ''.join(faker.random_letters(length))

    @staticmethod
    def get_password() -> str:
        upper = [letter.upper() for letter in faker.random_letters(length=3)]
        lower = [letter.lower() for letter in faker.random_letters(length=3)]
        digits = [str(faker.random_digit()) for _ in range(3)]
        special = [random.choice('!@#$%^&')]
        password = upper + lower + digits + special
        random.shuffle(password)
        return ''.join(password)

    @staticmethod
    def get_balance() -> float:
        return round(random.uniform(1, 5000), 2)

    @staticmethod
    def get_profile_name() -> str:
        return f"{faker.first_name()} {faker.last_name()}"
