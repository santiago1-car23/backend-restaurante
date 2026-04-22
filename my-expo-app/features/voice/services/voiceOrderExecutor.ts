import pedidosService, { Pedido } from '../../pedidos/services/pedidosService';
import type { VoiceOrderItem } from '../types';

const buildProductoPayload = (item: Extract<VoiceOrderItem, { kind: 'producto' }>) => ({
  producto_id: item.productoId,
  cantidad: item.quantity,
  observaciones: item.note || '',
});

const buildCorrientePayload = (item: Extract<VoiceOrderItem, { kind: 'corriente' }>) => ({
  cantidad: item.quantity,
  proteina: item.proteina || '',
  sopa: item.sopa || '',
  principio: item.principio || '',
  acompanante: item.acompanante || '',
  observaciones: item.note || '',
});

const buildDesayunoPayload = (item: Extract<VoiceOrderItem, { kind: 'desayuno' }>) => ({
  cantidad: item.quantity,
  principal: item.principal || '',
  bebida: item.bebida || '',
  acompanante: item.acompanante || '',
  observaciones: item.note || '',
});

export const executeVoiceOrder = async (
  pedidoId: number,
  items: VoiceOrderItem[]
): Promise<Pedido | null> => {
  if (!pedidoId || !items.length) {
    return null;
  }

  let latestPedido: Pedido | null = null;

  for (const item of items) {
    if (!item.quantity || item.quantity <= 0) {
      continue;
    }

    if (item.kind === 'producto') {
      latestPedido = await pedidosService.agregarDetalle(
        pedidoId,
        buildProductoPayload(item)
      );
      continue;
    }

    if (item.kind === 'corriente') {
      latestPedido = await pedidosService.agregarCorriente(
        pedidoId,
        buildCorrientePayload(item)
      );
      continue;
    }

    latestPedido = await pedidosService.agregarDesayuno(
      pedidoId,
      buildDesayunoPayload(item)
    );
  }

  return latestPedido;
};
