import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

class MemoriaPaginada(tk.Tk):
    def __init__(self, tamano_memoria, tamano_pagina):
        super().__init__()
        self.title("Simulador de Memoria Paginada")
        
        # Parámetros de la memoria
        self.tamano_memoria = tamano_memoria
        self.tamano_pagina = tamano_pagina
        self.paginas_totales = tamano_memoria // tamano_pagina
        self.memoria = [None] * self.paginas_totales  # Lista que representa cada página de memoria
        self.memoria_usada = 0  # Espacio usado en memoria
        self.memoria_total = tamano_memoria  # Tamaño total de la memoria visual

        # Lock para manejar exclusión mutua
        self.lock = threading.Lock()

        # Crear la interfaz gráfica
        self.canvas = tk.Canvas(self, width=300, height=self.paginas_totales * 30)
        self.canvas.grid(row=0, column=0, columnspan=3)
        
        self.label_id = tk.Label(self, text="ID del proceso")
        self.label_id.grid(row=1, column=0)
        self.entry_id = tk.Entry(self)
        self.entry_id.grid(row=1, column=1)
        
        self.label_espacio = tk.Label(self, text="Espacio requerido")
        self.label_espacio.grid(row=2, column=0)
        self.entry_espacio = tk.Entry(self)
        self.entry_espacio.grid(row=2, column=1)

        self.btn_agregar = tk.Button(self, text="Agregar Proceso", command=self.agregar_proceso)
        self.btn_agregar.grid(row=3, column=0)

        self.btn_simular = tk.Button(self, text="Simular Ejecución", command=self.simular_proceso)
        self.btn_simular.grid(row=3, column=1)

        self.btn_compactar = tk.Button(self, text="Compactar Memoria", command=self.compactar_memoria)
        self.btn_compactar.grid(row=3, column=2)

        self.btn_reset = tk.Button(self, text="Reiniciar", command=self.reiniciar_memoria)
        self.btn_reset.grid(row=4, column=0, columnspan=3)

        # Mostrar el proceso en ejecución
        self.label_proceso_actual = tk.Label(self, text="Proceso en ejecución: Ninguno", font=("Arial", 12))
        self.label_proceso_actual.grid(row=5, column=0, columnspan=3)

        # Label para mostrar memoria usada
        self.label_memoria_usada = tk.Label(self, text=f"Memoria Usada: {self.memoria_usada}/{self.memoria_total}", font=("Arial", 12))
        self.label_memoria_usada.grid(row=6, column=0, columnspan=3)

        # Dibuja la memoria en el canvas
        self.dibujar_memoria()

        # Lista para almacenar los procesos activos
        self.procesos = []

        # Iniciar generación automática al inicio
        self.generacion_automatica = True
        threading.Thread(target=self.generar_procesos_automaticos).start()

    def dibujar_memoria(self):
        self.canvas.delete("all")  # Limpiar el canvas antes de redibujar
        for i in range(self.paginas_totales):
            if self.memoria[i] is None:
                texto = "Vacío"  # Texto si la página está vacía
                color = "white"
            else:
                texto = f"ID: {self.memoria[i]}"  # Mostrar el ID del proceso que ocupa la página
                color = "lightblue"

            self.canvas.create_rectangle(50, i * 30, 250, (i + 1) * 30, fill=color, outline="black")
            self.canvas.create_text(150, (i * 30) + 15, text=texto, fill="black")

        # Actualizar el label de memoria usada
        self.label_memoria_usada.config(text=f"Memoria Usada: {self.memoria_usada}/{self.memoria_total}")

    def agregar_proceso(self):
        try:
            id_proceso = self.entry_id.get()
            espacio_proceso = int(self.entry_espacio.get())

            # Calcular cuántas páginas necesita el proceso
            paginas_necesarias = (espacio_proceso + self.tamano_pagina - 1) // self.tamano_pagina

            # Buscar espacio en la memoria
            paginas_disponibles = [i for i, pagina in enumerate(self.memoria) if pagina is None]

            # Verificar si hay suficiente espacio
            if len(paginas_disponibles) < paginas_necesarias:
                messagebox.showwarning("Advertencia", "No hay suficiente espacio en memoria para el proceso.")
                return

            # Asignar páginas al proceso
            with self.lock:  # Iniciar bloque de exclusión mutua
                for i in range(paginas_necesarias):
                    self.memoria[paginas_disponibles[i]] = id_proceso

                # Actualizar memoria usada
                self.memoria_usada += paginas_necesarias * self.tamano_pagina

            # Guardar el proceso en la lista de procesos
            self.procesos.append({"id": id_proceso, "estado": "En ejecución", "espacio": paginas_necesarias * self.tamano_pagina})
            self.dibujar_memoria()

            # Iniciar ejecución del proceso en un hilo separado
            threading.Thread(target=self.ejecutar_proceso, args=(id_proceso,)).start()

        except ValueError:
            messagebox.showerror("Error", "Espacio debe ser un número entero")

    def ejecutar_proceso(self, id_proceso):
        # Simular el tiempo de ejecución del proceso (de 2 a 6 segundos)
        tiempo_ejecucion = random.randint(2, 6)
        self.label_proceso_actual.config(text=f"Proceso en ejecución: {id_proceso}")
        time.sleep(tiempo_ejecucion)

        # Liberar la memoria ocupada por el proceso después de la ejecución
        with self.lock:  # Iniciar bloque de exclusión mutua
            espacio_liberado = 0
            for i in range(self.paginas_totales):
                if self.memoria[i] == id_proceso:
                    self.memoria[i] = None
                    espacio_liberado += self.tamano_pagina

            self.memoria_usada -= espacio_liberado  # Actualizar memoria usada

        # Actualizar la lista de procesos
        self.procesos = [p for p in self.procesos if p["id"] != id_proceso]
        self.dibujar_memoria()
        self.label_proceso_actual.config(text="Proceso en ejecución: Ninguno")

    def simular_proceso(self):
        if self.procesos:
            proceso_actual = random.choice(self.procesos)  # Elegir un proceso aleatorio
            id_proceso = proceso_actual['id']
            threading.Thread(target=self.ejecutar_proceso, args=(id_proceso,)).start()
        else:
            messagebox.showinfo("Información", "No hay procesos para simular.")

    def compactar_memoria(self):
        # Mover todos los procesos para eliminar huecos entre ellos
        nueva_memoria = [None] * self.paginas_totales
        indice = 0

        with self.lock:  # Iniciar bloque de exclusión mutua
            for i in range(self.paginas_totales):
                if self.memoria[i] is not None:
                    nueva_memoria[indice] = self.memoria[i]
                    indice += 1

            self.memoria = nueva_memoria

        self.dibujar_memoria()
        messagebox.showinfo("Compactación", "La memoria ha sido compactada exitosamente.")

    def reiniciar_memoria(self):
        # Limpiar la memoria y la lista de procesos
        with self.lock:  # Iniciar bloque de exclusión mutua
            self.memoria = [None] * self.paginas_totales
            self.memoria_usada = 0  # Reiniciar memoria usada
        self.procesos = []
        self.dibujar_memoria()

    def generar_procesos_automaticos(self):
        while self.generacion_automatica:
            self.agregar_proceso_aleatorio()
            time.sleep(random.randint(1, 3))  # Generar un proceso aleatorio cada 3 a 8 segundos

if __name__ == "__main__":
    tamano_memoria = 1024  # Tamaño total de la memoria
    tamano_pagina = 64  # Tamaño de cada página

    app = MemoriaPaginada(tamano_memoria, tamano_pagina)
    app.mainloop()
