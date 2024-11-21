import re
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import random
import datetime

class InterfazAhorcado:
    def __init__(self, root):
        self.root = root
        self.root.title("Ahorcado")
        self.jugador_id = None
        self.palabra = ""
        self.palabra_oculta = []
        self.intentos = 6
        self.letras_intentadas = []

        # Crear la interfaz de entrada
        self.mostrar_entrada_nombre()

    def conectar_db(self):
        """Establece la conexión a la base de datos."""
        return sqlite3.connect('ahorcado.db')

    def obtener_jugador(self, nombre):
        """Obtiene un jugador de la base de datos o lo crea si no existe."""
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Jugador WHERE nombre=?", (nombre,))
        jugador = cursor.fetchone()

        if jugador is None:
            cursor.execute("INSERT INTO Jugador (nombre) VALUES (?)", (nombre,))
            conn.commit()
            jugador_id = cursor.lastrowid
            jugador = (jugador_id, nombre, 0, 0, 0)
        else:
            jugador_id, nombre, victorias, derrotas, partidas_totales = jugador

        conn.close()
        return jugador

    def elegir_palabra(self, tema):
        """Selecciona una palabra aleatoria del tema dado."""
        conn = self.conectar_db()
        cursor = conn.cursor()


        cursor.execute("SELECT palabra FROM Palabra WHERE tema=?", (tema,))
        palabras = cursor.fetchall()

        # Depuración: muestra las palabras recuperadas
        print(f"Palabras encontradas: {palabras}")

        if not palabras: #Si no hay palabras para el tema
            messagebox.showerror("Error ", f"No hay palabras disponibles para este tema'{tema}'.")
            conn.close()
            return None

        palabra = random.choice(palabras)[0]
        conn.close()
        return palabra

    def guardar_resultado_partida(self, resultado):
        """Guarda el resultado de la partida en la base de datos."""
        conn = self.conectar_db()
        cursor = conn.cursor()

        # Registramos la partida
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Partida (fecha, resultado, id_jugador, id_palabra) VALUES (?, ?, ?, ?)",
                       (fecha, resultado, self.jugador_id, self.obtener_id_palabra(self.palabra)))
        conn.commit()

        # Actualizamos victorias y derrotas
        if resultado == 'ganado':
            cursor.execute("UPDATE Jugador SET victorias = victorias + 1 WHERE id_jugador=?", (self.jugador_id,))
        else:
            cursor.execute("UPDATE Jugador SET derrotas = derrotas + 1 WHERE id_jugador=?", (self.jugador_id,))

        # Actualizar partidas totales
        cursor.execute("UPDATE Jugador SET partidas_totales = partidas_totales + 1 WHERE id_jugador=?", (self.jugador_id,))
        conn.commit()
        conn.close()

    def obtener_id_palabra(self, palabra):
        """Obtiene el id de una palabra en la base de datos."""
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id_palabra FROM Palabra WHERE palabra = ?", (palabra,))
        id_palabra = cursor.fetchone()[0]
        conn.close()
        return id_palabra

    def mostrar_estadisticas(self):
        """Muestra las estadísticas del jugador en la interfaz gráfica."""
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT victorias, derrotas, partidas_totales FROM Jugador WHERE id_jugador = ?", (self.jugador_id,))
        victorias, derrotas, partidas_totales = cursor.fetchone()
        conn.close()

        stats_text = f"Victorias: {victorias}\nDerrotas: {derrotas}\nPartidas Totales: {partidas_totales}"
        messagebox.showinfo("Estadísticas", stats_text)

    def jugar_partida(self, tema):
        """Inicia la lógica del juego."""
        self.palabra = self.elegir_palabra(tema)
        self.palabra_oculta = ['_'] * len(self.palabra)
        self.intentos = 6
        self.letras_intentadas = []

        self.actualizar_palabra_oculta()

    def actualizar_palabra_oculta(self):
        """Actualiza la visualización de la palabra oculta."""
        self.palabra_label.config(text=" ".join(self.palabra_oculta))
        self.intentos_label.config(text=f"Te quedan {self.intentos} intentos.")

    def adivinar_letra(self):
        """Recibe una letra del jugador e interactúa con el juego."""
        letra = self.letra_entry.get().lower()
        if len(letra) != 1 or not letra.isalpha():
            messagebox.showwarning("Entrada inválida", "Por favor, ingresa solo una letra.")
            return
        if letra in self.letras_intentadas:
            messagebox.showinfo("Letra repetida", f"Ya intentaste la letra '{letra}'")
            return

        self.letras_intentadas.append(letra)

        if letra in self.palabra:
            for i, char in enumerate(self.palabra):
                if char == letra:
                    self.palabra_oculta[i] = letra
            self.actualizar_palabra_oculta()
        else:
            self.intentos -= 1
            self.actualizar_palabra_oculta()
            if self.intentos == 0:
                messagebox.showinfo("¡Perdiste!", f"¡Perdiste! La palabra era: {self.palabra}")
                self.guardar_resultado_partida('perdido')
                self.boton_adivinar.config(state=tk.DISABLED)

        if "_" not in self.palabra_oculta:
            messagebox.showinfo("¡Ganaste!", "¡Felicidades, adivinaste la palabra!")
            self.guardar_resultado_partida('ganado')
            self.boton_adivinar.config(state=tk.DISABLED)

        self.letra_entry.delete(0, tk.END)

    def mostrar_entrada_nombre(self):
        """Muestra la interfaz para ingresar el nombre del jugador."""
        self.nombre_label = tk.Label(self.root, text="Ingrese su nombre:", bg="#f0f0f0", font=("Helvetica",14))
        self.nombre_label.pack(pady=10)
        self.nombre_entry = tk.Entry(self.root, font=("Helvetica",14))
        self.nombre_entry.pack(pady=10)
        self.nombre_button = tk.Button(self.root, text="Comenzar", font =("Helvetica",14),bg="#4CAF50", fg="white",command=self.iniciar_juego)
        self.nombre_button.pack(pady=20)

    def iniciar_juego(self):
        """Inicia el juego después de que el jugador ingresa su nombre."""
        nombre = self.nombre_entry.get()

        # Validación del nombre: solo letras, sin espacios ni caracteres especiales
        if not nombre or not re.match("^[A-Za-z]+$", nombre):
            messagebox.showwarning("Nombre inválido","Por favor, ingresa un nombre válido. Solo letras (sin espacios ni números).")
            return

        jugador = self.obtener_jugador(nombre)
        self.jugador_id = jugador[0]

        self.nombre_label.pack_forget()
        self.nombre_entry.pack_forget()
        self.nombre_button.pack_forget()

        self.mostrar_entrada_tema()

    def mostrar_entrada_tema(self):
        """Muestra la interfaz para seleccionar el tema."""
        self.tema_label = tk.Label(self.root, text="Elige un tema:", bg="#f0f0f0", font=("Helvetica", 14))
        self.tema_label.pack(pady=10)

        self.tema_var = tk.StringVar(self.root)
        self.tema_var.set("Frutas")
        self.tema_menu = tk.OptionMenu(self.root, self.tema_var, "Frutas", "Conceptos informáticos", "Nombres de personas")
        self.tema_menu.config(font=("Helvetica", 14))
        self.tema_menu.pack(pady=10)

        self.tema_button = tk.Button(self.root, text="Jugar", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=self.comenzar_partida)
        self.tema_button.pack(pady=20)

    def comenzar_partida(self):
        """Comienza la partida con el tema seleccionado."""
        tema = self.tema_var.get().lower()

        palabra=self.elegir_palabra(tema)
        if palabra is None:
            return

        self.jugar_partida(tema)

        self.tema_label.pack_forget()
        self.tema_menu.pack_forget()
        self.tema_button.pack_forget()
        self.mostrar_juego()

    def mostrar_juego(self):
        """Muestra la interfaz del juego."""
        self.palabra_label = tk.Label(self.root, text="Palabra oculta:", font=("Helvetica", 24))
        self.palabra_label.pack()

        self.intentos_label = tk.Label(self.root, text=f"Te quedan {self.intentos} intentos.", font=("Helvetica", 14))
        self.intentos_label.pack()

        self.letra_label = tk.Label(self.root, text="Ingresa una letra:", font=("Helvetica", 14))
        self.letra_label.pack()
        self.letra_entry = tk.Entry(self.root, font=("Helvetica", 14))
        self.letra_entry.pack()

        self.boton_adivinar = tk.Button(self.root, text="Adivinar Letra", font=("Helvetica", 14), command=self.adivinar_letra)
        self.boton_adivinar.pack()

        self.estadisticas_button = tk.Button(self.root, text="Ver Estadísticas", font=("Helvetica", 14), command=self.mostrar_estadisticas)
        self.estadisticas_button.pack()

# Crear la ventana principal
root = tk.Tk()
juego = InterfazAhorcado(root)
root.mainloop()
