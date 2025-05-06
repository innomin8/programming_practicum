import os
import shutil

class DirectoryOperations:
    def __init__(self, manager):
        self.manager = manager

    def change_dir(self, *dir_parts):
        if not dir_parts:
            print("Укажите директорию")
            return

        dir_name = ' '.join(dir_parts)
        try:
            new_dir = self.manager.validate_path(dir_name)

            # Проверяем существование директории
            if not os.path.exists(new_dir):
                raise ValueError(f"Директория не существует: {new_dir}")
            if not os.path.isdir(new_dir):
                raise ValueError(f"Это не директория: {new_dir}")

            self.manager.current_dir = new_dir
            print(f"Текущая директория: {new_dir}")
        except Exception as e:
            print(f"Ошибка: {str(e)}")

    def list_dir(self):
        items = os.listdir(self.manager.current_dir)
        for item in items:
            path = os.path.join(self.manager.current_dir, item)
            if os.path.isdir(path):
                print(f"{item}/")
            else:
                print(item)

    def make_dir(self, *name_parts):
        """Создание директории с пробелами в имени"""
        dirname = self.manager.validate_path(' '.join(name_parts))
        try:
            os.makedirs(dirname, exist_ok=True)
            print(f"Директория создана: {dirname}")
        except Exception as e:
            print(f"Ошибка создания директории: {str(e)}")

    def remove_dir(self, dir_name):
        dir_path = self.manager.validate_path(dir_name)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Директория удалена: {dir_name}")
        else:
            raise ValueError(f"Директория не существует: {dir_name}")