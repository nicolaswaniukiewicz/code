import tkinter as tk
import random
import threading
import time

# Configuración de la memoria
MEMORIA_TOTAL = 1000  # Memoria total disponible (en MB)
MEMORIA_USADA = 0  # Memoria actualmente en uso (en MB)
MAX_SWAP = 10  # Máximo número de procesos en swap
TAMANO_PAGINA = 50 # Tamaño de cada página en MB

# Lista de procesos en diferentes estados
procesos = []
procesos_nuevos = []
procesos_listos = []
procesos_bloqueados = []
procesos_swap = []
procesos_terminados = []
paginas_memoria = []
proceso_ejecucion = None

# Actualiza la clase Proceso para manejar paginación
class Proceso:
    def __init__(self, id, memoria):
        self.id = id
        self.memoria = memoria
        self.paginas = [] #paginas asignadas entre proceoso
        self.estado = 'Nuevos'

    def __str__(self): 
        return f"Proceso {self.id}: {self.estado} (Memoria: {self.memoria} MB, Paginas: {len(self.paginas)})"

def asignar_paginas(proceso):
    global MEMORIA_USADA
    paginas_nececsarias = (proceso.memoria + TAMANO_PAGINA - 1) // TAMANO_PAGINA # Redondeo para arriba

    if MEMORIA_USADA + paginas_nececsarias * TAMANO_PAGINA <= MEMORIA_TOTAL:
        for _ in range(paginas_nececsarias):
            paginas_memoria.append(proceso.id) # Asigna páginas al proceso
            proceso.paginas.append(len(paginas_memoria) - 1)
        MEMORIA_USADA += paginas_nececsarias * TAMANO_PAGINA
        return True
    return False

# Modifica la función agregar_proceso
def agregar_proceso(memoria_necesaria):
    proceso = Proceso(len(procesos) + 1, memoria_necesaria)
    if asignar_paginas(proceso):
        procesos_nuevos.append(proceso)
        proceso.append(proceso)
        proceso.estado = 'Nuevos'
    else:
        mensaje_error.config(text= "Mmemoria insuficiente para asignar paginas.")

        actualizar_interfaz
    
# Función para compactar la memoria
def comactar_memoria():
    global MEMORIA_USADA
    paginas_memoria_compactadas = []
    for p in procesos:
        if p.estado in ['Listo', 'Ejecutando', 'Bloqueado']:
            paginas_memoria_compactadas.extend([p.id] * len(p.paginas))
    
    paginas_memoria.clear()
    paginas_memoria.extend(paginas_memoria_compactadas)
    mensaje_error.config(text= "Memoria compactada.")
    actualizar_interfaz()

# Clase para representar un proceso Nuevo
class Proceso:
    def __init__(self, id, memoria):
        self.id = id
        self.memoria = memoria
        self.estado = 'Nuevos'

    def __str__(self):
        return f"Proceso {self.id}: {self.estado} (Memoria: {self.memoria} MB)"
    
# Clase para representar un proceso listo
class Proceso:
    def __init__(self, id, memoria):
        self.id = id
        self.memoria = memoria
        self.estado = 'Listo'
        self.veces_bloqueado = 0  # Nuevo atributo para contar las veces que ha sido bloqueado

    def __str__(self):
        return f"Proceso {self.id}: {self.estado} (Memoria: {self.memoria} MB)"

# Función para crear procesos aleatorios
def crear_procesos_automaticos():
    while True:
        if len(procesos) < 30:  # Máximo 10 procesos simultáneos
            memoria_necesaria = random.randint(50, 200)
            agregar_proceso(memoria_necesaria)
        time.sleep(4)

# Función para agregar un proceso (manual o aleatorio)
def agregar_proceso(memoria_necesaria):
    global MEMORIA_USADA
    proceso = Proceso(len(procesos) + 1, memoria_necesaria)
    
    # Agrega el proceso que se creó a "NUEVO" y a "PROCESOS"
    if MEMORIA_USADA + memoria_necesaria <= MEMORIA_TOTAL:
        procesos_nuevos.append(proceso)
        proceso.estado = 'Nuevos'
        procesos.append(proceso)

    actualizar_interfaz()

