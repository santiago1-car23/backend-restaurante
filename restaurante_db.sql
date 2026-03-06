-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 08-01-2026 a las 19:10:04
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `restaurante_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add Restaurante', 7, 'add_restaurante'),
(26, 'Can change Restaurante', 7, 'change_restaurante'),
(27, 'Can delete Restaurante', 7, 'delete_restaurante'),
(28, 'Can view Restaurante', 7, 'view_restaurante'),
(29, 'Can add Rol', 8, 'add_rol'),
(30, 'Can change Rol', 8, 'change_rol'),
(31, 'Can delete Rol', 8, 'delete_rol'),
(32, 'Can view Rol', 8, 'view_rol'),
(33, 'Can add Empleado', 9, 'add_empleado'),
(34, 'Can change Empleado', 9, 'change_empleado'),
(35, 'Can delete Empleado', 9, 'delete_empleado'),
(36, 'Can view Empleado', 9, 'view_empleado'),
(37, 'Can add Notificación', 10, 'add_notificacion'),
(38, 'Can change Notificación', 10, 'change_notificacion'),
(39, 'Can delete Notificación', 10, 'delete_notificacion'),
(40, 'Can view Notificación', 10, 'view_notificacion'),
(41, 'Can add Categoría', 11, 'add_categoria'),
(42, 'Can change Categoría', 11, 'change_categoria'),
(43, 'Can delete Categoría', 11, 'delete_categoria'),
(44, 'Can view Categoría', 11, 'view_categoria'),
(45, 'Can add Producto', 12, 'add_producto'),
(46, 'Can change Producto', 12, 'change_producto'),
(47, 'Can delete Producto', 12, 'delete_producto'),
(48, 'Can view Producto', 12, 'view_producto'),
(49, 'Can add Menú diario', 13, 'add_menudiario'),
(50, 'Can change Menú diario', 13, 'change_menudiario'),
(51, 'Can delete Menú diario', 13, 'delete_menudiario'),
(52, 'Can view Menú diario', 13, 'view_menudiario'),
(53, 'Can add Mesa', 14, 'add_mesa'),
(54, 'Can change Mesa', 14, 'change_mesa'),
(55, 'Can delete Mesa', 14, 'delete_mesa'),
(56, 'Can view Mesa', 14, 'view_mesa'),
(57, 'Can add Pedido', 15, 'add_pedido'),
(58, 'Can change Pedido', 15, 'change_pedido'),
(59, 'Can delete Pedido', 15, 'delete_pedido'),
(60, 'Can view Pedido', 15, 'view_pedido'),
(61, 'Can add Detalle de Pedido', 16, 'add_detallepedido'),
(62, 'Can change Detalle de Pedido', 16, 'change_detallepedido'),
(63, 'Can delete Detalle de Pedido', 16, 'delete_detallepedido'),
(64, 'Can view Detalle de Pedido', 16, 'view_detallepedido'),
(65, 'Can add Factura', 17, 'add_factura'),
(66, 'Can change Factura', 17, 'change_factura'),
(67, 'Can delete Factura', 17, 'delete_factura'),
(68, 'Can view Factura', 17, 'view_factura'),
(69, 'Can add Sesión de caja', 18, 'add_cajasesion'),
(70, 'Can change Sesión de caja', 18, 'change_cajasesion'),
(71, 'Can delete Sesión de caja', 18, 'delete_cajasesion'),
(72, 'Can view Sesión de caja', 18, 'view_cajasesion'),
(73, 'Can add Movimiento de caja', 19, 'add_movimientocaja'),
(74, 'Can change Movimiento de caja', 19, 'change_movimientocaja'),
(75, 'Can delete Movimiento de caja', 19, 'delete_movimientocaja'),
(76, 'Can view Movimiento de caja', 19, 'view_movimientocaja'),
(77, 'Can add Ingrediente', 20, 'add_ingrediente'),
(78, 'Can change Ingrediente', 20, 'change_ingrediente'),
(79, 'Can delete Ingrediente', 20, 'delete_ingrediente'),
(80, 'Can view Ingrediente', 20, 'view_ingrediente'),
(81, 'Can add Movimiento de Inventario', 21, 'add_movimientoinventario'),
(82, 'Can change Movimiento de Inventario', 21, 'change_movimientoinventario'),
(83, 'Can delete Movimiento de Inventario', 21, 'delete_movimientoinventario'),
(84, 'Can view Movimiento de Inventario', 21, 'view_movimientoinventario'),
(85, 'Can add Teléfono del negocio', 22, 'add_telefononegocio'),
(86, 'Can change Teléfono del negocio', 22, 'change_telefononegocio'),
(87, 'Can delete Teléfono del negocio', 22, 'delete_telefononegocio'),
(88, 'Can view Teléfono del negocio', 22, 'view_telefononegocio'),
(89, 'Can add Proveedor', 23, 'add_proveedor'),
(90, 'Can change Proveedor', 23, 'change_proveedor'),
(91, 'Can delete Proveedor', 23, 'delete_proveedor'),
(92, 'Can view Proveedor', 23, 'view_proveedor');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$600000$j4WQoA3OwhmlqqwI2HCSxR$wLJTqIZWq3OKQ0I1Ab5E1LeuN7+Bwvo22PEkZHpwt6s=', '2026-01-04 22:29:35.540310', 1, 'santi', '', '', '', 1, 1, '2026-01-04 22:28:55.213316'),
(2, 'pbkdf2_sha256$600000$Sbbe5D7eZelMW8nI3ZfTuC$8Xiuph6anBz8TWnbdydhgyAC+WjXEXwdnlKknGGGFdE=', '2026-01-06 21:47:27.695386', 1, 'adminrest1', '', '', '', 1, 1, '2026-01-04 22:32:12.327593'),
(3, 'pbkdf2_sha256$600000$jk71tIMVkYSIldTVLXsmuO$iIE7mgCeQf/xKX3QFnt+dZl4c7Ju+voM2uRKTNyMIdw=', '2026-01-06 21:48:00.812995', 0, 'mesero_restaurante', '', '', '', 0, 1, '2026-01-04 22:33:26.519863'),
(4, 'pbkdf2_sha256$600000$jpiYYN6I7bD4mA5jnpM44s$KVyQtB7WO/pNMNCeUmDT/FjKuWxuidILsHNqO3Egof0=', '2026-01-06 21:51:09.186197', 0, 'cocinero_restaurante', '', '', '', 0, 1, '2026-01-04 22:34:01.389975'),
(5, 'pbkdf2_sha256$600000$vDGaAtRC74bClu7ufw7eTp$hOU/lgVAh1kLwgsPic5xVRTAgR2iaw/aQmMGs0+dAMo=', '2026-01-04 23:56:06.653288', 1, 'adminrest2', '', '', '', 1, 1, '2026-01-04 22:35:11.322562'),
(6, 'pbkdf2_sha256$600000$lOP9AuS8t24r7a5WNKEvmg$+Wg8JOmMrbTZ8yUWw3MqJY9/ejEQoboCy7UlDxInYnw=', NULL, 0, 'restcocinero_2', '', '', '', 0, 1, '2026-01-04 22:36:12.968977'),
(7, 'pbkdf2_sha256$600000$mFvqT0SMfn7mzoTIKgTn0x$vharrRFNf+J6P4ZxGYk19g3OLNPKz4WHtgbsdYr+Fis=', NULL, 0, 'restmesero_2', '', '', '', 0, 1, '2026-01-04 22:36:40.279340');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `caja_cajasesion`
--

CREATE TABLE `caja_cajasesion` (
  `id` bigint(20) NOT NULL,
  `fecha_apertura` datetime(6) NOT NULL,
  `fecha_cierre` datetime(6) DEFAULT NULL,
  `estado` varchar(10) NOT NULL,
  `saldo_inicial` decimal(10,2) NOT NULL,
  `saldo_final` decimal(10,2) DEFAULT NULL,
  `observaciones` longtext NOT NULL,
  `usuario_apertura_id` int(11) DEFAULT NULL,
  `usuario_cierre_id` int(11) DEFAULT NULL,
  `salidas` decimal(10,2) NOT NULL,
  `entradas_extra` decimal(10,2) NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `caja_factura`
--

CREATE TABLE `caja_factura` (
  `id` bigint(20) NOT NULL,
  `numero_factura` varchar(20) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `metodo_pago` varchar(15) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `impuesto` decimal(10,2) NOT NULL,
  `descuento` decimal(10,2) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `cliente_nombre` varchar(200) NOT NULL,
  `cliente_nit` varchar(20) NOT NULL,
  `cajero_id` int(11) DEFAULT NULL,
  `pedido_id` bigint(20) NOT NULL,
  `sesion_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `caja_movimientocaja`
