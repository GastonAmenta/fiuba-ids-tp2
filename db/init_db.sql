-- ============================================================
-- Base de datos: Club Deportivo Encuentro
-- Motor: MySQL 8.0+
-- Autor: Proyecto Backend FIUBA
-- ============================================================

CREATE DATABASE IF NOT EXISTS club_deportivo
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE club_deportivo;

-- ============================================================
-- TABLA: deportes
-- Deportes precargados. No se modifican desde la API.
-- ============================================================
CREATE TABLE deportes (
    id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre  VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ============================================================
-- TABLA: socios
-- Nombre y email obligatorios. Email único (incluso inactivos).
-- activo por defecto true.
-- ============================================================
CREATE TABLE socios (
    id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre  VARCHAR(100) NOT NULL,
    email   VARCHAR(150) NOT NULL UNIQUE,
    activo  BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_socios_nombre
        CHECK (CHAR_LENGTH(TRIM(nombre)) > 0),
    CONSTRAINT chk_socios_email
        CHECK (email LIKE '%_@_%._%')
) ENGINE=InnoDB;

-- ============================================================
-- TABLA: canchas
-- precio_hora entero positivo (en centavos).
-- techada y activa por defecto false y true respectivamente.
-- ============================================================
CREATE TABLE canchas (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    id_deporte  INT UNSIGNED NOT NULL,
    precio_hora INT UNSIGNED NOT NULL,
    techada     BOOLEAN NOT NULL DEFAULT FALSE,
    activa      BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_canchas_deporte
        FOREIGN KEY (id_deporte) REFERENCES deportes(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_canchas_nombre
        CHECK (CHAR_LENGTH(TRIM(nombre)) > 0),
    CONSTRAINT chk_canchas_precio
        CHECK (precio_hora > 0)
) ENGINE=InnoDB;

-- ============================================================
-- TABLA: reservas
-- Estado ENUM. Precio histórico y total calculado por el server.
-- No se permite borrar cancha con reservas (FK RESTRICT).
-- ============================================================
CREATE TABLE reservas (
    id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_socio          INT UNSIGNED NOT NULL,
    id_cancha         INT UNSIGNED NOT NULL,
    fecha_hora_inicio DATETIME(6) NOT NULL,
    fecha_hora_fin    DATETIME(6) NOT NULL,
    estado            ENUM('confirmada','cancelada','finalizada')
                      NOT NULL DEFAULT 'confirmada',
    precio_hora       INT UNSIGNED NOT NULL,
    precio_total      INT UNSIGNED NOT NULL,

    CONSTRAINT fk_reservas_socio
        FOREIGN KEY (id_socio) REFERENCES socios(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_reservas_cancha
        FOREIGN KEY (id_cancha) REFERENCES canchas(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_reservas_fechas
        CHECK (fecha_hora_inicio < fecha_hora_fin),
    CONSTRAINT chk_reservas_duracion
        CHECK (TIMESTAMPDIFF(HOUR, fecha_hora_inicio, fecha_hora_fin) BETWEEN 1 AND 3),
    CONSTRAINT chk_reservas_hora_punto
        CHECK (MINUTE(fecha_hora_inicio) = 0
           AND SECOND(fecha_hora_inicio) = 0
           AND MINUTE(fecha_hora_fin) = 0
           AND SECOND(fecha_hora_fin) = 0),
    CONSTRAINT chk_reservas_horario
        CHECK (HOUR(fecha_hora_inicio) >= 8
           AND (HOUR(fecha_hora_fin) <= 23 OR HOUR(fecha_hora_fin) = 0)),
    CONSTRAINT chk_reservas_no_atraviesa_medianoche
        CHECK (DATE(fecha_hora_inicio) = DATE(fecha_hora_fin)),
    CONSTRAINT chk_reservas_precios
        CHECK (precio_hora > 0 AND precio_total > 0)
) ENGINE=InnoDB;

CREATE TABLE bloqueos (
    id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_cancha         INT UNSIGNED NOT NULL,
    fecha             DATE NOT NULL,
    hora_inicio       TIME NOT NULL,
    hora_fin          TIME NOT NULL,
    motivo            VARCHAR(255) NOT NULL,

    CONSTRAINT fk_bloqueos_cancha
        FOREIGN KEY (id_cancha) REFERENCES canchas(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_bloqueos_horas CHECK (hora_inicio < hora_fin),
    CONSTRAINT chk_bloqueos_motivo CHECK (CHAR_LENGTH(TRIM(motivo)) > 0)
) ENGINE=InnoDB;

-- ============================================================
-- ÍNDICES para acelerar búsquedas y validaciones de superposición
-- ============================================================
CREATE INDEX idx_reservas_cancha_fechas
    ON reservas (id_cancha, fecha_hora_inicio, fecha_hora_fin, estado);

CREATE INDEX idx_reservas_socio_fechas
    ON reservas (id_socio, fecha_hora_inicio, fecha_hora_fin, estado);

CREATE INDEX idx_reservas_estado
    ON reservas (estado);

CREATE INDEX idx_bloqueos_cancha_fecha
    ON bloqueos (id_cancha, fecha, hora_inicio, hora_fin);

CREATE INDEX idx_canchas_deporte
    ON canchas (id_deporte);

CREATE INDEX idx_canchas_activa
    ON canchas (activa);

CREATE INDEX idx_socios_activo
    ON socios (activo);

-- ============================================================
-- DATOS DE EJEMPLO
-- ============================================================

-- --------- Deportes ---------
INSERT INTO deportes (nombre) VALUES
    ('Fútbol'),
    ('Tenis'),
    ('Básquet'),
    ('Vóley'),
    ('Pádel');

-- --------- Socios ---------
INSERT INTO socios (nombre, email, activo) VALUES
    ('Juan Pérez',        'juan.perez@example.com',    TRUE),
    ('María González',    'maria.gonzalez@example.com', TRUE),
    ('Carlos Rodríguez',  'carlos.rodriguez@example.com', TRUE),
    ('Ana Martínez',      'ana.martinez@example.com',  TRUE),
    ('Luis Fernández',    'luis.fernandez@example.com', TRUE),
    ('Sofía López',       'sofia.lopez@example.com',   TRUE),
    ('Diego Sánchez',     'diego.sanchez@example.com', FALSE),
    ('Laura Díaz',        'laura.diaz@example.com',    TRUE),
    ('Pablo Romero',      'pablo.romero@example.com',  TRUE),
    ('Carla Sosa',        'carla.sosa@example.com',    FALSE);

-- --------- Canchas ---------
INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
    ('Cancha 1 - Fútbol 5',     1, 1000000, FALSE, TRUE),
    ('Cancha 2 - Fútbol 5',     1, 1000000, TRUE,  TRUE),
    ('Cancha 3 - Fútbol 7',     1, 1500000, FALSE, TRUE),
    ('Cancha 1 - Tenis',        2,  800000, FALSE, TRUE),
    ('Cancha 2 - Tenis',        2,  800000, TRUE,  TRUE),
    ('Cancha 1 - Básquet',      3, 1200000, TRUE,  TRUE),
    ('Cancha 1 - Vóley',        4,  900000, FALSE, TRUE),
    ('Cancha 1 - Pádel',        5, 1100000, TRUE,  TRUE),
    ('Cancha 2 - Pádel',        5, 1100000, FALSE, FALSE),
    ('Cancha 4 - Fútbol 5',     1, 1000000, TRUE,  TRUE);

-- --------- Reservas ---------
-- Nota: usar fechas futuras para que pasen la validación "inicio > ahora".
-- Los precios_hora y precios_total son "históricos" (los fija el server).

INSERT INTO reservas
    (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
VALUES
    -- Confirmadas
    (1, 1, '2026-10-15 18:00:00.000000', '2026-10-15 20:00:00.000000', 'confirmada', 1000000, 2000000),
    (2, 2, '2026-10-15 19:00:00.000000', '2026-10-15 21:00:00.000000', 'confirmada', 1000000, 2000000),
    (3, 4, '2026-10-16 09:00:00.000000', '2026-10-16 10:00:00.000000', 'confirmada',  800000,  800000),
    (4, 6, '2026-10-16 15:00:00.000000', '2026-10-16 18:00:00.000000', 'confirmada', 1200000, 3600000),
    (5, 3, '2026-10-17 10:00:00.000000', '2026-10-17 12:00:00.000000', 'confirmada', 1500000, 3000000),
    (8, 8, '2026-10-17 20:00:00.000000', '2026-10-17 22:00:00.000000', 'confirmada', 1100000, 2200000),

    -- Canceladas
    (1, 5, '2026-10-18 08:00:00.000000', '2026-10-18 09:00:00.000000', 'cancelada',   800000,  800000),
    (6, 7, '2026-10-18 14:00:00.000000', '2026-10-18 16:00:00.000000', 'cancelada',   900000, 1800000),

    -- Finalizadas
    (2, 1, '2026-09-01 18:00:00.000000', '2026-09-01 20:00:00.000000', 'finalizada', 1000000, 2000000),
    (3, 2, '2026-09-02 10:00:00.000000', '2026-09-02 11:00:00.000000', 'finalizada', 1000000, 1000000),
    (4, 6, '2026-09-03 16:00:00.000000', '2026-09-03 18:00:00.000000', 'finalizada', 1200000, 2400000),
    (5, 4, '2026-09-04 09:00:00.000000', '2026-09-04 12:00:00.000000', 'finalizada',  800000, 2400000);

-- ============================================================
-- VISTA: disponibilidad de canchas por intervalo
-- Útil para el endpoint GET /canchas/disponibles
-- ============================================================
CREATE OR REPLACE VIEW vista_canchas_disponibles AS
SELECT
    c.id,
    c.nombre,
    c.id_deporte,
    d.nombre AS deporte,
    c.precio_hora,
    c.techada,
    c.activa
FROM canchas c
JOIN deportes d ON d.id = c.id_deporte
WHERE c.activa = TRUE;

-- ============================================================
-- VERIFICACIÓN
-- ============================================================
SELECT 'Deportes:' AS tabla, COUNT(*) AS total FROM deportes
UNION ALL
SELECT 'Socios:',   COUNT(*) FROM socios
UNION ALL
SELECT 'Canchas:',  COUNT(*) FROM canchas
UNION ALL
SELECT 'Reservas:', COUNT(*) FROM reservas;