# Función para mover un proceso directamente al swap
def mover_a_swap_directo(proceso):
    global MEMORIA_USADA
    if len(procesos_swap) < MAX_SWAP:
        procesos_swap.append(proceso)
        proceso.estado = 'Swap'
        actualizar_interfaz()
    else:
        # Se queda bloqueado si no hay espacio en swap
        proceso.estado = 'Bloqueado'
        procesos_bloqueados.append(proceso)
        actualizar_interfaz()

def nuevo_a_listo():
    global MEMORIA_USADA
    while True:
        for proceso in procesos_nuevos[:]:
            if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL:
                procesos_nuevos.remove(proceso)
                procesos_listos.append(proceso)
                proceso.estado = 'Listo'
                MEMORIA_USADA += proceso.memoria  # Solo suma cuando entra a Listo
                actualizar_interfaz()
            else:
                mensaje_error.config(text="Memoria insuficiente. El proceso se mantiene en Nuevos.")
        time.sleep(3)

# Función para mover procesos bloqueados a listos periódicamente
# Función para mover el proceso con la menor memoria de bloqueado a listo o swap
def mover_a_listo_menor_memoria():
    global MEMORIA_USADA

    if procesos_bloqueados:
        proceso_menor_memoria = min(procesos_bloqueados, key=lambda p: p.memoria)

        # No es necesario verificar MEMORIA_USADA + proceso_menor_memoria.memoria, 
        # ya que el proceso bloqueado está usando su 100% de memoria.

        procesos_bloqueados.remove(proceso_menor_memoria)
        procesos_listos.append(proceso_menor_memoria)
        proceso_menor_memoria.estado = 'Listo'
        actualizar_interfaz()

def mover_a_listo_mayor_memoria():
    global MEMORIA_USADA

    if procesos_bloqueados:
        # Ahora se usa max para seleccionar el proceso de mayor memoria
        proceso_mayor_memoria = max(procesos_bloqueados, key=lambda p: p.memoria)

        procesos_bloqueados.remove(proceso_mayor_memoria)
        procesos_listos.append(proceso_mayor_memoria)
        proceso_mayor_memoria.estado = 'Listo'
        actualizar_interfaz()


# Función para mover procesos bloqueados a listos periódicamente
def mover_bloqueados_a_listos():
    while True:
        time.sleep(3)  # Cada 3 segundos
        mover_a_listo_menor_memoria()  # Intenta mover el proceso con la menor memoria a listo
        actualizar_interfaz()
        time.sleep(6) # Cada 6 segundos
        mover_a_listo_mayor_memoria() # Intenta mover el proceso con la mayor memoria a listo
        actualizar_interfaz()
        #esto se hace como que ocurren los eventos necesarios para que se mueva un bloqueado a listo


# Función para mover bloqueados a swap
def mover_a_swap(proceso):
    global MEMORIA_USADA
    if proceso in procesos_bloqueados:
        procesos_bloqueados.remove(proceso)
        procesos_swap.append(proceso)
        proceso.estado = 'Swap'
        MEMORIA_USADA -= proceso.memoria  # Restar memoria solo cuando sale de bloqueado
        actualizar_interfaz()


# Define la probabilidad de mover procesos de swap a bloqueados
PROBABILIDAD_SWAP_A_BLOQUEADO = 0.3  # 30% de probabilidad
# Función para revisar procesos en Swap y moverlos a Listos o Bloqueados si hay suficiente memoria
def revisar_swap():
    global MEMORIA_USADA
    while True:
        for proceso in procesos_swap[:]:
            if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL and random.random() < PROBABILIDAD_SWAP_A_BLOQUEADO:
                # Mover proceso a bloqueados si cumple con la probabilidad
                procesos_swap.remove(proceso) # aca movemos el proceso de swap
                procesos_bloqueados.append(proceso) # lo añadimos a bloqueados
                proceso.estado = 'Bloqueado'
                MEMORIA_USADA += proceso.memoria # se le suma a la memoria usada 
                mensaje_error.config(text=f"El Proceso {proceso.id} se ha movido a Bloqueado desde Swap.")
            else:
                if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL:
                    # Mover proceso a listos si hay memoria suficiente
                    procesos_swap.remove(proceso)
                    procesos_listos.append(proceso)
                    proceso.estado = 'Listo'
                    MEMORIA_USADA += proceso.memoria  # Sumar memoria solo cuando sale de Swap a Listo
                    mensaje_error.config(text=f"El Proceso {proceso.id} ha pasado a Listo desde Swap.")
                    # aca lo que pasaria es que el proceso listo/suspendido dentro de swap pase a listo pero obviamos el hecho de que hubo otro evento que hizo que pase de bloqueado/suspendido a listo/suspendido asi nos ahorramos un marron copado
                    
            actualizar_interfaz()
        time.sleep(7)


