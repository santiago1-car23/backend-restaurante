// Consulta el stock de un producto por nombre
import { endEvent } from 'react-native/Libraries/Performance/Systrace';
import API from './api';

export async function fetchStockPorProducto(nombre: string): Promise<number | null> {
  try {
    const res = await API.get(`/inventario/ingredientes/?q=${encodeURIComponent(nombre)}`);
    if (Array.isArray(res.data) && res.data.length > 0) {
      return Number(res.data[0].cantidad_actual);
    }
    return null;
  } catch {
    return null;
  }
}




