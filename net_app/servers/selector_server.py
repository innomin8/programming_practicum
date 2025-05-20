import socket
import selectors


def accept_connection(server_socket, selector):
    conn, addr = server_socket.accept()
    print(f"Принято подключение от {addr}")
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, read_data)


def read_data(conn, selector):
    addr = conn.getpeername()
    try:
        data = conn.recv(1024)
        if data:
            print(f"Получено от {addr}: {data.decode('utf-8')}")
            conn.send(data)
        else:
            print(f"Соединение с {addr} закрыто")
            selector.unregister(conn)
            conn.close()
    except ConnectionResetError:
        print(f"Клиент {addr} разорвал соединение")
        selector.unregister(conn)
        conn.close()


def run_server(host='127.0.0.1', port=12347):
    selector = selectors.DefaultSelector()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        server_socket.bind((host, port))
        server_socket.listen(5)
        server_socket.setblocking(False)
        selector.register(server_socket, selectors.EVENT_READ, accept_connection)

        print(f"Сервер с селекторами запущен на {host}:{port}")

        while True:
            events = selector.select()
            for key, _ in events:
                callback = key.data
                callback(key.fileobj, selector)


if __name__ == "__main__":
    run_server()