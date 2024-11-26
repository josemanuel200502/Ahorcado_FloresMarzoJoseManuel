import re
import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
from PIL import Image, ImageTk


class InterfazAhorcado:
    def __init__(self, root):
        self.root = root
        self.root.title("Ahorcado")
        self.jugador_id = None
        self.palabra = ""
        self.palabra_oculta = []
        self.intentos = 6
        self.letras_intentadas = []
        self.imagen_label = tk.Label(self.root)
        self.imagen_label.pack(pady=10)
        self.tema_actual = None
        self.imagenes = [
            self.redimensionar_imagen(Image.open("Imagenes/imagen1.png")),
            self.redimensionar_imagen(Image.open("Imagenes/imagen2.png")),
            self.redimensionar_imagen(Image.open("Imagenes/imagen3.png")),
            self.redimensionar_imagen(Image.open("Imagenes/imagen4.png")),
            self.redimensionar_imagen(Image.open("Imagenes/imagen5.png")),
            self.redimensionar_imagen(Image.open("Imagenes/imagen6.png")),
            self.redimensionar_imagen(Image.open("Imagenes/Victoria.png")),
            self.redimensionar_imagen(Image.open("Imagenes/Perder.png")),

        ]

        # Crear la interfaz de entrada

        self.mostrar_entrada_nombre()


    # Metodo para redimensionar la imagen

    def redimensionar_imagen(self, imagen, tamano=(300, 300)):
        imagen = imagen.resize(tamano, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(imagen)

    # Metodo para conexion a la base de datos

    def conectar_db(self):

        # Establece la conexión a la base de datos.

        return sqlite3.connect('ahorcado.db')

    #Metodo para obtener los jugadores

    def obtener_jugador(self, nombre):

        # Obtiene un jugador de la base de datos o lo crea si no existe.

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

    #Metodo para elegir la palabra

    def elegir_palabra(self, tema):

        # Selecciona una palabra aleatoria del tema dado.

        conn = self.conectar_db()
        cursor = conn.cursor()

        tema = tema.strip().lower()

        print(f"Buscando palabras para el tema '{tema.strip()}'")
        # Realizar una consulta más simple

        cursor.execute("SELECT palabra FROM Palabra WHERE LOWER(tema) LIKE ?", ('%' + tema.lower() + '%',))
        resultados = cursor.fetchall()

        # Mostrar los resultados

        if resultados:
            # Selecciona una palabra aleatoria del tema

            palabra = random.choice(resultados)[0]  # obtener solo la palabra

            conn.close()
            return palabra
        else:
            print("No se encontraron palabras para este tema.")
            conn.close()
            return None  # Devolver None si no se encuentran palabras

    # Metodo para resetear el juego

    def reset(self):

        # Reinicia los valores del juego a su estado inicial

        self.palabra_oculta = []
        self.intentos = 6
        self.letras_intentadas = []

        # Obtén una nueva palabra del tema actual

        palabra = self.elegir_palabra(self.tema_actual)  # Usamos self.tema_actual para mantener el tema
        if palabra:
            self.palabra_original = palabra
            self.palabra_oculta = ['_'] * len(self.palabra_original)

            # Actualiza la interfaz del juego con la nueva palabra y los intentos

            self.actualizar_palabra_oculta()

            # Reinicia el estado del juego (por ejemplo, el contador de intentos)

            self.intentos_label.config(text=f"Te quedan {self.intentos} intentos.")
            self.letra_entry.delete(0, tk.END)  # Limpia el campo de la letra
            self.actualizar_imagen_ahorcado()

        else:
            messagebox.showwarning("Error", "No se pudo obtener una nueva palabra.")

    #Metodo que ve la entrada del nombre

    def mostrar_entrada_nombre(self):
        # Función de validación usando expresiones regulares (re) que solo permite letras

        def validar_nombre(char):
            if re.match("^[A-Za-z]+$", char):  # Permite solo letras (mayúsculas o minúsculas)
                return True
            else:
                messagebox.showwarning("Nombre inválido", "Solo se permiten letras.")
                return False

        # Crear la validación del campo de entrada

        self.nombre_valida = self.root.register(validar_nombre)

        # Muestra la interfaz para ingresar el nombre del jugador.

        self.nombre_label = tk.Label(self.root, text="Ingrese su nombre:", bg="#f0f0f0", font=("Helvetica", 14))
        self.nombre_label.pack(pady=10)

        self.nombre_entry = tk.Entry(self.root, font=("Helvetica", 14), validate="key",
                                     validatecommand=(self.nombre_valida, "%S"))
        self.nombre_entry.pack(pady=10)

        self.tema_label = tk.Label(self.root, text="Elige un tema:", bg="#f0f0f0", font=("Helvetica", 14))
        self.tema_label.pack(pady=10)

        self.tema_button_1 = tk.Button(self.root, text="fruta", font=("Helvetica", 14),
                                       command=lambda: self.iniciar_juego('fruta'))
        self.tema_button_1.pack(pady=5)

        self.tema_button_2 = tk.Button(self.root, text="concepto informático", font=("Helvetica", 14),
                                       command=lambda: self.iniciar_juego('concepto informático'))
        self.tema_button_2.pack(pady=5)

        self.tema_button_3 = tk.Button(self.root, text="nombre de persona", font=("Helvetica", 14),
                                       command=lambda: self.iniciar_juego('nombre de persona'))
        self.tema_button_3.pack(pady=5)

    #Metodo que inicia el juego

    def iniciar_juego(self, tema):
        # Este método se llama cuando el jugador hace clic en un tema
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Nombre inválido", "Por favor, ingresa tu nombre.")
            return

        jugador = self.obtener_jugador(nombre)
        self.jugador_id = jugador[0]

        palabra = self.elegir_palabra(tema)
        if not palabra:
            messagebox.showwarning("Error", f"No se encontraron palabras para el tema '{tema}'.")
            return

        # Guardamos el tema para usarlo en el reset

        self.tema_actual = tema

        # Inicializar los valores del juego

        self.palabra_oculta = ['_'] * len(palabra)
        self.palabra_original = palabra
        self.intentos = 6
        self.letras_intentadas = []

        # Ocultar la interfaz de inicio y mostrar la de juego

        self.nombre_label.pack_forget()
        self.nombre_entry.pack_forget()
        self.tema_label.pack_forget()
        self.tema_button_1.pack_forget()
        self.tema_button_2.pack_forget()
        self.tema_button_3.pack_forget()
        self.boton_reset = tk.Button(self.root, text="Reset", font=("Helvetica", 14), command=self.reset)
        self.boton_reset.pack(pady=10)

        # Mostrar la interfaz de juego

        self.mostrar_juego()

    #Metodo que muestra el jeugo

    def mostrar_juego(self):
        """Muestra la interfaz del juego."""
        self.palabra_label = tk.Label(self.root, text="Palabra oculta:", font=("Helvetica", 24))
        self.palabra_label.pack()

        self.intentos_label = tk.Label(self.root, text=f"Te quedan {self.intentos} intentos.", font=("Helvetica", 14))
        self.intentos_label.pack()

        self.imagen_label = tk.Label(self.root)
        self.imagen_label.pack(pady=10)
        self.actualizar_imagen_ahorcado()

        self.letra_label = tk.Label(self.root, text="Ingresa una letra:", font=("Helvetica", 14))
        self.letra_label.pack()
        self.letra_entry = tk.Entry(self.root, font=("Helvetica", 14))
        self.letra_entry.pack()

        self.letra_entry.bind("<Key>", self.adivinar_letra)
        self.imagen_label.pack(pady=10)

        self.salir_button = tk.Button(self.root)

        self.estadisticas_button = tk.Button(self.root, text="Ver Estadísticas", font=("Helvetica", 14),
                                             command=self.mostrar_estadisticas)
        self.estadisticas_button.pack()

        self.salir_button = tk.Button(self.root, text="Salir", font=("Helvetica", 14), command=self.salir)
        self.salir_button.pack(pady=10)

    def actualizar_palabra_oculta(self):
        #Actualiza la visualización de la palabra oculta en la interfaz.

        self.palabra_label.config(text=" ".join(self.palabra_oculta))
        self.intentos_label.config(text=f"Te quedan {self.intentos} intentos.")

    def salir(self):
        # Cierra la aplicación.

        self.root.quit()

    def actualizar_imagen_ahorcado(self):
        # Actualiza la imagen del ahorcado según los intentos restantes.

        if self.intentos == 6:
            self.imagen_label.config(image=self.imagenes[0])  # Sin fallos
        elif self.intentos == 5:
            self.imagen_label.config(image=self.imagenes[1])
        elif self.intentos == 4:
            self.imagen_label.config(image=self.imagenes[2])
        elif self.intentos == 3:
            self.imagen_label.config(image=self.imagenes[3])
        elif self.intentos == 2:
            self.imagen_label.config(image=self.imagenes[4])
        elif self.intentos == 1:
            self.imagen_label.config(image=self.imagenes[5])
        elif self.intentos == 0:
            self.imagen_label.config(image=self.imagenes[7])  # Mostrar imagen de derrota

    def adivinar_letra(self, event):

        # Deshabilitar el evento de la tecla si el juego terminó

        if self.intentos == 0 or "_" not in self.palabra_oculta:
            return  # Si el juego terminó, no se procesan más letras

        letra = event.char.lower()
        if len(letra) != 1 or not letra.isalpha():
            messagebox.showwarning("Entrada inválida", "Por favor, ingresa solo una letra.")
            return

        if letra in self.letras_intentadas:
            messagebox.showinfo("Letra repetida", f"Ya intentaste la letra '{letra}'")
            return

        self.letras_intentadas.append(letra)

        if letra in self.palabra_original:
            for i, char in enumerate(self.palabra_original):
                if char == letra:
                    self.palabra_oculta[i] = letra
            self.actualizar_palabra_oculta()

        else:
            self.intentos -= 1
            self.actualizar_imagen_ahorcado()
            self.actualizar_palabra_oculta()
            if self.intentos == 0:
                self.imagen_label.config(image=self.imagenes[7])  # Muestra la imagen de la derrota
                messagebox.showinfo("¡Perdiste!", f"¡Perdiste! La palabra era: {self.palabra_original}")
                self.actualizar_estadisticas(False)  # Actualiza las estadísticas con derrota
                self.letra_entry.config(state="disabled")  # Deshabilita la entrada de texto

        # Comprobamos si se ha ganado (todas las letras han sido adivinadas)

        if "_" not in self.palabra_oculta:
            self.imagen_label.config(image=self.imagenes[6])  # Muestra la imagen de la victoria
            messagebox.showinfo("¡Ganaste!", "¡Felicidades, adivinaste la palabra!")
            self.actualizar_estadisticas(True)  # Actualiza las estadísticas con victoria
            self.letra_entry.config(state="disabled")  # Deshabilita la entrada de texto

    def mostrar_estadisticas(self):
        # Muestra las estadísticas del jugador en la interfaz gráfica.
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT victorias, derrotas, partidas_totales FROM Jugador WHERE id_jugador = ?",
                       (self.jugador_id,))
        victorias, derrotas, partidas_totales = cursor.fetchone()
        conn.close()

        stats_text = f"Victorias: {victorias}\nDerrotas: {derrotas}\nPartidas Totales: {partidas_totales}"
        messagebox.showinfo("Estadísticas", stats_text)

    def actualizar_estadisticas(self, gano):
        # Actualiza las estadísticas del jugador en la base de datos.
        conn = self.conectar_db()
        cursor = conn.cursor()

        if gano:
            cursor.execute(
                "UPDATE Jugador SET victorias = victorias + 1, partidas_totales = partidas_totales + 1 WHERE id_jugador = ?",
                (self.jugador_id,))
        else:
            cursor.execute(
                "UPDATE Jugador SET derrotas = derrotas + 1, partidas_totales = partidas_totales + 1 WHERE id_jugador = ?",
                (self.jugador_id,))

        conn.commit()
        conn.close()


# Crear la ventana principal

root = tk.Tk()
root.config(bg="#ebdae4")
juego = InterfazAhorcado(root)
root.mainloop()
