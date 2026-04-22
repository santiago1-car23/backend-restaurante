import { useCallback, useMemo, useState } from 'react';
import type { CatalogoPedido, Pedido } from '../../pedidos/services/pedidosService';
import { parseVoiceOrder } from '../services/voiceCatalogMatcher';
import { executeVoiceOrder } from '../services/voiceOrderExecutor';

type Params = {
  pedidoId: number | null;
  catalogo: CatalogoPedido | null;
  onApplied: (pedido: Pedido) => void;
  onError: (message: string) => void;
};

export function useVoiceOrder({ pedidoId, catalogo, onApplied, onError }: Params) {
  const [visible, setVisible] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interpreting, setInterpreting] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const parsed = useMemo(() => parseVoiceOrder(transcript, catalogo), [catalogo, transcript]);

  const open = useCallback(() => setVisible(true), []);

  const close = useCallback(() => {
    setVisible(false);
    setInterpreting(false);
    setSubmitting(false);
  }, []);

  const reset = useCallback(() => {
    setTranscript('');
    setInterpreting(false);
  }, []);

  const interpret = useCallback(() => {
    setInterpreting(true);
  }, []);

  const confirm = useCallback(async () => {
    if (!pedidoId || !parsed.items.length) {
      return;
    }

    setSubmitting(true);
    try {
      const updatedPedido = await executeVoiceOrder(pedidoId, parsed.items);
      if (updatedPedido) {
        onApplied(updatedPedido);
      }
      close();
      reset();
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.producto_id?.[0] ||
        err?.response?.data?.cantidad?.[0] ||
        'No se pudo agregar el pedido por voz.';
      onError(message);
    } finally {
      setSubmitting(false);
    }
  }, [close, onApplied, onError, parsed.items, pedidoId, reset]);

  return {
    visible,
    open,
    close,
    transcript,
    setTranscript,
    interpret,
    interpreting,
    submitting,
    parsed,
    confirm,
    reset,
  };
}
