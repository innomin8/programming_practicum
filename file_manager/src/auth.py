import os
import json
import hashlib


class UserManager:
    def __init__(self, config):
        self.config = config
        self.users_file = os.path.join(config['workspace'], '.users.json')
        self.load_users()

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)

    def register(self, username, password, is_admin=False):
        if username in self.users:
            raise ValueError("Пользователь уже существует")

        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )

        self.users[username] = {
            'salt': salt.hex(),
            'key': key.hex(),
            'home': username,
            'is_admin': is_admin
        }

        # Создаем домашнюю директорию
        home_dir = os.path.join(self.config['workspace'], username)
        os.makedirs(home_dir, exist_ok=True)

        self.save_users()
        print("Пользователь успешно зарегистрирован")

    def login(self, username, password):
        if username not in self.users:
            print("Пользователь не найден")
            return False

        user_data = self.users[username]
        salt = bytes.fromhex(user_data['salt'])
        key = bytes.fromhex(user_data['key'])

        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )

        if key == new_key:
            print("Авторизация успешна")
            return True
        else:
            print("Неверный пароль")
            return False