# Función para simular la ejecución de procesos
# Definir la probabilidad de que un proceso en ejecución pase a bloqueado
PROBABILIDAD_BLOQUEO = 0.9  # 90% de probabilidad de que un proceso pase a bloqueado

# Define la probabilidad de que un proceso en listo pase a swap en lugar de ejecutarse
PROBABILIDAD_LISTO_A_SWAP = 0.2  # 20% de probabilidad
PROBABILIDAD_EJECUTANDO_A_SWAP = 0.2  # 20% de probabilidad

# Función para simular la ejecución de procesos
def ejecutar_procesos():
    global MEMORIA_USADA, proceso_ejecucion
    while True:
        if procesos_listos:
            proceso_ejecucion = procesos_listos.pop(0) # FIFO, obtenemos el primer proceso listo
            
            # Verificar si el proceso se mueve a Swap
            if random.random() < PROBABILIDAD_LISTO_A_SWAP and len(procesos_swap) < MAX_SWAP:
                # Mover el proceso a Swap
                proceso_ejecucion.estado = 'Swap'
                procesos_swap.append(proceso_ejecucion)
                mensaje_error.config(text=f"El Proceso {proceso_ejecucion.id} se ha movido a Swap desde Listos.")
                MEMORIA_USADA -= proceso_ejecucion.memoria
            else:
                # Ejecutar el proceso normalmente
                proceso_ejecucion.estado = 'Ejecutando'
                actualizar_interfaz()
                time.sleep(3)  # Simula el tiempo de ejecución del proceso

                # Ajustar la probabilidad de bloqueo
                if proceso_ejecucion.veces_bloqueado > 0:
                    # Si el proceso ha sido bloqueado antes, la probabilidad de bloqueo baja al 10%
                    probabilidad_bloqueo_actual = 0.1
                else:
                    # Probabilidad normal de bloqueo si nunca ha sido bloqueado
                    probabilidad_bloqueo_actual = PROBABILIDAD_BLOQUEO

                # Simular el bloqueo del proceso
                if random.random() < probabilidad_bloqueo_actual:
                    proceso_ejecucion.estado = 'Bloqueado'
                    procesos_bloqueados.append(proceso_ejecucion)
                    proceso_ejecucion.veces_bloqueado += 1  # Incrementar el contador de bloqueos
                    mensaje_error.config(text=f"El Proceso {proceso_ejecucion.id} se ha bloqueado durante la ejecución.")

                elif random.random() < PROBABILIDAD_EJECUTANDO_A_SWAP and len(procesos_swap) < MAX_SWAP:
                    proceso_ejecucion.estado = 'Swap'
                    procesos_swap.append(proceso_ejecucion)
                    mensaje_error.config(text=f"El Proceso {proceso_ejecucion.id} se ha suspendido durante la ejecución.")
                    MEMORIA_USADA -= proceso_ejecucion.memoria

                else:
                    proceso_ejecucion.estado = 'Terminado'
                    procesos_terminados.append(proceso_ejecucion)
                    MEMORIA_USADA -= proceso_ejecucion.memoria  # Restar memoria solo cuando el proceso termina y ocupaba memoria

            proceso_ejecucion = None
        actualizar_interfaz()
        time.sleep(1)

