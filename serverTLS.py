import socket
import threading
import base64
from cryptography.fernet import Fernet

archivos = ["archivo1.txt", "archivo2.txt", "archivo3.txt"]

SERVER_IP = "127.0.0.1"
SERVER_PORT = 20001
BUFFER_SIZE = 1024
TIMEOUT = 2

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Servidor UDP iniciado en {SERVER_IP}:{SERVER_PORT}")

clientes = {}

# ----------------------------
# Función de cifrado
# ----------------------------
def generar_clave():
    return Fernet.generate_key()

def manejar_cliente(addr, archivo, puerto_cliente, clave):
    fernet = Fernet(clave)
    print(f"[+] Iniciando transferencia cifrada a {addr} con archivo {archivo}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((SERVER_IP, puerto_cliente))

    try:
        with open(archivo, "r") as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"Archivo {archivo} no encontrado.")
        return

    seq_num = 0
    for linea in lineas:
        ack_recibido = False
        while not ack_recibido:
            mensaje = f"{seq_num}|{linea.strip()}".encode()
            mensaje_cifrado = fernet.encrypt(mensaje)

            client_socket.sendto(mensaje_cifrado, addr)
            print(f"[Servidor → {addr}] Cifrado: {mensaje_cifrado}")
            print(f"[Servidor] Original: {mensaje.decode()}")

            client_socket.settimeout(TIMEOUT)
            try:
                data, _ = client_socket.recvfrom(BUFFER_SIZE)
                if data.decode() == f"ACK{seq_num}":
                    print(f"[Servidor] ACK{seq_num} recibido de {addr}")
                    ack_recibido = True
                    seq_num += 1
            except socket.timeout:
                print(f"[Servidor] Timeout esperando ACK{seq_num}, retransmitiendo...")

    client_socket.sendto(fernet.encrypt("FIN".encode()), addr)
    print(f"[Servidor] Transferencia finalizada para {addr}")
    client_socket.close()


def esperar_clientes():
    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        mensaje = data.decode()

        if mensaje == "SYN":
            print(f"[Servidor] Solicitud de conexión (SYN) de {addr}")
            server_socket.sendto("SYN-ACK".encode(), addr)

        elif mensaje == "ACK":
            if addr not in clientes and len(clientes) < len(archivos):
                puerto_cliente = 30000 + len(clientes)
                archivo = archivos[len(clientes)]

                # 🔹 Handshake TLS simulado: generar clave
                clave = generar_clave()
                clientes[addr] = (archivo, puerto_cliente, clave)

                # Enviar algoritmo y clave compartida
                server_socket.sendto(f"TLS-AES|{clave.decode()}".encode(), addr)

                print(f"[Servidor] Conexión segura con {addr}, clave de sesión generada.")

                threading.Thread(
                    target=manejar_cliente,
                    args=(addr, archivo, puerto_cliente, clave)
                ).start()


if __name__ == "__main__":
    esperar_clientes()