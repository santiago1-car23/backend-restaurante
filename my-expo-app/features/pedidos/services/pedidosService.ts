import API from '../../../constants/api';

export interface Mesa {
  id: number;
  numero: number;
  capacidad: number;
  estado: string;
  estado_display: string;
  pedido_activo_id?: number | null;
}

export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string;
  activo: boolean;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  precio: string | number;
  precio_formateado?: string;
  categoria: number | null;
  categoria_nombre: string;
  disponible: boolean;
  tiempo_preparacion: number;
}

export interface DetallePedido {
  id: number;
  pedido?: number;
  producto: number;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: string | number;
  precio_unitario_formateado?: string;
  subtotal: string | number;
  subtotal_formateado?: string;
  observaciones: string;
  servido: boolean;
}

export interface Pedido {
  id: number;
  mesa: number;
  mesa_numero: number;
  mesero_nombre: string;
  estado: string;
  estado_display: string;
  total: string | number;
  total_formateado?: string;
  hora: string;
  observaciones: string;
  tiene_factura: boolean;
  factura_id?: number | null;
  detalles: DetallePedido[];
}

export interface MenuCorriente {
  sopa: string;
  sopas: string[];
  principio: string[];
  proteina: string[];
  acompanante: string;
  limonada: string;
  precio_sopa: string | number;
  precio_sopa_formateado?: string;
  precio_bandeja: string | number;
  precio_bandeja_formateado?: string;
  precio_completo: string | number;
  precio_completo_formateado?: string;
}

export interface MenuDesayuno {
  principales: string[];
  bebidas: string[];
  caldos?: string[];
  acompanante: string;
  precio_desayuno: string | number;
  precio_desayuno_formateado?: string;
}

export interface CatalogoPedido {
  pedido: Pedido;
  categorias: Categoria[];
  productos: Producto[];
  categoria_id: number | null;
  query: string;
  show_corriente: boolean;
  show_desayuno: boolean;
  categoria_corriente_id: number | null;
  categoria_desayuno_id: number | null;
  categoria_snacks_id: number | null;
  menu_corriente: MenuCorriente | null;
  menu_desayuno: MenuDesayuno | null;
  fecha_menu: string | null;
}

export interface ActualizarPedidoPayload {
  estado?: string;
  observaciones?: string;
}

export interface ActualizarDetallePayload {
  producto_id?: number;
  cantidad?: number;
  observaciones?: string;
  servido?: boolean;
}

interface ApiListResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}

export interface PedidosPage {
  items: Pedido[];
  count: number;
  next: string | null;
  hasNext: boolean;
}

let pedidoPreviewCache: Pedido | null = null;
let pedidoListPatchCache: Pedido | null = null;

const toArray = <T,>(payload: T[] | ApiListResponse<T>): T[] => {
  if (Array.isArray(payload)) {
    return payload;
  }

  return payload.results ?? [];
};

const pedidosService = {
  setPedidoPreview(pedido: Pedido) {
    pedidoPreviewCache = pedido;
  },

  getPedidoPreview(id: number | string) {
    if (!pedidoPreviewCache) {
      return null;
    }

    return String(pedidoPreviewCache.id) === String(id) ? pedidoPreviewCache : null;
  },

  buildPedidoPreview(pedido: Pedido) {
    return {
      ...pedido,
      detalles: [],
    };
  },

  clearPedidoPreview(id?: number | string) {
    if (!pedidoPreviewCache) {
      return;
    }

    if (id === undefined || String(pedidoPreviewCache.id) === String(id)) {
      pedidoPreviewCache = null;
    }
  },

  setPedidoListPatch(pedido: Pedido) {
    pedidoListPatchCache = pedido;
  },

  consumePedidoListPatch() {
    const patch = pedidoListPatchCache;
    pedidoListPatchCache = null;
    return patch;
  },

  async getPedidos(page = 1, pageSize = 12): Promise<PedidosPage> {
    const res = await API.get<Pedido[] | ApiListResponse<Pedido>>('pedidos/', {
      params: { archivado: 0, page, page_size: pageSize },
    });
    const payload = res.data;
    const items = toArray(payload);

    if (Array.isArray(payload)) {
      return {
        items,
        count: items.length,
        next: null,
        hasNext: false,
      };
    }

    return {
      items,
      count: payload.count ?? items.length,
      next: payload.next ?? null,
      hasNext: !!payload.next,
    };
  },

  async getMesasDisponibles(): Promise<Mesa[]> {
    const res = await API.get<Mesa[] | ApiListResponse<Mesa>>('mesas/', {
      params: { disponibles: 1 },
    });
    return toArray(res.data);
  },

  async abrirPedido(mesaId: number): Promise<Pedido> {
    const res = await API.post<Pedido>('pedidos/abrir/', { mesa_id: mesaId });
    return res.data;
  },

  async getPedidoDetalle(id: number | string): Promise<Pedido> {
    const res = await API.get<Pedido>(`pedidos/${id}/`);
    return res.data;
  },

  async actualizarPedido(id: number | string, payload: ActualizarPedidoPayload): Promise<Pedido> {
    const res = await API.patch<Pedido>(`pedidos/${id}/`, payload);
    return res.data;
  },

  async eliminarPedido(id: number | string): Promise<void> {
    await API.delete(`pedidos/${id}/`);
  },

  async getCatalogoPedido(id: number | string): Promise<CatalogoPedido> {
    const res = await API.get<CatalogoPedido>(`pedidos/${id}/catalogo/`);
    return res.data;
  },

  async agregarDetalle(
    pedidoId: number | string,
    payload: { producto_id: number; cantidad: number; observaciones?: string }
  ): Promise<Pedido> {
    const res = await API.post<{ pedido: Pedido }>(`pedidos/${pedidoId}/agregar-detalle/`, payload);
    return res.data.pedido;
  },

  async agregarCorriente(
    pedidoId: number | string,
    payload: {
      sopa?: string;
      principio?: string;
      proteina?: string;
      acompanante?: string;
      cantidad: number;
      observaciones?: string;
    }
  ): Promise<Pedido> {
    const res = await API.post<{ pedido: Pedido }>(`pedidos/${pedidoId}/agregar-corriente/`, payload);
    return res.data.pedido;
  },

  async agregarDesayuno(
    pedidoId: number | string,
    payload: {
      principal?: string;
      bebida?: string;
      acompanante?: string;
      cantidad: number;
      observaciones?: string;
    }
  ): Promise<Pedido> {
    const res = await API.post<{ pedido: Pedido }>(`pedidos/${pedidoId}/agregar-desayuno/`, payload);
    return res.data.pedido;
  },

  async marcarDetalleServido(detalleId: number): Promise<Pedido> {
    const res = await API.post<{ pedido: Pedido }>(`pedidos/detalles/${detalleId}/marcar-servido/`);
    return res.data.pedido;
  },

  async actualizarDetalle(detalleId: number, payload: ActualizarDetallePayload): Promise<DetallePedido> {
    const res = await API.patch<DetallePedido>(`pedidos/detalles/${detalleId}/`, payload);
    return res.data;
  },

  async eliminarDetalle(detalleId: number): Promise<void> {
    await API.delete(`pedidos/detalles/${detalleId}/`);
  },
};

export default pedidosService;
