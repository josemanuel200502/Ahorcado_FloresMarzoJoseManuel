import sqlite3

#Conexion a la base de datos ( se crea automáticamente si no existe)

def conectar():
    conexion= sqlite3.connect("ahorcado.db") #Se crea un archivo de base de datos llamado "ahorcado.db"
    return conexion

#Cerramos la conexión

def cerrar_conexion(conexion):
    conexion.close()
    print("Conexion cerrada.")

def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    #Creamos tabla Jugador
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Jugador (
            id_jugador INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Victorias INTEGER DEFAULT 0,
            Derrotas INTEGER DEFAULT 0,
            Partidas_totales INTEGER DEFAULT 0
        )
    """)

    #Creamos tabla Palabra
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Palabra (
            id_palabra INTEGER PRIMARY KEY AUTOINCREMENT,
            palabra TEXT NOT NULL,
            tema TEXT NOT NULL
        )
    """)



    # Verificar si ya existen palabras antes de insertarlas
    cursor.execute("SELECT COUNT(*) FROM Palabra")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute('''
        INSERT INTO Palabra(palabra,tema)VALUES
        ('manzana','fruta'),
        ('platano','fruta'),
        ('naranja','fruta'),
        ('sandia','fruta'),
        ('fresa','fruta'),
        ('frambuesa','fruta'),
        ('kiwi','fruta'),
        ('melon','fruta'),
        ('python','concepto informático'),
        ('algoritmo','concepto informático'),
        ('variable','concepto informático'),
        ('java','concepto informático'),
        ('Array','concepto informático'),
        ('html','concepto informático'),
        ('juan', 'nombre de persona'),
        ('ana','nombre de persona'),
        ('maria','nombre de persona'),
        ('victor', 'nombre de persona'),
        ('daniel','nombre de persona'),
        ('rodrigo','nombre de persona')
        ''')

    conexion.commit()
    cerrar_conexion(conexion)

#Crear la base de datos y tablas
crear_tablas()
print ("Base de datos y tablas creadas exitosamente.")

