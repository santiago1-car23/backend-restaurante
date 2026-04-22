# Documentación: Opción de Voz en la App (Expo)

Este documento explica cómo funciona la opción de voz en la aplicación móvil (Expo) y en qué archivos/carpetas se implementa, para que cualquier IA o desarrollador pueda entender y extender el sistema.

## Estructura de Carpetas y Archivos

La funcionalidad de voz está centralizada en la carpeta:

- `my-expo-app/features/voice/`

Archivos principales:
- `components/VoiceCaptureButton.tsx`: Botón para activar la captura de voz.
- `components/VoiceOrderPreviewModal.tsx`: Modal para mostrar y confirmar el pedido interpretado por voz.
- `hooks/useVoiceOrder.ts`: Hook principal que orquesta el flujo de captura, interpretación y envío del pedido por voz.
- `services/speechService.ts`: Abstracción sobre el reconocimiento de voz (usa `expo-speech-recognition`).
- `services/voiceCatalogMatcher.ts`: Lógica para interpretar el texto capturado y mapearlo a productos, corrientes, desayunos, etc.
- `services/voiceOrderExecutor.ts`: Toma los ítems interpretados y los envía como pedido real al backend.
- `types.ts`: Tipos TypeScript para los datos de voz.

## Flujo General

1. **Captura de voz**
   - El usuario mantiene presionado el `VoiceCaptureButton`.
   - Se inicia la escucha usando `speechService.startLiveListening()`.
   - Al soltar, se detiene la escucha y se obtiene el texto transcrito.

2. **Interpretación del texto**
   - El texto transcrito se pasa a `parseVoiceOrder` (en `voiceCatalogMatcher.ts`).
   - Se extraen productos, cantidades, notas, etc., usando reglas y palabras clave.
   - El resultado es un arreglo de `VoiceOrderItem`.

3. **Vista previa y confirmación**
   - El usuario ve el resultado en `VoiceOrderPreviewModal`.
   - Puede editar el texto, volver a interpretar o confirmar el pedido.

4. **Ejecución del pedido**
   - Al confirmar, el hook `useVoiceOrder` llama a `executeVoiceOrder`.
   - Se construye el payload y se envía al backend (servicio de pedidos).

## Detalles Técnicos

- **Reconocimiento de voz:**
  - Implementado en `speechService.ts` usando `expo-speech-recognition`.
  - Maneja errores comunes (sin permisos, sin voz detectada, etc.).

- **Interpretación:**
  - `voiceCatalogMatcher.ts` normaliza el texto, tokeniza, y busca coincidencias con productos/categorías del catálogo.
  - Soporta palabras clave, cantidades en texto ("dos", "tres"), modificadores ("sin", "extra", etc.).

- **Envío de pedido:**
  - `voiceOrderExecutor.ts` convierte los ítems en payloads específicos según el tipo (producto, corriente, desayuno) y los envía usando el servicio de pedidos.

- **Tipos:**
  - `types.ts` define los tipos de datos para los ítems de voz y el resultado del parseo.

## Extensión y Mantenimiento

- Para agregar nuevos tipos de pedidos o reglas de interpretación, modificar `voiceCatalogMatcher.ts` y actualizar los tipos en `types.ts`.
- Para cambiar la UI, editar los componentes en `components/`.
- Para adaptar el flujo, modificar el hook `useVoiceOrder.ts`.

---

Cualquier IA puede seguir este flujo para entender, modificar o extender la funcionalidad de voz en la app Expo.