# Función para manejar el evento de agregar un proceso manualmente
def agregar_proceso_manual():
    try:
        memoria_necesaria = int(memoria_entry.get())
        if memoria_necesaria > 0:
            agregar_proceso(memoria_necesaria)
        else:
            tk.messagebox.showerror("Error", "La memoria debe ser un número positivo.")
            time.sleep(3)
    except ValueError:
        tk.messagebox.showerror("Error", "Ingrese un valor numérico válido para la memoria.")
        time.sleep(3)
    finally:
        memoria_entry.delete(0, tk.END)  # Limpiar el campo de entrada

# Función para agregar un proceso aleatorio desde el botón
def agregar_proceso_aleatorio():
    memoria_necesaria = random.randint(50, 200)
    print(f"Agregando proceso aleatorio con {memoria_necesaria} MB de memoria")
    agregar_proceso(memoria_necesaria)


# Actualiza la interfaz gráfica
# Actualiza la interfaz gráfica
def actualizar_interfaz():
    memoria_label.config(text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB")
    
    # Limpiar y actualizar lista de procesos nuevos
    nuevos_listbox.delete(0, tk.END)
    for p in procesos_nuevos:
        nuevos_listbox.insert(tk.END, str(p))

    # Limpiar y actualizar lista de procesos listos
    listos_listbox.delete(0, tk.END)
    for p in procesos_listos:
        listos_listbox.insert(tk.END, str(p))

    # Limpiar y actualizar lista de procesos bloqueados
    bloqueados_listbox.delete(0, tk.END)
    for p in procesos_bloqueados:
        bloqueados_listbox.insert(tk.END, str(p))

    # Limpiar y actualizar lista de procesos en swap
    swap_listbox.delete(0, tk.END)
    for p in procesos_swap:
        swap_listbox.insert(tk.END, str(p))

    # Limpiar y actualizar lista de procesos terminados
    terminados_listbox.delete(0, tk.END)
    for p in procesos_terminados:
        terminados_listbox.insert(tk.END, str(p))

    ejecucion_label.config(text=f"{proceso_ejecucion if proceso_ejecucion else ''}")
    mensaje_error.config(text="")  # Limpiar mensaje de error en cada actualización


# Configuración de la interfaz gráfica con Tkinter
ventana = tk.Tk()
ventana.title("Simulador de Gestión de Procesos y Memoria")
ventana.geometry("800x600")
ventana.config(bg="#f0f0f0")

# Agregar botón de compactación en la interfaz
compactar_boton = tk.Button(ventana, text="Compactar Memoria", command=comactar_memoria, font=("Arial", 12), bg="#ffd700")
compactar_boton.pack(side=tk.BOTTOM, pady=10)

# Sección superior para mostrar el uso de memoria
frame_memoria = tk.Frame(ventana, pady=10, bg="#f0f0f0")
frame_memoria.pack(fill=tk.X)

memoria_label = tk.Label(frame_memoria, text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB", font=("Arial", 14, "bold"), bg="#f0f0f0")
memoria_label.pack()

# Sección para agregar procesos manualmente y aleatoriamente
frame_agregar = tk.Frame(ventana, pady=10, padx=10, bd=2, relief=tk.RAISED, bg="#dcdcdc")
frame_agregar.pack(fill=tk.X, pady=10)

memoria_label_entry = tk.Label(frame_agregar, text="Memoria del Proceso (MB):", font=("Arial", 12), bg="#dcdcdc")
memoria_label_entry.pack(side=tk.LEFT)

memoria_entry = tk.Entry(frame_agregar, width=10, font=("Arial", 12))
memoria_entry.pack(side=tk.LEFT, padx=5)

agregar_boton = tk.Button(frame_agregar, text="Agregar Proceso", command=agregar_proceso_manual, font=("Arial", 12), bg="#90ee90")
agregar_boton.pack(side=tk.LEFT, padx=5)

# Botón para agregar proceso aleatorio
agregar_aleatorio_boton = tk.Button(frame_agregar, text="Agregar Proceso Aleatorio", command=agregar_proceso_aleatorio, font=("Arial", 12), bg="#add8e6")
agregar_aleatorio_boton.pack(side=tk.LEFT, padx=5)

# Mensaje de error si se supera la memoria
mensaje_error = tk.Label(frame_agregar, text="", font=("Arial", 12), fg="red", bg="#dcdcdc")
mensaje_error.pack(side=tk.LEFT, padx=10)

# seccion arriba ejecutando
frame_ejecucion = tk.Frame(ventana, pady=10, bg="#f0f0f0")
frame_ejecucion.pack(fill=tk.X)

ejecucion_label = tk.Label(frame_ejecucion, font=("Arial", 14, "bold"), bg="#f0f0f0")
ejecucion_label.pack()

# Sección para mostrar la lista de procesos en diferentes estados
frame_procesos = tk.Frame(ventana, padx=10, pady=10, bg="#f0f0f0")
frame_procesos.pack(fill=tk.BOTH, expand=True)

# Sección de procesos listos
frame_nuevos = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_nuevos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

nuevos_label = tk.Label(frame_nuevos, text="Procesos Nuevos", font=("Arial", 14, "bold"), bg="#f0f0f0")
nuevos_label.pack()

nuevos_listbox = tk.Listbox(frame_nuevos, font=("Arial", 12), bg="#e0f7fa")
nuevos_listbox.pack(fill=tk.BOTH, expand=True)

frame_listos = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_listos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

listos_label = tk.Label(frame_listos, text="Procesos Listos", font=("Arial", 14, "bold"), bg="#f0f0f0")
listos_label.pack()

listos_listbox = tk.Listbox(frame_listos, font=("Arial", 12), bg="#3a6e97")
listos_listbox.pack(fill=tk.BOTH, expand=True)

# Sección de procesos bloqueados
frame_bloqueados = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_bloqueados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

bloqueados_label = tk.Label(frame_bloqueados, text="Procesos Bloqueados", font=("Arial", 14, "bold"), bg="#f0f0f0")
bloqueados_label.pack()

bloqueados_listbox = tk.Listbox(frame_bloqueados, font=("Arial", 12), bg="#973a3a")
bloqueados_listbox.pack(fill=tk.BOTH, expand=True)

# Sección de procesos en swap
frame_swap = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_swap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

swap_label = tk.Label(frame_swap, text="Procesos en Swap", font=("Arial", 14, "bold"), bg="#f0f0f0")
swap_label.pack()

swap_listbox = tk.Listbox(frame_swap, font=("Arial", 12), bg="#977f3a")
swap_listbox.pack(fill=tk.BOTH, expand=True)

# Sección de procesos terminados
frame_terminados = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_terminados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

terminados_label = tk.Label(frame_terminados, text="Procesos Terminados", font=("Arial", 14, "bold"), bg="#f0f0f0")
terminados_label.pack()

terminados_listbox = tk.Listbox(frame_terminados, font=("Arial", 12), bg="#40973a")
terminados_listbox.pack(fill=tk.BOTH, expand=True)

# Sección para mostrar el proceso en ejecución

# Función para finalizar la simulación
def finalizar_simulacion():
    ventana.quit()

# Botón para finalizar la simulación
finalizar_boton = tk.Button(ventana, text="Finalizar Simulación", command=finalizar_simulacion, font=("Arial", 14), bg="#ff6f61")
finalizar_boton.pack(side=tk.BOTTOM, pady=10)

# Inicialización de hilos
hilo_ejecucion = threading.Thread(target=ejecutar_procesos)
hilo_ejecucion.start()

hilo_bloqueados = threading.Thread(target=mover_bloqueados_a_listos)
hilo_bloqueados.start()

hilo_nuevolisto = threading.Thread(target=nuevo_a_listo)
hilo_nuevolisto.start()

hilo_swap = threading.Thread(target=revisar_swap)
hilo_swap.start()

# Hilo para crear procesos aleatorios
hilo_procesos_aleatorios = threading.Thread(target=crear_procesos_automaticos)
hilo_procesos_aleatorios.start()

#hilo principal que se encarga de actualizar la interfaz siendo este el responsable de la exclusion mutua
ventana.mainloop()
