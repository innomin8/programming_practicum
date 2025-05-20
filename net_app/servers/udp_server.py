import socket


def run_server(host='127.0.0.1', port=12346):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"UDP сервер запущен на {host}:{port}")

        while True:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Получено от {addr}: {message}")
            sock.sendto(data, addr)


if __name__ == "__main__":
    run_server()