from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

# Фиксированные параметры (RFC 3526 - 2048-bit Group)
DH_PRIME = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16
)
DH_GENERATOR = 2


def generate_dh_parameters():
    return dh.DHParameterNumbers(DH_PRIME, DH_GENERATOR).parameters(default_backend())


def generate_dh_key_pair():
    parameters = generate_dh_parameters()
    private_key = parameters.generate_private_key()
    return private_key, private_key.public_key()


def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def deserialize_public_key(serialized_key):
    try:
        return serialization.load_pem_public_key(
            serialized_key,
            backend=default_backend()
        )
    except Exception as e:
        print(f"[ОШИБКА] Не удалось загрузить публичный ключ: {str(e)}")
        raise


def derive_shared_key(private_key, peer_public_key):
    try:
        # Проверка совместимости параметров
        if (private_key.parameters().parameter_numbers().p !=
                peer_public_key.parameters().parameter_numbers().p):
            raise ValueError("Параметры DH не совпадают (разные простые числа)")

        if (private_key.parameters().parameter_numbers().g !=
                peer_public_key.parameters().parameter_numbers().g):
            raise ValueError("Параметры DH не совпадают (разные генераторы)")

        # Вычисление общего ключа
        shared_key = private_key.exchange(peer_public_key)
        return shared_key[:32]  # Используем первые 32 байта для AES-256

    except Exception as e:
        print(f"[ОШИБКА] Ошибка обмена ключами: {str(e)}")
        print("Параметры локального ключа:", private_key.parameters().parameter_numbers())
        print("Параметры удалённого ключа:", peer_public_key.parameters().parameter_numbers())
        raise


def encrypt_message(key, message):
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return iv + encryptor.update(padded_data) + encryptor.finalize()


def decrypt_message(key, encrypted_data):
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(padded_data) + unpadder.finalize()).decode()