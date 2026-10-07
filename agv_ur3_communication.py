import socket

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(1)

print(f"Servidor escuchando en el puerto {PORT}...")
print("Esperando conexión del UR3...")

conn, addr = server.accept()

print(f"UR3 conectado desde {addr}")

try:

    datos = conn.recv(1024)

    if datos:
        mensaje = datos.decode().strip()
        print(f"Mensaje recibido del UR3: {mensaje}")

    # wait till typing q
    while True:
        mensaje = input("Escribe 'q' para continuar: ")

        if mensaje.lower() == "q":
            conn.sendall(b"q")
            print("Se envió 'q' al UR3")
            break

finally:
    conn.close()
    server.close()
    print("Conexión cerrada.")