--

CREATE TABLE `caja_movimientocaja` (
  `id` bigint(20) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `concepto` varchar(255) NOT NULL,
  `sesion_id` bigint(20) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contactos_proveedor`
--

CREATE TABLE `contactos_proveedor` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `telefono` varchar(30) NOT NULL,
  `telefono_secundario` varchar(30) NOT NULL,
  `email` varchar(254) DEFAULT NULL,
  `direccion` longtext DEFAULT NULL,
  `tipo` varchar(20) NOT NULL,
  `notas` longtext NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `creado_en` datetime(6) NOT NULL,
  `actualizado_en` datetime(6) NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contactos_telefononegocio`
--

CREATE TABLE `contactos_telefononegocio` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `numero` varchar(30) NOT NULL,
  `notas` longtext NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `creado_en` datetime(6) NOT NULL,
  `actualizado_en` datetime(6) NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `core_restaurante`
--

CREATE TABLE `core_restaurante` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `nit` varchar(50) NOT NULL,
  `codigo_cliente` varchar(50) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin_licencia` date DEFAULT NULL,
  `creado_en` datetime(6) NOT NULL,
  `actualizado_en` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `core_restaurante`
--

INSERT INTO `core_restaurante` (`id`, `nombre`, `nit`, `codigo_cliente`, `activo`, `fecha_inicio`, `fecha_fin_licencia`, `creado_en`, `actualizado_en`) VALUES
(1, 'restaurante1', '', 'REST01', 1, NULL, NULL, '2026-01-04 22:32:36.658668', '2026-01-04 22:32:36.658668'),
(2, 'restaurante2', '', 'REST02', 1, NULL, NULL, '2026-01-04 22:34:46.914111', '2026-01-04 22:34:46.914111');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2026-01-04 22:30:13.676338', '1', 'Administrador', 1, '[{\"added\": {}}]', 8, 1),
(2, '2026-01-04 22:30:20.176003', '2', 'Mesero', 1, '[{\"added\": {}}]', 8, 1),
(3, '2026-01-04 22:30:25.495430', '3', 'Cocinero', 1, '[{\"added\": {}}]', 8, 1),
(4, '2026-01-04 22:32:12.762027', '2', 'adminrest1', 1, '[{\"added\": {}}]', 4, 1),
(5, '2026-01-04 22:32:36.659764', '1', 'restaurante1 (REST01)', 1, '[{\"added\": {}}]', 7, 1),
(6, '2026-01-04 22:32:43.515454', '1', ' - Administrador', 1, '[{\"added\": {}}]', 9, 1),
(7, '2026-01-04 22:33:26.974750', '3', 'mesero_restaurante', 1, '[{\"added\": {}}]', 4, 1),
(8, '2026-01-04 22:33:34.061904', '2', ' - Mesero', 1, '[{\"added\": {}}]', 9, 1),
(9, '2026-01-04 22:34:01.847610', '4', 'cocinero_restaurante', 1, '[{\"added\": {}}]', 4, 1),
(10, '2026-01-04 22:34:17.734483', '3', ' - Cocinero', 1, '[{\"added\": {}}]', 9, 1),
(11, '2026-01-04 22:34:46.914628', '2', 'restaurante2 (REST02)', 1, '[{\"added\": {}}]', 7, 1),
(12, '2026-01-04 22:35:11.814489', '5', 'adminrest2', 1, '[{\"added\": {}}]', 4, 1),
(13, '2026-01-04 22:35:54.264467', '4', ' - Administrador', 1, '[{\"added\": {}}]', 9, 1),
(14, '2026-01-04 22:36:13.506929', '6', 'restcocinero_2', 1, '[{\"added\": {}}]', 4, 1),
(15, '2026-01-04 22:36:22.682683', '5', ' - Cocinero', 1, '[{\"added\": {}}]', 9, 1),
(16, '2026-01-04 22:36:40.859764', '7', 'restmesero_2', 1, '[{\"added\": {}}]', 4, 1),
(17, '2026-01-04 22:36:48.474341', '6', ' - Mesero', 1, '[{\"added\": {}}]', 9, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(18, 'caja', 'cajasesion'),
(17, 'caja', 'factura'),
(19, 'caja', 'movimientocaja'),
(23, 'contactos', 'proveedor'),
(22, 'contactos', 'telefononegocio'),
(5, 'contenttypes', 'contenttype'),
(7, 'core', 'restaurante'),
(20, 'inventario', 'ingrediente'),
(21, 'inventario', 'movimientoinventario'),
(11, 'menu', 'categoria'),
(13, 'menu', 'menudiario'),
(12, 'menu', 'producto'),
(14, 'mesas', 'mesa'),
(16, 'pedidos', 'detallepedido'),
(15, 'pedidos', 'pedido'),
(6, 'sessions', 'session'),
(9, 'usuarios', 'empleado'),
(10, 'usuarios', 'notificacion'),
(8, 'usuarios', 'rol');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-01-04 22:22:23.693040'),
(2, 'auth', '0001_initial', '2026-01-04 22:22:24.181980'),
(3, 'admin', '0001_initial', '2026-01-04 22:22:24.288998'),
(4, 'admin', '0002_logentry_remove_auto_add', '2026-01-04 22:22:24.299630'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2026-01-04 22:22:24.307157'),
(6, 'contenttypes', '0002_remove_content_type_name', '2026-01-04 22:22:24.370549'),
(7, 'auth', '0002_alter_permission_name_max_length', '2026-01-04 22:22:24.421281'),
(8, 'auth', '0003_alter_user_email_max_length', '2026-01-04 22:22:24.437971'),
(9, 'auth', '0004_alter_user_username_opts', '2026-01-04 22:22:24.447071'),
(10, 'auth', '0005_alter_user_last_login_null', '2026-01-04 22:22:24.503536'),
(11, 'auth', '0006_require_contenttypes_0002', '2026-01-04 22:22:24.507555'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2026-01-04 22:22:24.520775'),
(13, 'auth', '0008_alter_user_username_max_length', '2026-01-04 22:22:24.540009'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2026-01-04 22:22:24.556879'),
(15, 'auth', '0010_alter_group_name_max_length', '2026-01-04 22:22:24.571917'),
(16, 'auth', '0011_update_proxy_permissions', '2026-01-04 22:22:24.585555'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2026-01-04 22:22:24.603361'),
(18, 'core', '0001_initial', '2026-01-04 22:22:24.634897'),
(19, 'mesas', '0001_initial', '2026-01-04 22:22:24.690251'),
(20, 'menu', '0001_initial', '2026-01-04 22:22:24.832214'),
(21, 'pedidos', '0001_initial', '2026-01-04 22:22:25.075092'),
(22, 'pedidos', '0002_detallepedido_servido_alter_detallepedido_id_and_more', '2026-01-04 22:22:25.711426'),
(23, 'pedidos', '0003_alter_pedido_estado', '2026-01-04 22:22:25.723935'),
(24, 'caja', '0001_initial', '2026-01-04 22:22:25.856716'),
(25, 'caja', '0002_cajasesion_factura_sesion', '2026-01-04 22:22:26.102601'),
(26, 'caja', '0003_cajasesion_salidas', '2026-01-04 22:22:26.127551'),
(27, 'caja', '0004_cajasesion_entradas_extra', '2026-01-04 22:22:26.153867'),
(28, 'caja', '0005_movimientocaja', '2026-01-04 22:22:26.291211'),
(29, 'caja', '0006_cajasesion_restaurante', '2026-01-04 22:22:26.355352'),
(30, 'contactos', '0001_initial', '2026-01-04 22:22:26.492759'),
(31, 'contactos', '0002_alter_proveedor_email', '2026-01-04 22:22:26.540029'),
(32, 'contactos', '0003_alter_proveedor_direccion', '2026-01-04 22:22:26.591994'),
(33, 'inventario', '0001_initial', '2026-01-04 22:22:26.733663'),
(34, 'inventario', '0002_alter_ingrediente_id_alter_movimientoinventario_id', '2026-01-04 22:22:27.223395'),
(35, 'inventario', '0003_ingrediente_restaurante', '2026-01-04 22:22:27.288406'),
(36, 'menu', '0002_menudiario_alter_categoria_id_alter_producto_id', '2026-01-04 22:22:27.936460'),
(37, 'menu', '0003_menudiario_desayuno', '2026-01-04 22:22:27.986952'),
(38, 'menu', '0004_menudiario_caldos', '2026-01-04 22:22:28.008926'),
(39, 'menu', '0005_categoria_restaurante_alter_categoria_nombre_and_more', '2026-01-04 22:22:28.365985'),
(40, 'menu', '0006_menudiario_restaurante_alter_menudiario_fecha_and_more', '2026-01-04 22:22:28.544070'),
(41, 'mesas', '0002_alter_mesa_id', '2026-01-04 22:22:28.790102'),
(42, 'mesas', '0003_mesa_restaurante_alter_mesa_numero_and_more', '2026-01-04 22:22:28.969456'),
(43, 'pedidos', '0004_pedido_archivado', '2026-01-04 22:22:28.993198'),
(44, 'pedidos', '0005_pedido_es_extra_alter_pedido_mesa', '2026-01-04 22:22:29.350726'),
(45, 'pedidos', '0006_remove_pedido_es_extra_alter_pedido_mesa', '2026-01-04 22:22:29.554014'),
(46, 'pedidos', '0007_pedido_restaurante', '2026-01-04 22:22:29.628724'),
(47, 'sessions', '0001_initial', '2026-01-04 22:22:29.661988'),
(48, 'usuarios', '0001_initial', '2026-01-04 22:22:29.834338'),
(49, 'usuarios', '0002_alter_empleado_id_alter_rol_id', '2026-01-04 22:22:30.190191'),
(50, 'usuarios', '0003_empleado_restaurante', '2026-01-04 22:22:30.352648'),
(51, 'usuarios', '0004_notificacion', '2026-01-04 22:22:30.420350'),
(52, 'usuarios', '0005_empleado_hora_entrada_empleado_hora_salida', '2026-01-05 20:58:18.144713');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('2zxvutm87s6j7jy5ivskqebyzpt4yxve', '.eJxVjEEOgjAQRe_StWlaYCh16Z4zNNOZwaKmTSisjHcXEha6_e-9_1YBtzWFrcoSZlZX1arL7xaRnpIPwA_M96Kp5HWZoz4UfdKqx8Lyup3u30HCmvYaEEzvpBUrnQU0hn3PntAPjhxTsxPnoRFsQZztIiGhnSYYABywserzBeV_OAY:1vdEuG:NBDqUpLcCH13znf8Ju10bDIT2uhXgDI3_3sBwIskg80', '2026-01-20 21:48:00.821844'),
('dwzn6zo3ly8p0bbg7271olda56k1oc6x', '.eJxVjEEOwiAQRe_C2hCgZUCX7nsGMgyDVA0kpV0Z765NutDtf-_9lwi4rSVsnZcwJ3ERozj9bhHpwXUH6Y711iS1ui5zlLsiD9rl1BI_r4f7d1Cwl2_tGZUid_YpOsPgWQMzaU8OMHP2EYBI2WSNGbTJNCKBR5Uh58GaGMX7AwGnOMk:1vdExJ:ttgTdvAP3CTR2bGGjct70ISLQiKiaIwTkB6OOjReE3Q', '2026-01-20 21:51:09.191405'),
('llinkfdfoxr8pk30xoaiuwpq1cpgxmcn', '.eJxVjMsOwiAQRf-FtSEyEB4u3fsNZJgBqRpISrsy_rtt0oVuzzn3vkXEdalxHXmOE4uLAHH6ZQnpmdsu-IHt3iX1tsxTknsiDzvkrXN-XY_276DiqNvaZNKeCpydDtlwyKhUUYpwo9Z4U8BrBsPOaiBGJA8OyDsbVOBUgvh8AeWPN-M:1vcZsr:ZS6sqJbzTLv8KNHJ_Pe4aq-NikGAf-WpumvIjptmDu8', '2026-01-19 01:59:49.428051'),
('qymjxixdab73blkvde9isjf0uddy15w5', '.eJxVjMsOwiAQRf-FtSEyEB4u3fsNZJgBqRpISrsy_rtt0oVuzzn3vkXEdalxHXmOE4uLAHH6ZQnpmdsu-IHt3iX1tsxTknsiDzvkrXN-XY_276DiqNvaZNKeCpydDtlwyKhUUYpwo9Z4U8BrBsPOaiBGJA8OyDsbVOBUgvh8AeWPN-M:1vcrp8:uEVMzWtIXJwe5sfKuG7uoXRD8TH3t9YG9YaiH-3vJpo', '2026-01-19 21:09:10.279972');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inventario_ingrediente`
--

CREATE TABLE `inventario_ingrediente` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `unidad` varchar(10) NOT NULL,
  `cantidad_actual` decimal(10,2) NOT NULL,
  `cantidad_minima` decimal(10,2) NOT NULL,
  `costo_unitario` decimal(10,2) NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `inventario_ingrediente`
--

INSERT INTO `inventario_ingrediente` (`id`, `nombre`, `unidad`, `cantidad_actual`, `cantidad_minima`, `costo_unitario`, `restaurante_id`) VALUES
(1, 'mojarra', 'unidad', 12.00, 0.00, 23000.00, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inventario_movimientoinventario`
--

CREATE TABLE `inventario_movimientoinventario` (
  `id` bigint(20) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `motivo` varchar(200) NOT NULL,
  `ingrediente_id` bigint(20) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `menu_categoria`
--

CREATE TABLE `menu_categoria` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` longtext NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `menu_categoria`
--

INSERT INTO `menu_categoria` (`id`, `nombre`, `descripcion`, `activo`, `restaurante_id`) VALUES
(1, 'Snacks', '', 1, 1),
(2, 'Postres', '', 1, 1),
(3, 'Platos', '', 1, 1),
(4, 'Bebidas', '', 1, 1),
(5, 'Snacks', '', 1, 2),
(6, 'Postres', '', 1, 2),
(7, 'Platos', '', 1, 2),
(8, 'Bebidas', '', 1, 2),
(9, 'Corriente', '', 1, 1),
(10, 'Desayuno', '', 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `menu_menudiario`
--

CREATE TABLE `menu_menudiario` (
  `id` bigint(20) NOT NULL,
  `fecha` date NOT NULL,
  `sopa` varchar(200) NOT NULL,
  `principios` longtext NOT NULL,
  `proteinas` longtext NOT NULL,
  `acompanante` varchar(200) NOT NULL,
  `limonada` varchar(200) NOT NULL,
  `precio_sopa` decimal(8,2) NOT NULL,
  `precio_bandeja` decimal(8,2) NOT NULL,
  `precio_completo` decimal(8,2) NOT NULL,
  `desayuno_principales` longtext NOT NULL,
  `desayuno_bebidas` longtext NOT NULL,
  `desayuno_acompanante` varchar(200) NOT NULL,
  `precio_desayuno` decimal(8,2) NOT NULL,
  `caldos` longtext NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `menu_menudiario`
--

INSERT INTO `menu_menudiario` (`id`, `fecha`, `sopa`, `principios`, `proteinas`, `acompanante`, `limonada`, `precio_sopa`, `precio_bandeja`, `precio_completo`, `desayuno_principales`, `desayuno_bebidas`, `desayuno_acompanante`, `precio_desayuno`, `caldos`, `restaurante_id`) VALUES
(1, '2026-01-04', '', '', '', '', '', 5000.00, 12000.00, 13000.00, '', '', '', 8000.00, '', 1),
(2, '2026-01-05', '', '', '', '', '', 5000.00, 12000.00, 13000.00, '', '', '', 8000.00, '', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `menu_producto`
--

CREATE TABLE `menu_producto` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `descripcion` longtext NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `imagen` varchar(100) DEFAULT NULL,
  `disponible` tinyint(1) NOT NULL,
  `tiempo_preparacion` int(11) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `categoria_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `menu_producto`
--

INSERT INTO `menu_producto` (`id`, `nombre`, `descripcion`, `precio`, `imagen`, `disponible`, `tiempo_preparacion`, `fecha_creacion`, `categoria_id`) VALUES
(1, 'mojarra', '', 23000.00, '', 1, 15, '2026-01-05 22:42:12.191080', 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mesas_mesa`
--

CREATE TABLE `mesas_mesa` (
  `id` bigint(20) NOT NULL,
  `numero` int(11) NOT NULL,
  `capacidad` int(11) NOT NULL,
  `estado` varchar(10) NOT NULL,
  `ubicacion` varchar(100) NOT NULL,
  `activa` tinyint(1) NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mesas_mesa`
--

INSERT INTO `mesas_mesa` (`id`, `numero`, `capacidad`, `estado`, `ubicacion`, `activa`, `restaurante_id`) VALUES
(1, 1, 4, 'libre', '', 1, 1),
(2, 2, 4, 'libre', '', 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos_detallepedido`
--

CREATE TABLE `pedidos_detallepedido` (
  `id` bigint(20) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `observaciones` varchar(200) NOT NULL,
  `producto_id` bigint(20) NOT NULL,
  `pedido_id` bigint(20) NOT NULL,
  `servido` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos_detallepedido`
--

INSERT INTO `pedidos_detallepedido` (`id`, `cantidad`, `precio_unitario`, `subtotal`, `observaciones`, `producto_id`, `pedido_id`, `servido`) VALUES
(2, 1, 23000.00, 23000.00, '', 1, 3, 1),
(3, 1, 23000.00, 23000.00, '', 1, 4, 1),
(4, 1, 23000.00, 23000.00, '', 1, 4, 1),
(5, 1, 23000.00, 23000.00, '', 1, 5, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos_pedido`
--

CREATE TABLE `pedidos_pedido` (
  `id` bigint(20) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `observaciones` longtext NOT NULL,
  `mesa_id` bigint(20) NOT NULL,
  `mesero_id` int(11) DEFAULT NULL,
  `archivado` tinyint(1) NOT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos_pedido`
--

INSERT INTO `pedidos_pedido` (`id`, `estado`, `fecha_creacion`, `fecha_actualizacion`, `total`, `observaciones`, `mesa_id`, `mesero_id`, `archivado`, `restaurante_id`) VALUES
(3, 'entregado', '2026-01-06 21:49:34.891056', '2026-01-06 21:50:12.178104', 23000.00, '', 1, 2, 0, 1),
(4, 'entregado', '2026-01-06 21:51:21.130767', '2026-01-06 21:51:49.566779', 46000.00, '', 2, 3, 0, 1),
(5, 'entregado', '2026-01-06 21:55:07.022192', '2026-01-06 21:55:33.444742', 23000.00, '', 1, 3, 0, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios_empleado`
--

CREATE TABLE `usuarios_empleado` (
  `id` bigint(20) NOT NULL,
  `telefono` varchar(15) NOT NULL,
  `direccion` longtext NOT NULL,
  `fecha_contratacion` date NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rol_id` bigint(20) DEFAULT NULL,
  `restaurante_id` bigint(20) DEFAULT NULL,
  `hora_entrada` time(6) DEFAULT NULL,
  `hora_salida` time(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios_empleado`
--

INSERT INTO `usuarios_empleado` (`id`, `telefono`, `direccion`, `fecha_contratacion`, `activo`, `user_id`, `rol_id`, `restaurante_id`, `hora_entrada`, `hora_salida`) VALUES
(1, '', '', '2026-01-04', 1, 2, 1, 1, NULL, NULL),
(2, '', '', '2026-01-04', 1, 3, 2, 1, NULL, NULL),
(3, '', '', '2026-01-04', 1, 4, 3, 1, NULL, NULL),
(4, '', '', '2026-01-04', 1, 5, 1, 2, NULL, NULL),
(5, '', '', '2026-01-04', 1, 6, 3, 2, NULL, NULL),
(6, '', '', '2026-01-04', 1, 7, 2, 2, NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios_notificacion`
--

CREATE TABLE `usuarios_notificacion` (
  `id` bigint(20) NOT NULL,
  `mensaje` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `creada` datetime(6) NOT NULL,
  `leida` tinyint(1) NOT NULL,
  `usuario_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios_notificacion`
--

INSERT INTO `usuarios_notificacion` (`id`, `mensaje`, `url`, `creada`, `leida`, `usuario_id`) VALUES
(1, 'Pedido #4 de mesa 2 está listo para servir.', '/pedidos/4/', '2026-01-06 21:51:49.577987', 1, 3),
(2, 'Pedido #5 de mesa 1 está listo para servir.', '/pedidos/5/', '2026-01-06 21:55:33.472775', 1, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios_rol`
--

CREATE TABLE `usuarios_rol` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(20) NOT NULL,
  `descripcion` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios_rol`
--

INSERT INTO `usuarios_rol` (`id`, `nombre`, `descripcion`) VALUES
(1, 'admin', ''),
(2, 'mesero', ''),
(3, 'cocinero', '');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indices de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indices de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `caja_cajasesion`
--
ALTER TABLE `caja_cajasesion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `caja_cajasesion_usuario_apertura_id_e9a916cb_fk_auth_user_id` (`usuario_apertura_id`),
  ADD KEY `caja_cajasesion_usuario_cierre_id_fb0f9068_fk_auth_user_id` (`usuario_cierre_id`),
  ADD KEY `caja_cajasesion_restaurante_id_79209546_fk_core_restaurante_id` (`restaurante_id`);

--
-- Indices de la tabla `caja_factura`
--
ALTER TABLE `caja_factura`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`),
  ADD UNIQUE KEY `pedido_id` (`pedido_id`),
  ADD KEY `caja_factura_cajero_id_d447ed9d_fk_auth_user_id` (`cajero_id`),
  ADD KEY `caja_factura_sesion_id_28aa9170_fk_caja_cajasesion_id` (`sesion_id`);

--
-- Indices de la tabla `caja_movimientocaja`
--
ALTER TABLE `caja_movimientocaja`
  ADD PRIMARY KEY (`id`),
  ADD KEY `caja_movimientocaja_sesion_id_ae2363b6_fk_caja_cajasesion_id` (`sesion_id`),
  ADD KEY `caja_movimientocaja_usuario_id_788e149a_fk_auth_user_id` (`usuario_id`);

--
-- Indices de la tabla `contactos_proveedor`
--
ALTER TABLE `contactos_proveedor`
  ADD PRIMARY KEY (`id`),
  ADD KEY `contactos_proveedor_restaurante_id_fd02f6a5_fk_core_rest` (`restaurante_id`);

--
-- Indices de la tabla `contactos_telefononegocio`
--
ALTER TABLE `contactos_telefononegocio`
  ADD PRIMARY KEY (`id`),
  ADD KEY `contactos_telefonone_restaurante_id_f80a3206_fk_core_rest` (`restaurante_id`);

--
-- Indices de la tabla `core_restaurante`
--
ALTER TABLE `core_restaurante`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `codigo_cliente` (`codigo_cliente`);

--
-- Indices de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indices de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indices de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indices de la tabla `inventario_ingrediente`
--
ALTER TABLE `inventario_ingrediente`
  ADD PRIMARY KEY (`id`),
  ADD KEY `inventario_ingredien_restaurante_id_c2de3230_fk_core_rest` (`restaurante_id`);

--
-- Indices de la tabla `inventario_movimientoinventario`
--
ALTER TABLE `inventario_movimientoinventario`
  ADD PRIMARY KEY (`id`),
  ADD KEY `inventario_movimient_usuario_id_6ba25fdb_fk_auth_user` (`usuario_id`),
  ADD KEY `inventario_movimientoinventario_ingrediente_id_53e09074_fk` (`ingrediente_id`);

--
-- Indices de la tabla `menu_categoria`
--
ALTER TABLE `menu_categoria`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `menu_categoria_restaurante_id_nombre_58c14848_uniq` (`restaurante_id`,`nombre`);

--
-- Indices de la tabla `menu_menudiario`
--
ALTER TABLE `menu_menudiario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `menu_menudiario_restaurante_id_fecha_784f651c_uniq` (`restaurante_id`,`fecha`);

--
-- Indices de la tabla `menu_producto`
--
ALTER TABLE `menu_producto`
  ADD PRIMARY KEY (`id`),
  ADD KEY `menu_producto_categoria_id_3f2522d6_fk` (`categoria_id`);

--
-- Indices de la tabla `mesas_mesa`
--
ALTER TABLE `mesas_mesa`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `mesas_mesa_restaurante_id_numero_8d0f4005_uniq` (`restaurante_id`,`numero`);

--
-- Indices de la tabla `pedidos_detallepedido`
--
ALTER TABLE `pedidos_detallepedido`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pedidos_detallepedido_pedido_id_37ae55c6_fk` (`pedido_id`),
  ADD KEY `pedidos_detallepedido_producto_id_fb78018a_fk` (`producto_id`);

--
-- Indices de la tabla `pedidos_pedido`
--
ALTER TABLE `pedidos_pedido`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pedidos_pedido_mesero_id_725bd811_fk_auth_user_id` (`mesero_id`),
  ADD KEY `pedidos_pedido_mesa_id_de63537a_fk_mesas_mesa_id` (`mesa_id`),
  ADD KEY `pedidos_pedido_restaurante_id_84ce6c3c_fk_core_restaurante_id` (`restaurante_id`);

--
-- Indices de la tabla `usuarios_empleado`
--
ALTER TABLE `usuarios_empleado`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `usuarios_empleado_rol_id_cdc93beb_fk` (`rol_id`),
  ADD KEY `usuarios_empleado_restaurante_id_6b2a0393_fk_core_restaurante_id` (`restaurante_id`);

--
-- Indices de la tabla `usuarios_notificacion`
--
ALTER TABLE `usuarios_notificacion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuarios_notificacion_usuario_id_bbfd603a_fk_auth_user_id` (`usuario_id`);

--
-- Indices de la tabla `usuarios_rol`
--
ALTER TABLE `usuarios_rol`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=93;

--
-- AUTO_INCREMENT de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `caja_cajasesion`
--
ALTER TABLE `caja_cajasesion`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `caja_factura`
--
ALTER TABLE `caja_factura`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `caja_movimientocaja`
--
ALTER TABLE `caja_movimientocaja`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `contactos_proveedor`
--
ALTER TABLE `contactos_proveedor`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `contactos_telefononegocio`
--
ALTER TABLE `contactos_telefononegocio`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `core_restaurante`
--
ALTER TABLE `core_restaurante`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `inventario_ingrediente`
--
ALTER TABLE `inventario_ingrediente`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `inventario_movimientoinventario`
--
ALTER TABLE `inventario_movimientoinventario`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `menu_categoria`
--
ALTER TABLE `menu_categoria`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `menu_menudiario`
--
ALTER TABLE `menu_menudiario`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `menu_producto`
--
ALTER TABLE `menu_producto`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `mesas_mesa`
--
ALTER TABLE `mesas_mesa`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `pedidos_detallepedido`
--
ALTER TABLE `pedidos_detallepedido`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `pedidos_pedido`
--
ALTER TABLE `pedidos_pedido`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `usuarios_empleado`
--
ALTER TABLE `usuarios_empleado`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `usuarios_notificacion`
--
ALTER TABLE `usuarios_notificacion`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `usuarios_rol`
--
ALTER TABLE `usuarios_rol`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Filtros para la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `caja_cajasesion`
--
ALTER TABLE `caja_cajasesion`
  ADD CONSTRAINT `caja_cajasesion_restaurante_id_79209546_fk_core_restaurante_id` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`),
  ADD CONSTRAINT `caja_cajasesion_usuario_apertura_id_e9a916cb_fk_auth_user_id` FOREIGN KEY (`usuario_apertura_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `caja_cajasesion_usuario_cierre_id_fb0f9068_fk_auth_user_id` FOREIGN KEY (`usuario_cierre_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `caja_factura`
--
ALTER TABLE `caja_factura`
  ADD CONSTRAINT `caja_factura_cajero_id_d447ed9d_fk_auth_user_id` FOREIGN KEY (`cajero_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `caja_factura_pedido_id_1349c1f7_fk_pedidos_pedido_id` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos_pedido` (`id`),
  ADD CONSTRAINT `caja_factura_sesion_id_28aa9170_fk_caja_cajasesion_id` FOREIGN KEY (`sesion_id`) REFERENCES `caja_cajasesion` (`id`);

--
-- Filtros para la tabla `caja_movimientocaja`
--
ALTER TABLE `caja_movimientocaja`
  ADD CONSTRAINT `caja_movimientocaja_sesion_id_ae2363b6_fk_caja_cajasesion_id` FOREIGN KEY (`sesion_id`) REFERENCES `caja_cajasesion` (`id`),
  ADD CONSTRAINT `caja_movimientocaja_usuario_id_788e149a_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `contactos_proveedor`
--
ALTER TABLE `contactos_proveedor`
  ADD CONSTRAINT `contactos_proveedor_restaurante_id_fd02f6a5_fk_core_rest` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`);

--
-- Filtros para la tabla `contactos_telefononegocio`
--
ALTER TABLE `contactos_telefononegocio`
  ADD CONSTRAINT `contactos_telefonone_restaurante_id_f80a3206_fk_core_rest` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `inventario_ingrediente`
--
ALTER TABLE `inventario_ingrediente`
  ADD CONSTRAINT `inventario_ingredien_restaurante_id_c2de3230_fk_core_rest` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`);

--
-- Filtros para la tabla `inventario_movimientoinventario`
--
ALTER TABLE `inventario_movimientoinventario`
  ADD CONSTRAINT `inventario_movimient_usuario_id_6ba25fdb_fk_auth_user` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `inventario_movimientoinventario_ingrediente_id_53e09074_fk` FOREIGN KEY (`ingrediente_id`) REFERENCES `inventario_ingrediente` (`id`);

--
-- Filtros para la tabla `menu_categoria`
--
ALTER TABLE `menu_categoria`
  ADD CONSTRAINT `menu_categoria_restaurante_id_068e5819_fk_core_restaurante_id` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`);

--
-- Filtros para la tabla `menu_menudiario`
--
ALTER TABLE `menu_menudiario`
  ADD CONSTRAINT `menu_menudiario_restaurante_id_49f4b97f_fk_core_restaurante_id` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`);

--
-- Filtros para la tabla `menu_producto`
--
ALTER TABLE `menu_producto`
  ADD CONSTRAINT `menu_producto_categoria_id_3f2522d6_fk` FOREIGN KEY (`categoria_id`) REFERENCES `menu_categoria` (`id`);

--
-- Filtros para la tabla `mesas_mesa`
--
ALTER TABLE `mesas_mesa`
  ADD CONSTRAINT `mesas_mesa_restaurante_id_65230667_fk_core_restaurante_id` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`);

--
-- Filtros para la tabla `pedidos_detallepedido`
--
ALTER TABLE `pedidos_detallepedido`
  ADD CONSTRAINT `pedidos_detallepedido_pedido_id_37ae55c6_fk` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos_pedido` (`id`),
  ADD CONSTRAINT `pedidos_detallepedido_producto_id_fb78018a_fk` FOREIGN KEY (`producto_id`) REFERENCES `menu_producto` (`id`);

--
-- Filtros para la tabla `pedidos_pedido`
--
ALTER TABLE `pedidos_pedido`
  ADD CONSTRAINT `pedidos_pedido_mesa_id_de63537a_fk_mesas_mesa_id` FOREIGN KEY (`mesa_id`) REFERENCES `mesas_mesa` (`id`),
  ADD CONSTRAINT `pedidos_pedido_mesero_id_725bd811_fk_auth_user_id` FOREIGN KEY (`mesero_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `pedidos_pedido_restaurante_id_84ce6c3c_fk_core_restaurante_id` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`);

--
-- Filtros para la tabla `usuarios_empleado`
--
ALTER TABLE `usuarios_empleado`
  ADD CONSTRAINT `usuarios_empleado_restaurante_id_6b2a0393_fk_core_restaurante_id` FOREIGN KEY (`restaurante_id`) REFERENCES `core_restaurante` (`id`),
  ADD CONSTRAINT `usuarios_empleado_rol_id_cdc93beb_fk` FOREIGN KEY (`rol_id`) REFERENCES `usuarios_rol` (`id`),
  ADD CONSTRAINT `usuarios_empleado_user_id_4c30305b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `usuarios_notificacion`
--
ALTER TABLE `usuarios_notificacion`
  ADD CONSTRAINT `usuarios_notificacion_usuario_id_bbfd603a_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
