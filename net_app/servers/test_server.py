import socket
import threading
import selectors
import time
from concurrent.futures import ThreadPoolExecutor
from utils.crypto_utils import *


class TestServer:
    def __init__(self):
        self.servers = {
            'tcp_threaded': {'port': 12345, 'running': False},
            'udp': {'port': 12346, 'running': False},
            'selector': {'port': 12347, 'running': False},
            'secure': {'port': 12348, 'running': False}
        }

    def start_tcp_threaded(self):
        def handler(conn, addr):
            with conn:
                print(f"[TCP] Подключён клиент {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        print(f"[TCP] Клиент {addr} отключился")
                        break
                    conn.sendall(data)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.servers['tcp_threaded']['port']))
            s.listen()
            self.servers['tcp_threaded']['running'] = True
            print(f"Многопоточный TCP сервер запущен на порту {self.servers['tcp_threaded']['port']}")

            with ThreadPoolExecutor(max_workers=10) as executor:
                while self.servers['tcp_threaded']['running']:
                    conn, addr = s.accept()
                    executor.submit(handler, conn, addr)

    def start_udp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', self.servers['udp']['port']))
            self.servers['udp']['running'] = True
            print(f"UDP сервер запущен на порту {self.servers['udp']['port']}")

            while self.servers['udp']['running']:
                data, addr = s.recvfrom(1024)
                print(f"[UDP] Получено сообщение от {addr}")
                s.sendto(data, addr)

    def start_selector(self):
        sel = selectors.DefaultSelector()

        def accept(sock):
            conn, addr = sock.accept()
            print(f"[Селектор] Подключён клиент {addr}")
            conn.setblocking(False)
            sel.register(conn, selectors.EVENT_READ, read)

        def read(conn):
            data = conn.recv(1024)
            if data:
                conn.send(data)
            else:
                addr = conn.getpeername()
                print(f"[Селектор] Клиент {addr} отключился")
                sel.unregister(conn)
                conn.close()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.servers['selector']['port']))
            s.listen()
            s.setblocking(False)
            sel.register(s, selectors.EVENT_READ, accept)
            self.servers['selector']['running'] = True
            print(f"Сервер с селекторами запущен на порту {self.servers['selector']['port']}")

            while self.servers['selector']['running']:
                events = sel.select(timeout=1)
                for key, _ in events:
                    callback = key.data
                    callback(key.fileobj)

    def start_secure(self):
        def secure_handler(conn, addr):
            try:
                print(f"\n[Защищённый] Новое подключение от {addr}")

                # 1. Получаем публичный ключ клиента
                client_public_key = deserialize_public_key(conn.recv(4096))

                # 2. Генерируем свою ключевую пару
                private_key, public_key = generate_dh_key_pair()
                conn.sendall(serialize_public_key(public_key))

                # 3. Вычисляем общий ключ
                shared_key = derive_shared_key(private_key, client_public_key)
                print(f"[Защищённый] Общий ключ с {addr} установлен")

                # Обработка сообщений
                while True:
                    encrypted = conn.recv(4096)
                    if not encrypted:
                        break

                    # Дешифровка
                    message = decrypt_message(shared_key, encrypted)
                    print(f"[Защищённый] Получено от {addr}: {message}")

                    # Шифровка ответа
                    response = encrypt_message(shared_key, f"ECHO: {message}")
                    conn.sendall(response)

            except Exception as e:
                print(f"[Защищённый] Ошибка: {str(e)}")
            finally:
                conn.close()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', self.servers['secure']['port']))
            s.listen()
            self.servers['secure']['running'] = True
            print(f"Защищённый сервер запущен на порту {self.servers['secure']['port']}")

            while self.servers['secure']['running']:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=secure_handler, args=(conn, addr)).start()
                except Exception as e:
                    if self.servers['secure']['running']:
                        print(f"Ошибка accept: {str(e)}")

    def start_all(self):
        # Запуск всех серверов
        servers = [
            threading.Thread(target=self.start_tcp_threaded),
            threading.Thread(target=self.start_udp),
            threading.Thread(target=self.start_selector),
            threading.Thread(target=self.start_secure)
        ]

        for s in servers:
            s.daemon = True
            s.start()

        print("Все серверы успешно запущены:")
        print(f"- TCP (многопоточный) на порту {self.servers['tcp_threaded']['port']}")
        print(f"- UDP на порту {self.servers['udp']['port']}")
        print(f"- TCP (селекторы) на порту {self.servers['selector']['port']}")
        print(f"- Защищенный TCP на порту {self.servers['secure']['port']}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nОстановка всех серверов...")
            for s in self.servers.values():
                s['running'] = False


if __name__ == "__main__":
    server = TestServer()
    server.start_all()