import { useState, useCallback } from 'react';
import pedidosService, { Pedido } from '../services/pedidosService';

export default function usePedidos() {
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 12;

  const fetchPedidos = useCallback(async (preserveLoaded = true) => {
    setLoading(true);
    setError(null);
    try {
      const currentPage = preserveLoaded ? page : 1;
      const data = await pedidosService.getPedidos(1, currentPage * pageSize);
      setPedidos(data.items);
      setPage(currentPage);
      setHasNext(data.hasNext);
      setTotalCount(data.count);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Error al cargar pedidos');
      setPedidos([]);
      setPage(1);
      setHasNext(false);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, [page]);

  const fetchMorePedidos = useCallback(async () => {
    if (loading || loadingMore || !hasNext) {
      return;
    }

    setLoadingMore(true);
    try {
      const nextPage = page + 1;
      const data = await pedidosService.getPedidos(nextPage, pageSize);
      setPedidos(current => [...current, ...data.items]);
      setPage(nextPage);
      setHasNext(data.hasNext);
      setTotalCount(data.count);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Error al cargar más pedidos');
    } finally {
      setLoadingMore(false);
    }
  }, [hasNext, loading, loadingMore, page]);

  const fetchLessPedidos = useCallback(async () => {
    if (loading || loadingMore || page <= 1) {
      return;
    }

    setLoadingMore(true);
    setError(null);
    try {
      const previousPage = page - 1;
      const data = await pedidosService.getPedidos(1, previousPage * pageSize);
      setPedidos(data.items);
      setPage(previousPage);
      setHasNext(data.hasNext);
      setTotalCount(data.count);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Error al cargar menos pedidos');
    } finally {
      setLoadingMore(false);
    }
  }, [loading, loadingMore, page]);

  const patchPedido = useCallback((pedidoActualizado: Pedido) => {
    setPedidos(current =>
      current.map(pedido =>
        pedido.id === pedidoActualizado.id
          ? { ...pedido, ...pedidoActualizado }
          : pedido
      )
    );
  }, []);

  return {
    pedidos,
    loading,
    loadingMore,
    hasNext,
    totalCount,
    error,
    fetchPedidos,
    fetchMorePedidos,
    fetchLessPedidos,
    patchPedido,
    page,
  };
}
