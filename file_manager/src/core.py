import os
import shutil
from .file_ops import FileOperations
from .dir_ops import DirectoryOperations


class FileManager:
    def __init__(self, config, username):
        self.username = username
        self.workspace = os.path.abspath(os.path.join(config['workspace'], username))
        os.makedirs(self.workspace, exist_ok=True)
        self.current_dir = self.workspace
        self.file_ops = FileOperations(self)
        self.dir_ops = DirectoryOperations(self)
        self.quota = config.get('quota', {}).get('default', 1024 * 1024 * 100)  # 100MB по умолчанию
        self.setup_commands()

    def show_help(self):
        """Показать справку по командам"""
        print("\nДоступные команды:")
        print("  help - показать эту справку")
        print("  exit - выход из программы")
        print("  cd <dir> - перейти в директорию")
        print("  ls - список файлов и папок")
        print("  pwd - текущий путь")
        print("  mkdir <name> - создать директорию")
        print("  rmdir <name> - удалить директорию")
        print("  create <file> - создать файл")
        print("  read <file> - прочитать файл")
        print("  write <file> <content> - записать в файл")
        print("  delete <file> - удалить файл")
        print("  copy <src> <dest> - копировать файл")
        print("  move <src> <dest> - переместить файл")
        print("  rename <old> <new> - переименовать файл")
        print("  zip <files> <archive> - создать архив")
        print("  unzip <archive> - распаковать архив")
        print("  quota - показать квоту диска")
        print("  search <pattern> - поиск файлов")

    def exit(self):
        """Выход из программы"""
        print("\nЗавершение работы файлового менеджера...")
        raise SystemExit

    def process_path_args(self, args):
        """Объединяет аргументы пути и возвращает нормализованный путь"""
        if not args:
            return ""

        # Объединяем все аргументы через пробел
        path = ' '.join(args)

        # Удаляем лишние кавычки если они есть
        if (path.startswith('"') and path.endswith('"')) or \
                (path.startswith("'") and path.endswith("'")):
            path = path[1:-1]

        # Нормализуем путь
        path = os.path.normpath(path.strip())

        # Проверяем абсолютный путь
        if os.path.isabs(path):
            return path

        # Для относительных путей добавляем текущую директорию
        return os.path.join(self.current_dir, path)

    def get_prompt(self):
        """Генерация приглашения командной строки"""
        # Получаем относительный путь от рабочей директории
        rel_path = os.path.relpath(self.current_dir, self.workspace)

        # Заменяем точку (текущую директорию) на ~ для красоты
        if rel_path == '.':
            return f"{self.username} ~"
        return f"{self.username} {rel_path}"

    def validate_path(self, path):
        """Обработка путей с любым количеством пробелов"""
        # Сохраняем оригинальные пробелы внутри кавычек
        if (path.startswith('"') and path.endswith('"')) or \
                (path.startswith("'") and path.endswith("'")):
            path = path[1:-1]

        # Заменяем множественные пробелы на одинарные (кроме UNC-путей)
        if not path.startswith('\\\\'):  # Не трогаем UNC-пути типа \\server\share
            path = ' '.join(path.split())

        # Нормализация пути
        try:
            path = os.path.normpath(path)
            if os.path.isabs(path):
                return path
            return os.path.join(self.current_dir, path)
        except Exception as e:
            raise ValueError(f"Некорректный путь: {str(e)}")

    def print_working_dir(self):
        """Показать текущую директорию"""
        print(f"Текущая директория: {self.current_dir}")

    def show_quota(self):
        """Показать информацию о квоте"""
        used = self.get_directory_size(self.workspace)
        print(f"\nИспользовано: {used / 1024:.1f} KB из {self.quota / 1024:.1f} KB")

    def get_directory_size(self, directory):
        """Вычислить размер директории"""
        total = 0
        for root, dirs, files in os.walk(directory):
            for f in files:
                fp = os.path.join(root, f)
                total += os.path.getsize(fp)
        return total

    def setup_commands(self):
        """Настройка доступных команд"""
        self.commands = {
            'help': self.show_help,
            'exit': self.exit,
            'cd': self.dir_ops.change_dir,
            'ls': self.dir_ops.list_dir,
            'pwd': self.print_working_dir,
            'mkdir': self.dir_ops.make_dir,
            'rmdir': self.dir_ops.remove_dir,
            'create': self.file_ops.create_file,
            'read': self.file_ops.read_file,
            'write': self.file_ops.write_file,
            'delete': self.file_ops.delete_file,
            'copy': self.file_ops.copy_file,
            'move': self.file_ops.move_file,
            'rename': self.file_ops.rename_file,
            'zip': self.file_ops.zip_files,
            'unzip': self.file_ops.unzip_file,
            'quota': self.show_quota,
            'search': self.file_ops.search_files,
        }

    def run(self):
        """Основной цикл обработки команд"""
        print(f"\nДобро пожаловать, {self.username}!")
        print("Введите 'help' для списка команд\n")

        while True:
            try:
                # Получаем ввод пользователя
                user_input = input(f"{self.get_prompt()}> ").strip()
                if not user_input:
                    continue

                # Разбиваем на команду и аргументы
                parts = self.split_command(user_input)
                cmd = parts[0].lower()
                args = parts[1:]

                # Обработка команд
                if cmd == 'help':
                    self.show_help()

                elif cmd == 'exit':
                    self.exit()

                elif cmd == 'cd':
                    if not args:
                        print("Укажите директорию")
                        continue
                    path = self.process_path_args(args)
                    self.dir_ops.change_dir(path)

                elif cmd == 'ls':
                    self.dir_ops.list_dir()

                elif cmd == 'pwd':
                    self.print_working_dir()

                elif cmd == 'mkdir':
                    if not args:
                        print("Укажите имя директории")
                        continue
                    path = self.process_path_args(args)
                    self.dir_ops.make_dir(path)

                elif cmd == 'rmdir':
                    if not args:
                        print("Укажите имя директории")
                        continue
                    path = self.process_path_args(args)
                    self.dir_ops.remove_dir(path)

                elif cmd == 'create':
                    if not args:
                        print("Укажите имя файла")
                        continue
                    path = self.process_path_args(args)
                    self.file_ops.create_file(path)

                elif cmd == 'read':
                    if not args:
                        print("Укажите имя файла")
                        continue
                    path = self.process_path_args(args)
                    self.file_ops.read_file(path)

                elif cmd == 'write':
                    if len(args) < 2:
                        print("Укажите имя файла и содержание")
                        continue
                    path = self.process_path_args([args[0]])
                    content = ' '.join(args[1:])
                    self.file_ops.write_file(path, content)

                elif cmd == 'delete':
                    if not args:
                        print("Укажите имя файла")
                        continue
                    path = self.process_path_args(args)
                    self.file_ops.delete_file(path)

                elif cmd == 'copy':
                    if len(args) < 2:
                        print("Укажите источник и назначение")
                        continue
                    src = self.process_path_args([args[0]])
                    dest = self.process_path_args(args[1:])
                    self.file_ops.copy_file(src, dest)

                elif cmd == 'move':
                    if len(args) < 2:
                        print("Укажите источник и назначение")
                        continue
                    src = self.process_path_args([args[0]])
                    dest = self.process_path_args(args[1:])
                    self.file_ops.move_file(src, dest)

                elif cmd == 'rename':
                    if len(args) < 2:
                        print("Укажите старое и новое имя")
                        continue
                    old = self.process_path_args([args[0]])
                    new = self.process_path_args(args[1:])
                    self.file_ops.rename_file(old, new)

                elif cmd == 'zip':
                    if len(args) < 2:
                        print("Укажите файлы и имя архива")
                        continue
                    files = [self.process_path_args([f]) for f in args[:-1]]
                    archive = self.process_path_args(args[-1:])
                    self.file_ops.zip_files(files, archive)

                elif cmd == 'unzip':
                    if not args:
                        print("Укажите архив")
                        continue
                    archive = self.process_path_args([args[0]])
                    target = self.process_path_args(args[1:]) if len(args) > 1 else None
                    self.file_ops.unzip_file(archive, target)

                elif cmd == 'search':
                    if not args:
                        print("Укажите шаблон поиска")
                        continue
                    search_dir = self.process_path_args(args[1:]) if len(args) > 1 else None
                    self.file_ops.search_files(args[0], search_dir)

                elif cmd == 'quota':
                    self.show_quota()

                else:
                    print(f"Неизвестная команда: {cmd}. Введите 'help' для справки")

            except Exception as e:
                print(f"Ошибка: {str(e)}")

    def split_command(self, input_str):
        """Умное разделение команд с сохранением любых пробелов в путях"""
        parts = []
        current_part = []
        in_quotes = False
        quote_char = None

        for char in input_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ' ' and not in_quotes:
                if current_part:
                    parts.append(''.join(current_part))
                    current_part = []
            else:
                current_part.append(char)

        if current_part:
            parts.append(''.join(current_part))

        return parts