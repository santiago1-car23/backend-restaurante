import API from '@/constants/api';

export interface Notificacion {
  id: number;
  mensaje: string;
  url: string;
  creada: string;
  leida: boolean;
}

interface ApiListResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}

// 🔹 Normaliza respuesta (array o paginada)
const toArray = <T,>(payload: T[] | ApiListResponse<T>): T[] => {
  if (Array.isArray(payload)) return payload;
  return payload.results ?? [];
};

// 🔹 Manejo genérico de errores
const handleError = (error: any, mensaje: string) => {
  console.error(mensaje, error);
};

const notificacionesService = {
  // 🔹 Obtener todas las notificaciones
  async getNotificaciones(): Promise<Notificacion[]> {
    try {
      const res = await API.get<
        Notificacion[] | ApiListResponse<Notificacion>
      >('usuarios/notificaciones/');
      
      return toArray(res.data);
    } catch (error) {
      handleError(error, 'Error al obtener notificaciones');
      return [];
    }
  },

  // 🔹 Obtener cantidad de no leídas (OPTIMIZADO)
  async getNoLeidasCount(): Promise<number> {
    try {
      const res = await API.get<{ count: number }>(
        'usuarios/notificaciones/no-leidas-count/'
      );
      return res.data.count ?? 0;
    } catch (error) {
      handleError(error, 'Error al obtener contador de no leídas');
      return 0;
    }
  },

  // 🔹 Marcar una como leída
  async marcarLeida(id: number): Promise<Notificacion | null> {
    try {
      const res = await API.post<Notificacion>(
        `usuarios/notificaciones/${id}/marcar-leida/`
      );
      return res.data;
    } catch (error) {
      handleError(error, 'Error al marcar notificación como leída');
      return null;
    }
  },

  // 🔹 Marcar todas como leídas
  async marcarTodasLeidas(): Promise<number> {
    try {
      const res = await API.post<{ marcadas: number }>(
        'usuarios/notificaciones/marcar-todas-leidas/'
      );
      return res.data.marcadas ?? 0;
    } catch (error) {
      handleError(error, 'Error al marcar todas como leídas');
      return 0;
    }
  },
};

export default notificacionesService;