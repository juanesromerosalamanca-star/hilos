import threading
import time

inventario = 1
ventas_aprobadas = 0
lock = threading.Lock()

def caja_sin_lock(id_caja, barrera):
    global inventario, ventas_aprobadas
    # Lectura del saldo
    saldo_visto = inventario
    
    # Sincronización previa a la decisión final
    barrera.wait()
    
    # Condición de carrera intencional
    if saldo_visto > 0:
        time.sleep(0.01) # Simula retraso en el procesamiento
        ventas_aprobadas += 1
        inventario -= 1
        print(f"Caja {id_caja}: Venta APROBADA (Versión sin Lock)")
    else:
        print(f"Caja {id_caja}: Venta RECHAZADA (Versión sin Lock)")

def caja_con_lock(id_caja):
    global inventario, ventas_aprobadas
    with lock:
        # Verificación y descuento dentro de la misma sección crítica
        if inventario > 0:
            inventario -= 1
            ventas_aprobadas += 1
            print(f"Caja {id_caja}: Venta APROBADA (Versión con Lock)")
        else:
            print(f"Caja {id_caja}: Venta RECHAZADA (Versión con Lock)")

def probar_sin_lock():
    global inventario, ventas_aprobadas
    inventario = 1
    ventas_aprobadas = 0
    barrera = threading.Barrier(2)
    
    hilo1 = threading.Thread(target=caja_sin_lock, args=(1, barrera))
    hilo2 = threading.Thread(target=caja_sin_lock, args=(2, barrera))
    
    hilo1.start()
    hilo2.start()
    hilo1.join()
    hilo2.join()
    
    print(f"[Sin Lock] Ventas aprobadas: {ventas_aprobadas} | Inventario final: {inventario}\n")

def probar_con_lock():
    global inventario, ventas_aprobadas
    inventario = 1
    ventas_aprobadas = 0
    
    hilo1 = threading.Thread(target=caja_con_lock, args=(1,))
    hilo2 = threading.Thread(target=caja_con_lock, args=(2,))
    
    hilo1.start()
    hilo2.start()
    hilo1.join()
    hilo2.join()
    
    print(f"[Con Lock] Ventas aprobadas: {ventas_aprobadas} | Inventario final: {inventario}")
    
    # Verificaciones requeridas por el taller
    assert ventas_aprobadas == 1, f"Error: Se aprobaron {ventas_aprobadas} ventas en lugar de 1."
    assert inventario == 0, f"Error: El inventario final es {inventario} en lugar de 0."
    print(">> Aserciones de verificación pasadas exitosamente.\n")

if __name__ == "__main__":
    print("=== PRUEBA 1: VERSIÓN SIN LOCK (RACE CONDITION) ===")
    probar_sin_lock()
    
    print("=== PRUEBA 2: VERSIÓN CORREGIDA CON LOCK ===")
    probar_con_lock()