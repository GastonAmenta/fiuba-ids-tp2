-- phpMyAdmin SQL Dump
-- version 5.2.1deb3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 27-09-2026 a las 21:28:09
-- Versión del servidor: 8.0.46-0ubuntu0.24.04.4
-- Versión de PHP: 8.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `club_deportivo`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bloqueos`
--

CREATE TABLE `bloqueos` (
  `id` int UNSIGNED NOT NULL,
  `id_cancha` int UNSIGNED NOT NULL,
  `fecha` date NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL,
  `motivo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `canchas`
--

CREATE TABLE `canchas` (
  `id` int UNSIGNED NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_deporte` int UNSIGNED NOT NULL,
  `precio_hora` int UNSIGNED NOT NULL,
  `techada` tinyint(1) NOT NULL DEFAULT '0',
  `activa` tinyint(1) NOT NULL DEFAULT '1'
) ;

--
-- Volcado de datos para la tabla `canchas`
--

INSERT INTO `canchas` (`id`, `nombre`, `id_deporte`, `precio_hora`, `techada`, `activa`) VALUES
(1, 'Cancha 1 - Fútbol 5', 1, 1000000, 0, 1),
(2, 'Cancha 2 - Fútbol 5', 1, 1000000, 1, 1),
(3, 'Cancha 3 - Fútbol 7', 1, 1500000, 0, 1),
(4, 'Cancha 1 - Tenis', 2, 800000, 0, 1),
(5, 'Cancha 2 - Tenis', 2, 800000, 1, 1),
(6, 'Cancha 1 - Básquet', 3, 1200000, 1, 1),
(7, 'Cancha 1 - Vóley', 4, 900000, 0, 1),
(8, 'Cancha 1 - Pádel', 5, 1100000, 1, 1),
(9, 'Cancha 2 - Pádel', 5, 1100000, 0, 0),
(10, 'Cancha 4 - Fútbol 5', 1, 1000000, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `deportes`
--

CREATE TABLE `deportes` (
  `id` int UNSIGNED NOT NULL,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `deportes`
--

INSERT INTO `deportes` (`id`, `nombre`) VALUES
(3, 'Básquet'),
(1, 'Fútbol'),
(5, 'Pádel'),
(2, 'Tenis'),
(4, 'Vóley');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reservas`
--

CREATE TABLE `reservas` (
  `id` int UNSIGNED NOT NULL,
  `id_socio` int UNSIGNED NOT NULL,
  `id_cancha` int UNSIGNED NOT NULL,
  `fecha_hora_inicio` datetime(6) NOT NULL,
  `fecha_hora_fin` datetime(6) NOT NULL,
  `estado` enum('confirmada','cancelada','finalizada') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'confirmada',
  `precio_hora` int UNSIGNED NOT NULL,
  `precio_total` int UNSIGNED NOT NULL
) ;

--
-- Volcado de datos para la tabla `reservas`
--

INSERT INTO `reservas` (`id`, `id_socio`, `id_cancha`, `fecha_hora_inicio`, `fecha_hora_fin`, `estado`, `precio_hora`, `precio_total`) VALUES
(1, 1, 1, '2026-10-15 18:00:00.000000', '2026-10-15 20:00:00.000000', 'confirmada', 1000000, 2000000),
(2, 2, 2, '2026-10-15 19:00:00.000000', '2026-10-15 21:00:00.000000', 'confirmada', 1000000, 2000000),
(3, 3, 4, '2026-10-16 09:00:00.000000', '2026-10-16 10:00:00.000000', 'confirmada', 800000, 800000),
(4, 4, 6, '2026-10-16 15:00:00.000000', '2026-10-16 18:00:00.000000', 'confirmada', 1200000, 3600000),
(5, 5, 3, '2026-10-17 10:00:00.000000', '2026-10-17 12:00:00.000000', 'confirmada', 1500000, 3000000),
(6, 8, 8, '2026-10-17 20:00:00.000000', '2026-10-17 22:00:00.000000', 'confirmada', 1100000, 2200000),
(7, 1, 5, '2026-10-18 08:00:00.000000', '2026-10-18 09:00:00.000000', 'cancelada', 800000, 800000),
(8, 6, 7, '2026-10-18 14:00:00.000000', '2026-10-18 16:00:00.000000', 'cancelada', 900000, 1800000),
(9, 2, 1, '2026-09-01 18:00:00.000000', '2026-09-01 20:00:00.000000', 'finalizada', 1000000, 2000000),
(10, 3, 2, '2026-09-02 10:00:00.000000', '2026-09-02 11:00:00.000000', 'finalizada', 1000000, 1000000),
(11, 4, 6, '2026-09-03 16:00:00.000000', '2026-09-03 18:00:00.000000', 'finalizada', 1200000, 2400000),
(12, 5, 4, '2026-09-04 09:00:00.000000', '2026-09-04 12:00:00.000000', 'finalizada', 800000, 2400000);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `socios`
--

CREATE TABLE `socios` (
  `id` int UNSIGNED NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1'
) ;

--
-- Volcado de datos para la tabla `socios`
--

INSERT INTO `socios` (`id`, `nombre`, `email`, `activo`) VALUES
(1, 'Juan Pérez', 'juan.perez@example.com', 1),
(2, 'María González', 'maria.gonzalez@example.com', 1),
(3, 'Carlos Rodríguez', 'carlos.rodriguez@example.com', 1),
(4, 'Ana Martínez', 'ana.martinez@example.com', 1),
(5, 'Luis Fernández', 'luis.fernandez@example.com', 1),
(6, 'Sofía López', 'sofia.lopez@example.com', 1),
(7, 'Diego Sánchez', 'diego.sanchez@example.com', 0),
(8, 'Laura Díaz', 'laura.diaz@example.com', 1),
(9, 'Pablo Romero', 'pablo.romero@example.com', 1),
(10, 'Carla Sosa', 'carla.sosa@example.com', 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `bloqueos`
--
ALTER TABLE `bloqueos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_bloqueos_cancha_fecha` (`id_cancha`,`fecha`,`hora_inicio`,`hora_fin`);

--
-- Indices de la tabla `canchas`
--
ALTER TABLE `canchas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_canchas_deporte` (`id_deporte`),
  ADD KEY `idx_canchas_activa` (`activa`);

--
-- Indices de la tabla `deportes`
--
ALTER TABLE `deportes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_reservas_cancha_fechas` (`id_cancha`,`fecha_hora_inicio`,`fecha_hora_fin`,`estado`),
  ADD KEY `idx_reservas_socio_fechas` (`id_socio`,`fecha_hora_inicio`,`fecha_hora_fin`,`estado`),
  ADD KEY `idx_reservas_estado` (`estado`);

--
-- Indices de la tabla `socios`
--
ALTER TABLE `socios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_socios_activo` (`activo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `bloqueos`
--
ALTER TABLE `bloqueos`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `canchas`
--
ALTER TABLE `canchas`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `deportes`
--
ALTER TABLE `deportes`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `reservas`
--
ALTER TABLE `reservas`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `socios`
--
ALTER TABLE `socios`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `bloqueos`
--
ALTER TABLE `bloqueos`
  ADD CONSTRAINT `fk_bloqueos_cancha` FOREIGN KEY (`id_cancha`) REFERENCES `canchas` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Filtros para la tabla `canchas`
--
ALTER TABLE `canchas`
  ADD CONSTRAINT `fk_canchas_deporte` FOREIGN KEY (`id_deporte`) REFERENCES `deportes` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Filtros para la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD CONSTRAINT `fk_reservas_cancha` FOREIGN KEY (`id_cancha`) REFERENCES `canchas` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_reservas_socio` FOREIGN KEY (`id_socio`) REFERENCES `socios` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
