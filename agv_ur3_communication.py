
import socket
import threading
import cv2

# Configuración TCP/IP
HOST = "0.0.0.0"
PORT = 5000

# Control de ejecución
stop_event = threading.Event()


def communication_thread():
    """Comunicación TCP/IP con el UR3."""

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
        server.listen(1)

        print(f"[TCP] Servidor escuchando en el puerto {PORT}")
        print("[TCP] Esperando conexión del UR3...")

        server.settimeout(1.0)

        # Esperar al robot sin bloquear el cierre del programa
        conn = None

        while not stop_event.is_set():
            try:
                conn, addr = server.accept()
                break
            except socket.timeout:
                continue

        if conn is None:
            return

        with conn:
            print(f"[TCP] UR3 conectado desde {addr}")

            conn.settimeout(1.0)
            datos = conn.recv(1024)

            if not datos:
                print("[TCP] El UR3 cerró la conexión.")
                return

            print(
                "[TCP] Mensaje recibido:",
                datos.decode(errors="replace").strip()
            )

            while not stop_event.is_set():
                # input() espera sin detener el hilo de cámara
                mensaje = input("[TCP] Escribe 'q' para continuar: ")

                if mensaje.lower().strip() == "q":
                    conn.sendall(b"q")
                    print("[TCP] Se envió 'q' al UR3.")
                    break

    except (OSError, ConnectionError) as error:
        print(f"[TCP] Error: {error}")

    finally:
        stop_event.set()
        server.close()
        print("[TCP] Comunicación finalizada.")


def camera_thread():
    """Muestra video en vivo utilizando OpenCV."""

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("[CÁMARA] No se pudo abrir la cámara.")
        stop_event.set()
        return

    print("[CÁMARA] Cámara iniciada.")
    print("[CÁMARA] Presiona ESC en la ventana del video para salir.")

    try:
        while not stop_event.is_set():
            ret, frame = camera.read()

            if not ret:
                print("[CÁMARA] No se pudo leer la imagen.")
                break

            cv2.imshow("Camara - Prueba de concurrencia", frame)

            # Permite actualizar la ventana y detectar ESC
            if cv2.waitKey(1) & 0xFF == 27:
                stop_event.set()
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("[CÁMARA] Cámara cerrada.")


if __name__ == "__main__":
    print("Iniciando sistema...\n")

    camera = threading.Thread(
        target=camera_thread,
        name="CameraThread"
    )

    communication = threading.Thread(
        target=communication_thread,
        name="CommunicationThread"
    )

    camera.start()
    communication.start()

    try:
        while camera.is_alive() and communication.is_alive():
            camera.join(timeout=0.2)
            communication.join(timeout=0.2)

    except KeyboardInterrupt:
        stop_event.set()

    finally:
        stop_event.set()
        camera.join()
        communication.join()
        print("Sistema finalizado.")
