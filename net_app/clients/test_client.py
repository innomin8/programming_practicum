import socket
import time
import statistics
from utils.crypto_utils import *


def test_tcp_client(host, port, messages=10):
    print(f"\nТестируем TCP сервер на порту {port}")
    delays = []
    for i in range(messages):
        start = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            msg = f"Сообщение {i + 1}"
            s.sendall(msg.encode())
            data = s.recv(1024)
            print(f"Получен ответ: {data.decode()}")
        delays.append(time.time() - start)
    return delays


def test_udp_client(host, port, messages=10):
    print(f"\nТестируем UDP сервер на порту {port}")
    delays = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        for i in range(messages):
            start = time.time()
            msg = f"Сообщение {i + 1}"
            s.sendto(msg.encode(), (host, port))
            data, _ = s.recvfrom(1024)
            print(f"Получен ответ: {data.decode()}")
            delays.append(time.time() - start)
    return delays


def test_secure_client(host, port, messages=3):
    print(f"\n=== Тестируем защищённый сервер на порту {port} ===")
    delays = []

    try:
        # 1. Установка TCP соединения
        print("[1/4] Установка TCP-соединения...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect((host, port))

        # 2. Генерация ключевой пары
        print("[2/4] Генерация ключей DH...")
        private_key, public_key = generate_dh_key_pair()

        # 3. Обмен публичными ключами
        print("[3/4] Обмен публичными ключами...")
        sock.sendall(serialize_public_key(public_key))
        peer_key = deserialize_public_key(sock.recv(4096))

        # 4. Вычисление общего ключа
        print("[4/4] Вычисление общего секрета...")
        shared_key = derive_shared_key(private_key, peer_key)
        print("✓ Безопасное соединение установлено")

        # Тестовая передача данных
        for i in range(1, messages + 1):
            try:
                msg = f"SECURE_TEST_{i}"
                print(f"\nОтправка сообщения {i}: {msg}")

                # Полное время обработки
                start_time = time.perf_counter()

                # Шифрование
                encrypted = encrypt_message(shared_key, msg)
                sock.sendall(encrypted)

                # Получение ответа
                response = sock.recv(4096)
                decrypted = decrypt_message(shared_key, response)

                total_time = time.perf_counter() - start_time
                delays.append(total_time)

                print(f"Получен ответ: {decrypted}")
                print(f"Время обработки: {total_time:.6f} сек")

                time.sleep(0.5)  # Пауза между сообщениями

            except Exception as e:
                print(f"Ошибка при обработке сообщения: {str(e)}")
                break

    except Exception as e:
        print(f"\n✗ Критическая ошибка: {str(e)}")
        traceback.print_exc()
        return [0.0] * messages  # Возвращаем заполненный список

    finally:
        sock.close()

    return delays


def print_stats(name, delays):
    print(f"\nРезультаты для {name}:")
    print(f"  Средняя задержка: {statistics.mean(delays):.4f} сек")
    print(f"  Максимальная: {max(delays):.4f} сек")
    print(f"  Минимальная: {min(delays):.4f} сек")
    if len(delays) > 1:
        print(f"  Отклонение: {statistics.stdev(delays):.4f} сек")


def run_tests(host='127.0.0.1'):
    servers = {
        'TCP Многопоточный': 12345,
        'UDP': 12346,
        'TCP Селекторы': 12347,
        'Защищённый TCP': 12348
    }

    print("=== Начало тестирования серверов ===")

    # Тестируем обычные серверы
    tcp_delays = test_tcp_client(host, servers['TCP Многопоточный'])
    udp_delays = test_udp_client(host, servers['UDP'])
    selector_delays = test_tcp_client(host, servers['TCP Селекторы'])
    secure_delays = test_secure_client(host, servers['Защищённый TCP'])

    # Выводим статистику
    print_stats("TCP Многопоточный", tcp_delays)
    print_stats("UDP", udp_delays)
    print_stats("TCP с селекторами", selector_delays)
    print_stats("Защищённый TCP", secure_delays)

    print("\n=== Тестирование завершено ===")


if __name__ == "__main__":
    run_tests()