import socket
from cryptography.fernet import Fernet

SERVER_IP = "127.0.0.1"
SERVER_PORT = 20001
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(2.0)

# Handshake 3 vías
client_socket.sendto("SYN".encode(), (SERVER_IP, SERVER_PORT))
print("[Cliente] Enviado: SYN")

data, _ = client_socket.recvfrom(BUFFER_SIZE)
if data.decode() == "SYN-ACK":
    print("[Cliente] Recibido: SYN-ACK")
    client_socket.sendto("ACK".encode(), (SERVER_IP, SERVER_PORT))
    print("[Cliente] Enviado: ACK")
else:
    print("[Cliente] Error en handshake")
    exit()

# 🔹 Recibir algoritmo y clave
data, _ = client_socket.recvfrom(BUFFER_SIZE)
info = data.decode().split("|")
if info[0].startswith("TLS"):
    algoritmo, clave = info
    print(f"[Cliente] Handshake TLS → Algoritmo: {algoritmo}, Clave recibida: {clave}")
    fernet = Fernet(clave.encode())
else:
    print("[Cliente] Error en TLS handshake")
    exit()

# ----------------------------
# Recepción de archivo cifrado
# ----------------------------
archivo_recibido = []

while True:
    try:
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        try:
            mensaje = fernet.decrypt(data).decode()
        except Exception:
            print("[Cliente] Error al descifrar mensaje")
            continue

        if mensaje == "FIN":
            print("[Cliente] Archivo recibido completamente.")
            break

        seq, contenido = mensaje.split("|", 1)
        seq = int(seq)

        print(f"[Cliente] Recibido (cifrado): {data}")
        print(f"[Cliente] Descifrado SEQ{seq}: {contenido}")

        archivo_recibido.append(contenido)

        ack = f"ACK{seq}"
        client_socket.sendto(ack.encode(), (SERVER_IP, SERVER_PORT))
        print(f"[Cliente] Enviado: {ack}")

    except socket.timeout:
        print("[Cliente] Timeout esperando datos")
        break

# Guardar archivo
if archivo_recibido:
    with open("copia_cliente_tls.txt", "w") as f:
        for linea in archivo_recibido:
            f.write(linea + "\n")
    print("[Cliente] Archivo guardado como copia_cliente_tls.txt")
else:
    print("[Cliente] No se recibió ningún archivo")

client_socket.close()