import os
import shutil
import zipfile
import fnmatch


class FileOperations:
    def __init__(self, manager):
        self.manager = manager

    def create_file(self, path):
        """Создание файла с автоматическим определением типа"""
        try:
            # Для .doc файлов создаем минимальный заголовок
            if path.lower().endswith('.doc'):
                with open(path, 'wb') as f:
                    f.write(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1')  # Заголовок DOCX
            else:
                open(path, 'a').close()
            print(f"Файл создан: {path}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def read_file(self, path):
        """Чтение файла"""
        try:
            with open(path, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"Ошибка: {e}")

    def write_file(self, path, content, mode='w'):
        """Запись в файл с поддержкой текстовых и бинарных режимов"""
        try:
            # Для .doc файлов используем бинарный режим
            if path.lower().endswith('.doc'):
                with open(path, 'wb') as f:
                    if isinstance(content, str):
                        f.write(content.encode('utf-8'))
                    else:
                        f.write(content)
            else:
                # Для обычных текстовых файлов
                with open(path, mode) as f:
                    f.write(content)
            print(f"Записано в: {path}")
        except Exception as e:
            print(f"Ошибка: {str(e)}")

    def delete_file(self, path):
        """Удаление файла"""
        try:
            os.remove(path)
            print(f"Удалён: {path}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def copy_file(self, src, dest):
        """Копирование файла"""
        try:
            shutil.copy2(src, dest)
            print(f"Скопировано: {src} → {dest}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def move_file(self, src, dest):
        """Перемещение файла"""
        try:
            shutil.move(src, dest)
            print(f"Перемещено: {src} → {dest}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def rename_file(self, old, new):
        """Переименование файла"""
        try:
            os.rename(old, new)
            print(f"Переименовано: {old} → {new}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def zip_files(self, files, archive_path):
        """Создание архива"""
        try:
            with zipfile.ZipFile(archive_path, 'w') as zipf:
                for file in files:
                    zipf.write(file, os.path.basename(file))
            print(f"Архив создан: {archive_path}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def unzip_file(self, archive_path, target_dir=None):
        """Распаковка архива"""
        try:
            if target_dir is None:
                target_dir = os.path.dirname(archive_path)

            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(target_dir)
            print(f"Распаковано в: {target_dir}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def search_files(self, pattern, search_dir=None):
        """Поиск файлов по шаблону"""
        try:
            if search_dir is None:
                search_dir = self.manager.current_dir

            matches = []
            for root, _, files in os.walk(search_dir):
                for filename in fnmatch.filter(files, pattern):
                    matches.append(os.path.join(root, filename))

            if not matches:
                print(f"Файлы по шаблону '{pattern}' не найдены")
                return

            print("Найдены файлы:")
            for match in matches:
                print(f"- {match}")

        except Exception as e:
            print(f"Ошибка поиска: {str(e)}")