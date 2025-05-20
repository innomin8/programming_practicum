import socket


def run_client(host='127.0.0.1', port=12347):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(5)
        sock.connect((host, port))
        print(f"Подключено к серверу {host}:{port}")

        while True:
            message = input("Введите сообщение (или 'exit'): ")
            if message.lower() == 'exit':
                break

            sock.sendall(message.encode('utf-8'))
            data = sock.recv(1024)
            print(f"Ответ сервера: {data.decode('utf-8')}")


if __name__ == "__main__":
    run_client()