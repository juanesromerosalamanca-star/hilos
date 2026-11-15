import socket
import threading

HOST = '127.0.0.1'
PORT = 5000


clientes = {}
lock_registro = threading.Lock()

def transmitir_mensaje(mensaje, origen_socket=None):
    with lock_registro:
        
        destinatarios = [(sock, lock_envio) for sock, (nombre, lock_envio) in clientes.items()]

    for sock, lock_envio in destinatarios:
        if sock != origen_socket:
            try:
                with lock_envio:
                    sock.sendall(mensaje.encode('utf-8'))
            except ConnectionError:
                pass

def atender_cliente(conn, addr):
    lock_envio = threading.Lock()
    nombre_usuario = ""
    
    try:
       
        conn.sendall("Ingrese su nombre de usuario: \n".encode('utf-8'))
        nombre_raw = conn.recv(1024).decode('utf-8').strip()
        if not nombre_raw:
            conn.close()
            return
        
        nombre_usuario = nombre_raw.capitalize()
        
        with lock_registro:
            clientes[conn] = (nombre_usuario, lock_envio)
            
        print(f"[CONEXIÓN] {nombre_usuario} conectado desde {addr}")
        transmitir_mensaje(f"*** {nombre_usuario} ha entrado al chat ***\n", origen_socket=conn)

    
        while True:
            datos = conn.recv(1024)
            if not datos:
                break
            
            texto = datos.decode('utf-8').strip()
            
            if texto == "/salir":
                break
            
            elif texto == "/usuarios":
              
                with lock_registro:
                    nombres = sorted([nombre for nombre, _ in clientes.values()])
                
                
                lista_str = "Usuarios conectados: " + ", ".join(nombres) + "\n"
                
                
                with lock_envio:
                    conn.sendall(lista_str.encode('utf-8'))
            
            else:
                msg_formateado = f"{nombre_usuario}: {texto}\n"
                transmitir_mensaje(msg_formateado, origen_socket=conn)

    except ConnectionError:
        pass
    finally:
        with lock_registro:
            if conn in clientes:
                del clientes[conn]
        conn.close()
        if nombre_usuario:
            print(f"[DESCONEXIÓN] {nombre_usuario} se ha desconectado.")
            transmitir_mensaje(f"*** {nombre_usuario} ha salido del chat ***\n")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[INICIADO] Servidor escuchando en {HOST}:{PORT}")
    
    while True:
        conn, addr = servidor.accept()
        hilo = threading.Thread(target=atender_cliente, args=(conn, addr))
        hilo.daemon = True
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()