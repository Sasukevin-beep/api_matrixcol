DROP DATABASE IF EXISTS matrixcol_db;
CREATE DATABASE matrixcol_db CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE matrixcol_db;

-- 1. TABLA USUARIO (Equivale a Cliente)
CREATE TABLE usuario (
    id_usuario          INT AUTO_INCREMENT PRIMARY KEY,
    tipo_documento      ENUM('CC','CE','NIT','PP','TI') NOT NULL,
    numero_documento    VARCHAR(20)  NOT NULL,
    nombre              VARCHAR(100) NOT NULL,
    correo              VARCHAR(100) NOT NULL UNIQUE,
    telefono            VARCHAR(16)  NOT NULL,
    direccion           VARCHAR(150) NULL,
    ciudad              VARCHAR(60)  NULL,
    estado              ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuario_documento UNIQUE (tipo_documento, numero_documento)
) ENGINE=InnoDB;

-- 2. TABLA PROGRAMA (Equivale a Categoría)
CREATE TABLE programa (
    id_programa         INT AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL UNIQUE,
    descripcion         VARCHAR(200) NULL,
    estado              ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. TABLA FICHA (Equivale a Producto, depende de Programa)
CREATE TABLE ficha (
    id_ficha            INT AUTO_INCREMENT PRIMARY KEY,
    id_programa         INT NOT NULL,
    codigo_ficha        VARCHAR(20)  NOT NULL UNIQUE,
    jornada             VARCHAR(100) NOT NULL,
    cupo_maximo         INT NOT NULL DEFAULT 30,
    estado              ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_ficha_cupo CHECK (cupo_maximo >= 0),
    CONSTRAINT fk_ficha_programa FOREIGN KEY (id_programa)
        REFERENCES programa (id_programa)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;