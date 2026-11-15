import time
import threading
from statistics import median

# Tiempos de respuesta requeridos
SENSORES = {
    'A': 1.0,
    'B': 2.0,
    'C': 1.5
}

def leer_sensor(nombre, duracion, start_time):
    t_inicio = time.perf_counter() - start_time
    print(f"[{t_inicio:.2f}s] Sensor {nombre}: Inicio de lectura")
    time.sleep(duracion)
    t_fin = time.perf_counter() - start_time
    print(f"[{t_fin:.2f}s] Sensor {nombre}: Fin de lectura")

def modo_secuencial():
    start_time = time.perf_counter()
    for nombre, duracion in SENSORES.items():
        leer_sensor(nombre, duracion, start_time)
    return time.perf_counter() - start_time

def modo_paralelo_espera_final():
    start_time = time.perf_counter()
    hilos = []
    for nombre, duracion in SENSORES.items():
        hilo = threading.Thread(target=leer_sensor, args=(nombre, duracion, start_time))
        hilos.append(hilo)
        hilo.start()
    
    for hilo in hilos:
        hilo.join()
    return time.perf_counter() - start_time

def modo_paralelo_join_inmediato():
    start_time = time.perf_counter()
    for nombre, duracion in SENSORES.items():
        hilo = threading.Thread(target=leer_sensor, args=(nombre, duracion, start_time))
        hilo.start()
        hilo.join()
    return time.perf_counter() - start_time

def ejecutar_pruebas():
    modos = [
        ("Secuencial, con llamadas directas", modo_secuencial),
        ("Iniciar todos los hilos y después esperarlos", modo_paralelo_espera_final),
        ("Ejecutar join() después de cada start()", modo_paralelo_join_inmediato)
    ]

    print("=== EJECUCIÓN DE EXPERIMENTOS DE SENSORES ===\n")
    for nombre_modo, funcion in modos:
        tiempos = []
        print(f"--- {nombre_modo} ---")
        for i in range(3):
            print(f"Prueba {i+1}:")
            duracion = funcion()
            tiempos.append(duracion)
            print(f"Tiempo medido: {duracion:.4f} s\n")
        
        mediana_medida = median(tiempos)
        print(f">> Mediana obtenida para '{nombre_modo}': {mediana_medida:.4f} s\n" + "="*50)

if __name__ == "__main__":
    ejecutar_pruebas()