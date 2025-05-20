import socket
import threading
from utils.crypto_utils import *


def handle_client(conn, addr):
    try:
        parameters = generate_dh_parameters()
        private_key, public_key = generate_dh_key_pair(parameters)

        serialized_public = serialize_public_key(public_key)
        conn.sendall(len(serialized_public).to_bytes(4, 'big'))
        conn.sendall(serialized_public)

        peer_key_length = int.from_bytes(conn.recv(4), 'big')
        peer_public_key = deserialize_public_key(conn.recv(peer_key_length))

        shared_key = derive_shared_key(private_key, peer_public_key)
        print(f"Установлено безопасное соединение с {addr}")

        while True:
            encrypted_length = int.from_bytes(conn.recv(4), 'big')
            encrypted_data = conn.recv(encrypted_length)

            if not encrypted_data:
                break

            message = decrypt_message(shared_key, encrypted_data)
            print(f"[{addr}] Получено: {message}")

            encrypted_response = encrypt_message(shared_key, f"ECHO: {message}")
            conn.sendall(len(encrypted_response).to_bytes(4, 'big'))
            conn.sendall(encrypted_response)

    except Exception as e:
        print(f"Ошибка с клиентом {addr}: {e}")
    finally:
        conn.close()
        print(f"Соединение с {addr} закрыто")


def run_server(host='127.0.0.1', port=12348):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Защищенный сервер запущен на {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    run_server()