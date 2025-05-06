import os
import json
from getpass import getpass
from src.core import FileManager
from src.auth import UserManager


def load_config():
    """Загрузка конфигурации из файла"""
    config_path = os.path.join('config', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    config = load_config()
    user_manager = UserManager(config)

    print("┌──────────────────────────────────────┐")
    print("│           ФАЙЛОВЫЙ МЕНЕДЖЕР          │")
    print("└──────────────────────────────────────┘")

    while True:
        print("\n1. Вход\n2. Регистрация\n3. Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            username = input("Имя пользователя: ")
            password = getpass("Пароль: ")
            if user_manager.login(username, password):
                manager = FileManager(config, username)
                manager.run()
        elif choice == '2':
            username = input("Новое имя пользователя: ")
            password = getpass("Пароль: ")
            user_manager.register(username, password)
        elif choice == '3':
            break


if __name__ == "__main__":
    main()