import socket


def run_client(host='127.0.0.1', port=12346):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        print(f"UDP клиент готов к отправке на {host}:{port}")

        while True:
            message = input("Введите сообщение (или 'exit'): ")
            if message.lower() == 'exit':
                break

            sock.sendto(message.encode('utf-8'), (host, port))
            data, _ = sock.recvfrom(1024)
            print(f"Ответ сервера: {data.decode('utf-8')}")


if __name__ == "__main__":
    run_client()