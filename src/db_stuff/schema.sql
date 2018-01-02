DROP OWNED BY redes;
DROP DATABASE IF EXISTS proyecto2redes;
DROP ROLE IF EXISTS redes;

create role redes with login password 'redes1234';
create database proyecto2redes owner redes;
grant all privileges on database proyecto2redes to redes;

\c proyecto2redes

-- Tabla de Pokemon
CREATE TABLE Pokemon(
	nIdpokemon	SERIAL						,
	nombre		VARCHAR(64)			NOT NULL,
	imagen		VARCHAR(128)				,
	CONSTRAINT pk_pokemon PRIMARY KEY (nIdpokemon),
	CONSTRAINT unq_pokemon UNIQUE (nombre)
);

-- Tabla de Usuario
CREATE TABLE Usuario(
	nIdusuario	SERIAL						,
	nombre		VARCHAR(64)			NOT NULL,
	password    VARCHAR(128)        NOT NULL,
	CONSTRAINT pk_usuario PRIMARY KEY (nIdusuario),
	CONSTRAINT unq_usuario UNIQUE (nombre)
);

-- Tabla de captura
CREATE TABLE Captura(
    nIdpokemon  INT     NOT NULL,
    nIdusuario  INT     NOT NULL,
    CONSTRAINT unq_captura UNIQUE (nIdpokemon, nIdusuario),
    CONSTRAINT fk_captura_pokemon FOREIGN KEY(nIdpokemon) REFERENCES Pokemon(nIdpokemon) ON DELETE CASCADE,
    CONSTRAINT fk_captura_usuario FOREIGN KEY(nIdusuario) REFERENCES Usuario(nIdusuario) ON DELETE CASCADE
);

ALTER TABLE Pokemon OWNER TO redes;
ALTER TABLE Usuario OWNER TO redes;
ALTER TABLE Captura OWNER TO redes;
