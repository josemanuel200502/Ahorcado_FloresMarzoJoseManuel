CREATE DATABASE ahorcado;
Use ahorcado;



CREATE TABLE Jugador( 
id_jugador INT PRIMARY KEY auto_increment,
Nombre varchar (20) NOT NULL,
Victorias int default 0  ,
Derrotas int default 0,
Partidas_totales int default 0
);

CREATE TABLE  palabra (
id_palabra INT PRIMARY KEY auto_increment,
palabra varchar (20) NOT NULL,
tema_id INT,
FOREIGN KEY (tema_id) REFERENCES Tema(id_tema)

);

CREATE TABLE Tema(
id_tema int PRIMARY KEY auto_increment,
nombre varchar(20) NOT NULL
);

CREATE TABLE Partida(
id_partida INT PRIMARY KEY auto_increment,
fecha date not null,
resultado ENUM('ganado','perdido') not null,
jugador_id int, 
tema_id int,
palabra_id int,
FOREIGN KEY (jugador_id) REFERENCES Jugador(id_jugador),
FOREIGN KEY (tema_id) REFERENCES Tema (id_tema),
FOREIGN KEY (palabra_id) REFERENCES Palabra (id_palabra)
);

