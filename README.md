# Hilos y Concurrencia en Python

**Asignatura:** Informática 2  
**Integrantes:** Juan Esteban Romero Salamanca – Oscar Steven Chaves Diaz  
**Fecha:** 13 de noviembre de 2026  

## 📂 Archivos Entregados

* `sensores.py`: Simulación y medición de tiempos de lectura secuencial vs. concurrente.
* `inventario.py`: Demostración de condición de carrera (*race condition*) y su resolución mediante `Lock`.
* `servidor_chat.py`: Servidor de chat TCP concurrente con soporte para el comando `/usuarios`.

---

## 1. Consultas a Sensores (`sensores.py`)

### 1.1 Predicción de Tiempos
Considerando los tiempos de respuesta **A = 1,0 s**, **B = 2,0 s** y **C = 1,5 s**, y un costo despreciable al crear cada hilo:

* **Modo Secuencial:** Las esperas se suman ($1,0 + 2,0 + 1,5 = 4,5\text{ s}$). Orden de finalización: `A, B, C`.
* **Iniciar todos los hilos y después esperarlos:** Las esperas se solapan, por lo que el tiempo total lo determina el sensor más lento ($\max(1,0;\ 2,0;\ 1,5) = 2,0\text{ s}$). Orden de finalización: `A (1,0 s), C (1,5 s), B (2,0 s)`.
* **Ejecutar `join()` después de cada `start()`:** Cada hilo termina antes de iniciar el siguiente, anulando el solapamiento ($4,5\text{ s}$). Orden de finalización: `A, B, C`.

### 1.2 Tabla Comparativa de Tiempos
Cada modo se ejecutó tres veces registrando la mediana con `time.perf_counter()` desde antes de la primera lectura o creación de hilos hasta la finalización de las tres lecturas:

| Modo | Tiempo previsto | Mediana medida |
| :--- | :---: | :---: |
| Secuencial, con llamadas directas | 4,5 s | 4,5010 s |
| Iniciar todos los hilos y después esperarlos | 2,0 s | 2,0008 s |
| Ejecutar `join()` después de cada `start()` | 4,5 s | 4,5019 s |

### 1.3 Marcas de Tiempo (Logs de Ejecución)

**Iniciar todos los hilos y después esperarlos:**
```text
[0.00s] Sensor A: Inicio de lectura
[0.00s] Sensor B: Inicio de lectura
[0.00s] Sensor C: Inicio de lectura
[1.00s] Sensor A: Fin de lectura
[1.50s] Sensor C: Fin de lectura
[2.00s] Sensor B: Fin de lectura
```

**Ejecutar `join()` después de cada `start()`:**
```text
[0.00s] Sensor A: Inicio de lectura
[1.00s] Sensor A: Fin de lectura
[1.00s] Sensor B: Inicio de lectura
[3.00s] Sensor B: Fin de lectura
[3.00s] Sensor C: Inicio de lectura
[4.50s] Sensor C: Fin de lectura
```

### 1.4 Diferencia entre los dos usos de `join()`
Las predicciones se cumplieron con una desviación menor a 2 ms debida a la creación de hilos e impresión en consola:

1. **Concurrencia real (`start()` masivo seguido de `join()`):** Los tres sensores arrancan en `0,00 s` y sus tiempos de espera se solapan, logrando un tiempo total de `2,0 s`.
2. **Ejecución secuencial disfrazada (`join()` tras cada `start()`):** `join()` bloquea el hilo principal hasta que el hilo recién creado finaliza. El sensor B no inicia hasta `1,00 s` y el C hasta `3,00 s`, sumando `4,5 s` sin obtener concurrencia.

---

## 2. Dos Cajas, Una Unidad (`inventario.py`)

### 2.1 Versión sin `Lock` (Condición de Carrera)
Cada caja lee el saldo inicial (`1`) y espera en una `Barrier(2)` fuera de cualquier sección crítica, provocando que ambas aprueben la venta antes de descontar del inventario:

```text
=== PRUEBA 1: VERSIÓN SIN LOCK (RACE CONDITION) ===
Caja 1: Venta APROBADA (Versión sin Lock)
Caja 2: Venta APROBADA (Versión sin Lock)
[Sin Lock] Ventas aprobadas: 2 | Inventario final: -1
```

* **Resultado:** Se aprobaron 2 ventas de una sola unidad disponible, dejando el inventario en un estado inválido (`-1`). *(Nota: en algunas ejecuciones los mensajes de `print()` también se entremezclan al competir por la salida estándar).*

### 2.2 Versión Corregida con `Lock`
La verificación del saldo, el descuento y el registro de la venta se agrupan dentro de la misma sección crítica (`with lock:`), eliminando la barrera:

```text
=== PRUEBA 2: VERSIÓN CORREGIDA CON LOCK ===
Caja 1: Venta APROBADA (Versión con Lock)
Caja 2: Venta RECHAZADA (Versión con Lock)
[Con Lock] Ventas aprobadas: 1 | Inventario final: 0
>> Aserciones de verificación pasadas exitosamente.
```

Tras ejecutar `join()` en ambos hilos, las aserciones `assert ventas_aprobadas == 1` y `assert inventario == 0` se cumplen de forma consistente en múltiples ejecuciones.

