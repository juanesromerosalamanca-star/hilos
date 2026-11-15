import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 5000

def recibir_mensajes(sock):
    while True:
        try:
            datos = sock.recv(1024)
            if not datos:
                print("\n[INFO] Conexión cerrada por el servidor.")
                break
            print(datos.decode('utf-8'), end='')
        except ConnectionError:
            break
    sys.exit()

def iniciar_cliente():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except Exception as e:
        print(f"No se pudo conectar al servidor: {e}")
        return

    # Hilo secundario para escuchar datos entrantes
    hilo_receptor = threading.Thread(target=recibir_mensajes, args=(client_socket,))
    hilo_receptor.daemon = True
    hilo_receptor.start()

    # Hilo principal para enviar datos
    try:
        while True:
            mensaje = input()
            client_socket.sendall((mensaje + "\n").encode('utf-8'))
            if mensaje.strip() == "/salir":
                break
    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()

if __name__ == "__main__":
    iniciar_cliente()