import socket
from utils.crypto_utils import *


def run_client(host='127.0.0.1', port=12348):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print(f"Подключено к защищенному серверу {host}:{port}")

        parameters = generate_dh_parameters()
        private_key, public_key = generate_dh_key_pair(parameters)

        server_key_length = int.from_bytes(sock.recv(4), 'big')
        server_public_key = deserialize_public_key(sock.recv(server_key_length))

        serialized_public = serialize_public_key(public_key)
        sock.sendall(len(serialized_public).to_bytes(4, 'big'))
        sock.sendall(serialized_public)

        shared_key = derive_shared_key(private_key, server_public_key)
        print("Установлено безопасное соединение с сервером")

        while True:
            message = input("Введите сообщение (или 'exit'): ")
            if message.lower() == 'exit':
                break

            encrypted_message = encrypt_message(shared_key, message)
            sock.sendall(len(encrypted_message).to_bytes(4, 'big'))
            sock.sendall(encrypted_message)

            encrypted_length = int.from_bytes(sock.recv(4), 'big')
            encrypted_response = sock.recv(encrypted_length)
            response = decrypt_message(shared_key, encrypted_response)
            print(f"Ответ сервера: {response}")


if __name__ == "__main__":
    run_client()