### 2.3 ¿Por qué proteger solo el descuento sería insuficiente?
El problema radica en tomar decisiones con datos obsoletos bajo un patrón **comprobar y luego actuar (*check-then-act*)**. Si el `Lock` protegiera únicamente `inventario -= 1`, ambas cajas podrían leer `saldo = 1` simultáneamente, aprobar la venta y ejecutar las restas una tras otra, llevando nuevamente el inventario a `-1`. La comprobación (`if inventario > 0`) y la modificación deben ejecutarse como una **operación atómica** dentro del mismo bloque `with lock:`.

---

## 3. Lista de Participantes en el Chat TCP (`servidor_chat.py`)

### 3.1 Implementación del Comando `/usuarios`
El servidor intercepta `/usuarios`, extrae una copia ordenada alfabéticamente de los nombres activos bajo `lock_registro`, libera el candado y envía la respuesta únicamente al cliente solicitante usando su `lock_envio`:

```python
elif texto == "/usuarios":
    with lock_registro:
        nombres = sorted([nombre for nombre, _ in clientes.values()])
    lista_str = "Usuarios conectados: " + ", ".join(nombres) + "\n"
    with lock_envio:
        conn.sendall(lista_str.encode('utf-8'))
```

### 3.2 Registro de Terminal de la Prueba
Prueba realizada con un servidor y tres clientes (`Ana`, `Luis` y `María`, normalizados con `.capitalize()`). Ana nunca envió un mensaje público normal:

```text
[SERVIDOR] [INICIADO] Servidor escuchando en 127.0.0.1:5000
[ANA] Ingrese su nombre de usuario:
--- ANA escribe: Ana
[SERVIDOR] [CONEXIÓN] Ana conectado desde ('127.0.0.1', 44136)
[LUIS] Ingrese su nombre de usuario:
--- LUIS escribe: Luis
[SERVIDOR] [CONEXIÓN] Luis conectado desde ('127.0.0.1', 44142)
[ANA] *** Luis ha entrado al chat ***
[MARIA] Ingrese su nombre de usuario:
--- MARIA escribe: maría
[SERVIDOR] [CONEXIÓN] María conectado desde ('127.0.0.1', 44150)
[ANA] *** María ha entrado al chat ***
[LUIS] *** María ha entrado al chat ***

--- LUIS escribe: Hola a todos
[MARIA] Luis: Hola a todos
[ANA] Luis: Hola a todos

--- ANA escribe: /usuarios
[ANA] Usuarios conectados: Ana, Luis, María

--- LUIS escribe: /salir
[SERVIDOR] [DESCONEXIÓN] Luis se ha desconectado.
[MARIA] *** Luis ha salido del chat ***
[ANA] *** Luis ha salido del chat ***

--- ANA escribe: /usuarios
[ANA] Usuarios conectados: Ana, María
```

**Verificaciones cumplidas:**
1. Ana recibió los mensajes de difusión sin haber escrito previamente.
2. La salida de `/usuarios` se mostró únicamente en la terminal de Ana.
3. Tras `/salir`, se notificó a los demás clientes y la lista se actualizó automáticamente.
4. Los nombres se despliegan ordenados alfabéticamente.

### 3.3 Recepción asíncrona en el cliente
En `cliente_chat.py`, el hilo principal queda bloqueado esperando la entrada del usuario mediante `input()`. De forma paralela, un hilo secundario en modo *daemon* (`hilo_receptor` ejecutando `recibir_mensajes`) mantiene un bucle continuo sobre `sock.recv(1024)` para imprimir los mensajes entrantes en tiempo real sin depender de que el usuario envíe texto.

### 3.4 ¿Por qué el envío ocurre fuera del candado del registro?
* **Evitar bloquear el servidor por red:** `sendall()` es una operación de E/S bloqueante. Si un cliente tiene una conexión lenta o su búfer lleno mientras se retiene `lock_registro`, ningún otro hilo podría registrar usuarios, desconectarlos o hacer *broadcast*.
* **Minimizar el alcance del candado:** `lock_registro` solo debe proteger el acceso al diccionario `clientes` durante el instante en que se copian los nombres a una lista local.
* **Prevenir interbloqueos (*deadlocks*) y mezcla de bytes:** Al tomar `lock_envio` fuera de `lock_registro`, se evita el anidamiento de candados en distinto orden entre hilos. Además, `lock_envio` garantiza que la respuesta de `/usuarios` y un mensaje de difusión simultáneo no mezclen sus bytes en el mismo socket.

---

## 📌 Conclusiones

* Los hilos permiten solapar tiempos de espera (E/S o `sleep`), reduciendo el tiempo total de ejecución de la suma de tareas al máximo individual; llamar a `join()` inmediatamente tras `start()` anula este beneficio.
* Las condiciones de carrera ocurren cuando la lectura y actualización de un recurso compartido no son atómicas, lo cual se resuelve encapsulando ambas acciones dentro de un mismo `Lock`.
* En servidores concurrentes, los candados deben retenerse el menor tiempo posible y nunca mantenerse activos durante operaciones bloqueantes de red.
````[cite: 1]
