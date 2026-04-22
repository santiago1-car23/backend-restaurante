# Expo App

Aplicacion movil en Expo para pedidos, detalle de ordenes y sincronizacion con el backend Django del proyecto.

## Scripts

- `npm start`
- `npm run android`
- `npm run ios`
- `npm run web`
- `npm run lint`

## Estructura

- `app/`: rutas y pantallas con Expo Router
- `features/`: modulos por dominio (`pedidos`, `detalle`, `ui`)
- `context/`: estado global como autenticacion
- `constants/`: colores, API y configuraciones compartidas
- `hooks/`: hooks globales de la app

## Backend

La app consume la API Django definida en `constants/api.ts`.
