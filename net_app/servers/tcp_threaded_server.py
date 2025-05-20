import socket
import threading


def handle_client(conn, addr):
    with conn:
        print(f"Подключен клиент {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"[{addr}] Получено: {message}")
            conn.sendall(data)
        print(f"Клиент {addr} отключен")


def run_server(host='127.0.0.1', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Многопоточный сервер запущен на {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"Активных подключений: {threading.active_count() - 1}")


if __name__ == "__main__":
    run_server()