import React, { useCallback, useEffect, useState } from 'react';
import { useIsFocused } from '@react-navigation/native';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Redirect, useLocalSearchParams } from 'expo-router';
import { colors } from '../../constants/colors';

import AddDetalleModal from '@/features/detalle/components/AddDetalleModal';
import EditDetalleModal from '@/features/detalle/components/EditDetalleModal';
import EditPedidoModal from '@/features/detalle/components/EditPedidoModal';
import ActionCardModal, { ActionCardButton } from '@/features/ui/ActionCardModal';
import VoiceCaptureButton from '@/features/voice/components/VoiceCaptureButton';
import VoiceOrderPreviewModal from '@/features/voice/components/VoiceOrderPreviewModal';
import { useVoiceOrder } from '@/features/voice/hooks/useVoiceOrder';
import { speechService } from '@/features/voice/services/speechService';
import pedidosService, {
  CatalogoPedido,
  DetallePedido,
  Pedido,
} from '@/features/pedidos/services/pedidosService';
import { useAuth } from '@/context/AuthContext';
import { isCocinero } from '@/features/auth/roleUtils';

type CorrienteForm = {
  sopa: string;
  principio: string;
  proteina: string;
  acompanante: string;
};

type FeedbackState = {
  visible: boolean;
  icon?: React.ComponentProps<typeof ActionCardModal>['icon'];
  title: string;
  message: string;
  actions: ActionCardButton[];
};

const initialFeedbackState: FeedbackState = {
  visible: false,
  title: '',
  message: '',
  actions: [],
};

const parseCorrienteObservaciones = (observaciones: string) => {
  const lines = (observaciones || '').split('\n').map(line => line.trim()).filter(Boolean);
  const corriente: CorrienteForm = {
    sopa: '',
    principio: '',
    proteina: '',
    acompanante: '',
  };
  const baseLines: string[] = [];

  lines.forEach(line => {
    const lower = line.toLowerCase();
    if (lower.startsWith('sopa:')) {
      corriente.sopa = line.split(':', 2)[1]?.trim() || '';
      return;
    }
    if (lower.startsWith('principio:')) {
      corriente.principio = line.split(':', 2)[1]?.trim() || '';
      return;
    }
    if (lower.startsWith('proteina:')) {
      corriente.proteina = line.split(':', 2)[1]?.trim() || '';
      return;
    }
    if (lower.startsWith('acompanante:')) {
      corriente.acompanante = line.split(':', 2)[1]?.trim() || '';
      return;
    }
    baseLines.push(line);
  });

  return {
    corriente,
    baseObservaciones: baseLines.join('\n'),
  };
};

const buildCorrienteObservaciones = (observaciones: string, corriente: CorrienteForm) => {
  const extras = [];
  if (corriente.sopa) extras.push(`Sopa: ${corriente.sopa}`);
  if (corriente.principio) extras.push(`Principio: ${corriente.principio}`);
  if (corriente.proteina) extras.push(`Proteina: ${corriente.proteina}`);
  if (corriente.acompanante) extras.push(`Acompanante: ${corriente.acompanante}`);

  return [observaciones.trim(), ...extras].filter(Boolean).join('\n');
};

const getEstadoPillStyle = (estado: string, tieneFactura?: boolean) => {
  if (tieneFactura) {
    return {
      label: 'Pagado',
      backgroundColor: colors.statusPagadoBg,
      textColor: colors.statusPagadoText,
    };
  }

  const normalizado = (estado || '').toLowerCase();

  if (['entregado', 'servido', 'listo'].includes(normalizado)) {
    return {
      label: 'Servido',
      backgroundColor: colors.statusEntregadoBg,
      textColor: colors.statusEntregadoText,
    };
  }

  return {
    label: 'En curso',
    backgroundColor: colors.statusPendienteBg,
    textColor: colors.statusPendienteText,
  };
};

export default function PedidoDetalleScreen() {
  const { token, loading: authLoading, user } = useAuth();
  const usuarioEsCocinero = isCocinero(user);
  const { id } = useLocalSearchParams<{ id: string }>();
  const isFocused = useIsFocused();
  const [pedido, setPedido] = useState<Pedido | null>(null);
  const [catalogo, setCatalogo] = useState<CatalogoPedido | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [cantidad, setCantidad] = useState('1');
  const [observaciones, setObservaciones] = useState('');
  const [corriente, setCorriente] = useState({
    sopa: '',
    principio: '',
    proteina: '',
    acompanante: '',
  });
  const [desayuno, setDesayuno] = useState({
    principal: '',
    bebida: '',
    acompanante: '',
  });
  const [editPedidoVisible, setEditPedidoVisible] = useState(false);
  const [editDetalleVisible, setEditDetalleVisible] = useState(false);
  const [selectedDetalle, setSelectedDetalle] = useState<DetallePedido | null>(null);
  const [pedidoEstado, setPedidoEstado] = useState('pendiente');
  const [pedidoObservaciones, setPedidoObservaciones] = useState('');
  const [editingPedido, setEditingPedido] = useState(false);
  const [editingDetalle, setEditingDetalle] = useState(false);
  const [editCantidad, setEditCantidad] = useState('1');
  const [editObservaciones, setEditObservaciones] = useState('');
  const [editSelectedProductId, setEditSelectedProductId] = useState<number | null>(null);
  const [editCorriente, setEditCorriente] = useState<CorrienteForm>({
    sopa: '',
    principio: '',
    proteina: '',
    acompanante: '',
  });
  const [feedback, setFeedback] = useState<FeedbackState>(initialFeedbackState);
  const [deletingDetalleId, setDeletingDetalleId] = useState<number | null>(null);
  const [voiceListening, setVoiceListening] = useState(false);
  const voiceSessionRef = React.useRef<{ stop: () => Promise<string>; cancel: () => Promise<void> } | null>(null);
  const voiceLongPressTriggeredRef = React.useRef(false);

  const closeFeedback = useCallback(() => {
    setFeedback(initialFeedbackState);
  }, []);

  const syncCatalogState = useCallback((catalogoData: CatalogoPedido) => {
    setCatalogo(catalogoData);
    setCorriente({
      sopa: '',
      principio: '',
      proteina: '',
      acompanante: catalogoData.menu_corriente?.acompanante || '',
    });
    setDesayuno({
      principal: '',
      bebida: '',
      acompanante: catalogoData.menu_desayuno?.acompanante || '',
    });
  }, []);

  const loadCatalogo = useCallback(async () => {
    if (!token || !id) {
      return;
    }

    try {
      const catalogoData = await pedidosService.getCatalogoPedido(id);
      syncCatalogState(catalogoData);
    } catch {
      // El detalle del pedido sigue siendo útil aunque el catálogo falle.
    }
  }, [id, syncCatalogState, token]);

  const loadPedido = useCallback(async () => {
    if (!token) {
      return;
    }

    if (!id) {
      setError('Pedido no encontrado.');
      setLoading(false);
      return;
    }

    try {
      const pedidoData = await pedidosService.getPedidoDetalle(id);
      setPedido(pedidoData);
      setPedidoEstado(pedidoData.estado);
      setPedidoObservaciones(pedidoData.observaciones || '');
      pedidosService.setPedidoListPatch(pedidoData);
      setError(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'No se pudo cargar el detalle del pedido.');
      setPedido(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [id, token]);

  const handleVoiceApplied = useCallback((pedidoActualizado: Pedido) => {
    setPedido(pedidoActualizado);
    pedidosService.setPedidoListPatch(pedidoActualizado);
    loadPedido();
  }, [loadPedido]);

  const handleVoiceError = useCallback((message: string) => {
    setFeedback({
      visible: true,
      icon: 'mic-outline',
      title: 'No se pudo agregar',
      message,
      actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
    });
  }, [closeFeedback]);

  const voiceOrder = useVoiceOrder({
    pedidoId: pedido?.id ?? null,
    catalogo,
    onApplied: handleVoiceApplied,
    onError: handleVoiceError,
  });

  useEffect(() => {
    loadPedido();
  }, [loadPedido]);

  useEffect(() => {
    loadCatalogo();
  }, [loadCatalogo]);

  useEffect(() => {
    if (!isFocused || !token || !id) {
      return undefined;
    }

    const intervalId = setInterval(() => {
      loadPedido();
    }, 3000);

    return () => clearInterval(intervalId);
  }, [id, isFocused, loadPedido, token]);

  useEffect(() => {
    return () => {
      const session = voiceSessionRef.current;
      if (session) {
        session.cancel().catch(() => {
          // Silencioso.
        });
      }
    };
  }, []);

  if (!authLoading && !token) {
    return <Redirect href="/login" />;
  }

  const resetForm = () => {
    setSelectedProductId(null);
    setCantidad('1');
    setObservaciones('');
    setCorriente({
      sopa: '',
      principio: '',
      proteina: '',
      acompanante: catalogo?.menu_corriente?.acompanante || '',
    });
    setDesayuno({
      principal: '',
      bebida: '',
      acompanante: catalogo?.menu_desayuno?.acompanante || '',
    });
  };

  const openModal = () => {
    if (usuarioEsCocinero) {
      Alert.alert('Permisos', 'Tu rol solo permite visualizar y marcar como servido.');
      return;
    }
    if (pedido?.tiene_factura) {
      Alert.alert('Pedido', 'No puedes agregar productos a un pedido pagado.');
      return;
    }
    resetForm();
    setModalVisible(true);
    if (!catalogo) {
      loadCatalogo();
    }
  };

  const openEditPedidoModal = () => {
    if (usuarioEsCocinero) {
      Alert.alert('Permisos', 'Tu rol solo permite visualizar y marcar como servido.');
      return;
    }
    if (!pedido) {
      return;
    }
    if (pedido.tiene_factura) {
      Alert.alert('Pedido', 'No puedes editar un pedido pagado.');
      return;
    }
    setPedidoEstado(pedido.estado);
    setPedidoObservaciones(pedido.observaciones || '');
    setEditPedidoVisible(true);
  };

  const openVoiceOrder = async () => {
    if (voiceLongPressTriggeredRef.current) {
      voiceLongPressTriggeredRef.current = false;
      return;
    }

    if (usuarioEsCocinero) {
      Alert.alert('Permisos', 'Tu rol solo permite visualizar y marcar como servido.');
      return;
    }
    if (pedido?.tiene_factura) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Pedido pagado',
        message: 'No puedes agregar productos por voz a un pedido pagado.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }

    if (!catalogo) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Catalogo cargando',
        message: 'Espera un momento mientras cargamos el catalogo del pedido para interpretar la voz.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      loadCatalogo();
      return;
    }

    voiceOrder.open();

    if (!speechService || typeof speechService.isAvailable !== 'function') {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Voz no disponible',
        message: 'El modulo de voz no se cargo correctamente en esta build. Reabre la app Development Build.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }

    if (!speechService.isAvailable()) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Reconocimiento no disponible',
        message:
          'No se detecta el servicio de voz en este entorno. Abre la app con Development Build y vuelve a intentar.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }
  };

  const startVoicePressHold = async () => {
    if (voiceListening || voiceSessionRef.current) {
      return;
    }

    voiceLongPressTriggeredRef.current = true;

    if (usuarioEsCocinero) {
      Alert.alert('Permisos', 'Tu rol solo permite visualizar y marcar como servido.');
      return;
    }
    if (pedido?.tiene_factura) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Pedido pagado',
        message: 'No puedes agregar productos por voz a un pedido pagado.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }
    if (!catalogo) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Catalogo cargando',
        message: 'Espera un momento mientras cargamos el catalogo del pedido para interpretar la voz.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      loadCatalogo();
      return;
    }
    if (!speechService || typeof speechService.isAvailable !== 'function') {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Voz no disponible',
        message: 'El modulo de voz no se cargo correctamente en esta build. Reabre la app Development Build.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }
    if (!speechService.isAvailable()) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Reconocimiento no disponible',
        message:
          'No se detecta el servicio de voz en este entorno. Abre la app con Development Build y vuelve a intentar.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }
    try {
      const session = await speechService.startLiveListening({ lang: 'es-CO' });
      voiceSessionRef.current = session;
      setVoiceListening(true);
    } catch (error: any) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'Captura por voz no disponible',
        message:
          error?.message ||
          'No fue posible iniciar la captura de voz. Puedes escribir el pedido manualmente en el asistente.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    }
  };

  const stopVoicePressHold = async () => {
    const session = voiceSessionRef.current;
    if (!session) {
      return;
    }

    voiceSessionRef.current = null;
    setVoiceListening(false);

    try {
      const transcript = await session.stop();
      if (!transcript.trim()) {
        return;
      }
      voiceOrder.open();
      voiceOrder.setTranscript(transcript);
      voiceOrder.interpret();
    } catch (error: any) {
      setFeedback({
        visible: true,
        icon: 'mic-outline',
        title: 'No detectamos voz',
        message:
          error?.message ||
          'No detectamos una frase valida. Puedes intentar de nuevo o escribir el pedido manualmente.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    }
  };

  const openEditDetalleModal = (detalle: DetallePedido) => {
    if (usuarioEsCocinero) {
      Alert.alert('Permisos', 'Tu rol solo permite visualizar y marcar como servido.');
      return;
    }
    if (pedido?.tiene_factura) {
      Alert.alert('Detalle', 'No puedes editar productos de un pedido pagado.');
      return;
    }
    const parsed = parseCorrienteObservaciones(detalle.observaciones || '');
    setSelectedDetalle(detalle);
    setEditCantidad(String(detalle.cantidad || 1));
    setEditObservaciones(parsed.baseObservaciones);
    setEditCorriente(parsed.corriente);
    setEditSelectedProductId(detalle.producto_nombre.toLowerCase() === 'menu corriente' ? null : detalle.producto);
    setEditDetalleVisible(true);
    if (!catalogo) {
      loadCatalogo();
    }
  };

  const handleGuardarPedido = async () => {
    if (!pedido) {
      return;
    }

    setEditingPedido(true);
    try {
      const pedidoActualizado = await pedidosService.actualizarPedido(pedido.id, {
        estado: pedidoEstado,
        observaciones: pedidoObservaciones,
      });
      setPedido(pedidoActualizado);
      pedidosService.setPedidoListPatch(pedidoActualizado);
      setEditPedidoVisible(false);
    } catch (err: any) {
      Alert.alert('Pedido', err?.response?.data?.detail || 'No se pudo actualizar el pedido.');
    } finally {
      setEditingPedido(false);
    }
  };

  const handleGuardarDetalle = async () => {
    if (!pedido || !selectedDetalle) {
      return;
    }

    const cantidadFinal = Number(editCantidad || '1');
    if (!Number.isFinite(cantidadFinal) || cantidadFinal <= 0) {
      Alert.alert('Detalle', 'La cantidad debe ser mayor que cero.');
      return;
    }

    const payload: {
      producto_id?: number;
      cantidad: number;
      observaciones: string;
    } = {
      cantidad: cantidadFinal,
      observaciones:
        selectedDetalle.producto_nombre.toLowerCase() === 'menu corriente'
          ? buildCorrienteObservaciones(editObservaciones, editCorriente)
          : editObservaciones.trim(),
    };

    if (
      selectedDetalle.producto_nombre.toLowerCase() !== 'menu corriente' &&
      editSelectedProductId &&
      editSelectedProductId !== selectedDetalle.producto
    ) {
      payload.producto_id = editSelectedProductId;
    }

    setEditingDetalle(true);
    try {
      await pedidosService.actualizarDetalle(selectedDetalle.id, payload);
      setEditDetalleVisible(false);
      setSelectedDetalle(null);
      await loadPedido();
    } catch (err: any) {
      Alert.alert('Detalle', err?.response?.data?.detail || 'No se pudo actualizar el detalle.');
    } finally {
      setEditingDetalle(false);
    }
  };

  const handleEliminarDetalle = (detalle: DetallePedido) => {
    if (usuarioEsCocinero) {
      Alert.alert('Permisos', 'Tu rol solo permite visualizar y marcar como servido.');
      return;
    }
    if (pedido?.tiene_factura) {
      setFeedback({
        visible: true,
        icon: 'receipt-outline',
        title: 'Pedido pagado',
        message: 'No puedes eliminar productos de un pedido pagado.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }

    setFeedback({
      visible: true,
      icon: 'trash-outline',
      title: 'Eliminar producto',
      message: `¿Quieres eliminar ${detalle.producto_nombre} del pedido?`,
      actions: [
        { label: 'Cancelar', onPress: closeFeedback, tone: 'neutral' },
        {
          label: 'Eliminar',
          tone: 'danger',
          loading: deletingDetalleId === detalle.id,
          onPress: async () => {
            setDeletingDetalleId(detalle.id);
            try {
              await pedidosService.eliminarDetalle(detalle.id);
              if (selectedDetalle?.id === detalle.id) {
                setEditDetalleVisible(false);
                setSelectedDetalle(null);
              }
              closeFeedback();
              await loadPedido();
            } catch (err: any) {
              setFeedback({
                visible: true,
                icon: 'alert-circle-outline',
                title: 'No se pudo eliminar',
                message: err?.response?.data?.detail || 'No se pudo eliminar el detalle.',
                actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
              });
            } finally {
              setDeletingDetalleId(null);
            }
          },
        },
      ],
    });
  };

  const handleAgregarProducto = async () => {
    if (!pedido || !selectedProductId) {
      setFeedback({
        visible: true,
        icon: 'alert-circle-outline',
        title: 'Producto requerido',
        message: 'Selecciona un producto para agregar.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }

    setSubmitting(true);
    try {
      const pedidoActualizado = await pedidosService.agregarDetalle(pedido.id, {
        producto_id: selectedProductId,
        cantidad: Number(cantidad || '1'),
        observaciones,
      });
      setPedido(pedidoActualizado);
      pedidosService.setPedidoListPatch(pedidoActualizado);
      setModalVisible(false);
      resetForm();
      loadPedido();
    } catch (err: any) {
      setFeedback({
        visible: true,
        icon: 'restaurant-outline',
        title: 'No se pudo agregar',
        message: err?.response?.data?.detail || 'No se pudo agregar el producto.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleAgregarCorriente = async () => {
    if (!pedido) return;

    setSubmitting(true);
    try {
      const pedidoActualizado = await pedidosService.agregarCorriente(pedido.id, {
        sopa: corriente.sopa,
        principio: corriente.principio,
        proteina: corriente.proteina,
        acompanante: corriente.acompanante,
        cantidad: Number(cantidad || '1'),
        observaciones,
      });
      setPedido(pedidoActualizado);
      pedidosService.setPedidoListPatch(pedidoActualizado);
      setModalVisible(false);
      resetForm();
      loadPedido();
    } catch (err: any) {
      setFeedback({
        visible: true,
        icon: 'restaurant-outline',
        title: 'No se pudo agregar',
        message: err?.response?.data?.detail || 'No se pudo agregar el menu corriente.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleAgregarDesayuno = async () => {
    if (!pedido) return;

    setSubmitting(true);
    try {
      const pedidoActualizado = await pedidosService.agregarDesayuno(pedido.id, {
        principal: desayuno.principal,
        bebida: desayuno.bebida,
        acompanante: desayuno.acompanante,
        cantidad: Number(cantidad || '1'),
        observaciones,
      });
      setPedido(pedidoActualizado);
      pedidosService.setPedidoListPatch(pedidoActualizado);
      setModalVisible(false);
      resetForm();
      loadPedido();
    } catch (err: any) {
      setFeedback({
        visible: true,
        icon: 'cafe-outline',
        title: 'No se pudo agregar',
        message: err?.response?.data?.detail || 'No se pudo agregar el menu desayuno.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleServido = async (detalleId: number) => {
    if (!pedido) return;
    if (pedido.tiene_factura) {
      Alert.alert('Pedido', 'No puedes modificar productos de un pedido pagado.');
      return;
    }

    try {
      const pedidoActualizado = await pedidosService.marcarDetalleServido(detalleId);
      setPedido(pedidoActualizado);
      pedidosService.setPedidoListPatch(pedidoActualizado);
      loadPedido();
    } catch (err: any) {
      Alert.alert('Pedido', err?.response?.data?.detail || 'No se pudo marcar el producto como servido.');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadPedido();
  };

  const pedidoPagado = !!pedido?.tiene_factura;

  const renderDetalle = ({ item }: { item: DetallePedido }) => {
    const precio = typeof item.precio_unitario === 'number'
      ? item.precio_unitario
      : Number(item.precio_unitario || 0);
    const subtotal = typeof item.subtotal === 'number'
      ? item.subtotal
      : Number(item.subtotal || 0);
    const precioTexto = item.precio_unitario_formateado || `$${precio.toFixed(2)}`;
    const subtotalTexto = item.subtotal_formateado || `$${subtotal.toFixed(2)}`;

    return (
      <View style={styles.productoCard}>
        <View style={styles.productHeader}>
          <View style={styles.productTitleBlock}>
            <Text style={styles.productoNombre}>{item.producto_nombre}</Text>
            {item.observaciones ? <Text style={styles.productObs}>Obs: {item.observaciones}</Text> : null}
          </View>
          <View style={[styles.badge, item.servido ? styles.badgeSuccess : styles.badgePending]}>
            <Text style={[styles.badgeText, item.servido ? styles.badgeSuccessText : styles.badgePendingText]}>
              {item.servido ? 'Servido' : 'En curso'}
            </Text>
          </View>
        </View>
        <View style={styles.metaGrid}>
          <View style={styles.metaBox}>
            <Text style={styles.metaLabel}>Cantidad</Text>
            <Text style={styles.metaValue}>{item.cantidad}</Text>
          </View>
          <View style={styles.metaBox}>
            <Text style={styles.metaLabel}>Precio</Text>
            <Text style={styles.metaMoneyValue}>{precioTexto}</Text>
          </View>
          <View style={styles.metaBox}>
            <Text style={styles.metaLabel}>Subtotal</Text>
            <Text style={styles.metaMoneyValue}>{subtotalTexto}</Text>
          </View>
        </View>
        {!usuarioEsCocinero ? (
          <View style={styles.actionRow}>
            <TouchableOpacity
              style={[styles.editBtn, pedidoPagado && styles.editBtnDisabled]}
              onPress={() => openEditDetalleModal(item)}
              disabled={pedidoPagado}
            >
              <Ionicons name="create-outline" size={17} color={colors.textSlate} />
              <Text style={styles.editBtnText}>{pedidoPagado ? 'Bloqueado' : 'Editar'}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.deleteBtn, pedidoPagado && styles.deleteBtnDisabled]}
              onPress={() => handleEliminarDetalle(item)}
              disabled={pedidoPagado}
            >
              <Ionicons name="trash-outline" size={17} color={colors.red} />
              <Text style={styles.deleteBtnText}>
                {pedidoPagado ? 'Bloqueado' : 'Eliminar'}
              </Text>
            </TouchableOpacity>
          </View>
        ) : null}
        {!item.servido ? (
          <TouchableOpacity
            style={[styles.servirBtn, pedidoPagado && styles.servirBtnDisabled]}
            onPress={() => handleServido(item.id)}
            disabled={pedidoPagado}
          >
            <Ionicons name="checkmark-circle-outline" size={18} color={colors.btnPrimaryText} />
            <Text style={styles.servirBtnText}>{pedidoPagado ? 'Bloqueado' : 'Marcar servido'}</Text>
          </TouchableOpacity>
        ) : null}
      </View>
    );
  };

  if (loading && !pedido) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (error || !pedido) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error || 'No encontrado'}</Text>
      </View>
    );
  }

  const total = typeof pedido.total === 'number' ? pedido.total : Number(pedido.total || 0);
  const totalTexto = pedido.total_formateado || `$${total.toFixed(2)}`;
  const estadoPill = getEstadoPillStyle(pedido.estado, pedido.tiene_factura);
  return (
    <View style={styles.container}>
      <FlatList
        data={pedido.detalles}
        keyExtractor={item => item.id.toString()}
        renderItem={renderDetalle}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary]} />}
        ListHeaderComponent={
          <>
            <View style={styles.header}>
              <Text style={styles.breadcrumb}>Pedidos / Detalle</Text>
              <Text style={styles.title}>Pedido #{pedido.id} · Mesa {pedido.mesa_numero}</Text>
              <Text style={styles.subtitle}>Mesero: {pedido.mesero_nombre}</Text>
              <View style={[styles.estadoPill, { backgroundColor: estadoPill.backgroundColor }]}>
                <Text style={[styles.estado, { color: estadoPill.textColor }]}>{estadoPill.label}</Text>
              </View>
              {pedido.observaciones ? <Text style={styles.notes}>Obs generales: {pedido.observaciones}</Text> : null}
            </View>

            {!usuarioEsCocinero ? (
              <>
                <View style={styles.headerActions}>
                  <TouchableOpacity
                    style={[styles.addBtn, styles.headerActionButton, pedidoPagado && styles.headerActionDisabled]}
                    onPress={openModal}
                    disabled={pedidoPagado}
                  >
                    <View style={styles.actionIconWrap}>
                      <Ionicons name="add-circle" size={18} color={colors.btnPrimaryText} />
                    </View>
                    <Text style={styles.addBtnText}>{pedidoPagado ? 'Bloqueado' : 'Agregar producto'}</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.editPedidoBtn, styles.headerActionButton, pedidoPagado && styles.headerActionDisabled]}
                    onPress={openEditPedidoModal}
                    disabled={pedidoPagado}
                  >
                    <View style={styles.actionIconWrap}>
                      <Ionicons name="create-outline" size={18} color={colors.btnPrimaryText} />
                    </View>
                    <Text style={styles.editPedidoBtnText}>{pedidoPagado ? 'Bloqueado' : 'Editar pedido'}</Text>
                  </TouchableOpacity>
                </View>

                <View style={styles.voiceRow}>
                  <VoiceCaptureButton
                    disabled={pedidoPagado}
                    listening={voiceListening}
                    onPress={openVoiceOrder}
                    onLongPress={startVoicePressHold}
                    onPressOut={stopVoicePressHold}
                  />
                </View>
              </>
            ) : null}

            <Text style={styles.sectionTitle}>Productos</Text>
          </>
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>No hay productos en este pedido.</Text>
        }
        ListFooterComponent={
          <View style={styles.totalBox}>
            <Text style={styles.totalLabel}>Total</Text>
            <Text style={styles.totalValue}>{totalTexto}</Text>
          </View>
        }
      />

      {!usuarioEsCocinero ? (
        <>
          <AddDetalleModal
            visible={modalVisible}
            catalogo={catalogo}
            selectedProductId={selectedProductId}
            onSelectProduct={setSelectedProductId}
            cantidad={cantidad}
            onChangeCantidad={setCantidad}
            observaciones={observaciones}
            onChangeObservaciones={setObservaciones}
            loading={submitting}
            onClose={() => setModalVisible(false)}
            onAgregarProducto={handleAgregarProducto}
            onAgregarCorriente={handleAgregarCorriente}
            onAgregarDesayuno={handleAgregarDesayuno}
            corriente={corriente}
            onChangeCorriente={(field, value) => setCorriente(prev => ({ ...prev, [field]: value }))}
            desayuno={desayuno}
            onChangeDesayuno={(field, value) => setDesayuno(prev => ({ ...prev, [field]: value }))}
          />
          <EditPedidoModal
            visible={editPedidoVisible}
            pedido={pedido}
            estado={pedidoEstado}
            observaciones={pedidoObservaciones}
            loading={editingPedido}
            onChangeEstado={setPedidoEstado}
            onChangeObservaciones={setPedidoObservaciones}
            onClose={() => setEditPedidoVisible(false)}
            onSave={handleGuardarPedido}
          />
          <EditDetalleModal
            visible={editDetalleVisible}
            detalle={selectedDetalle}
            catalogo={catalogo}
            selectedProductId={editSelectedProductId}
            cantidad={editCantidad}
            observaciones={editObservaciones}
            corriente={editCorriente}
            loading={editingDetalle}
            onChangeProduct={setEditSelectedProductId}
            onChangeCantidad={setEditCantidad}
            onChangeObservaciones={setEditObservaciones}
            onChangeCorriente={(field, value) => setEditCorriente(prev => ({ ...prev, [field]: value }))}
            onClose={() => setEditDetalleVisible(false)}
            onSave={handleGuardarDetalle}
          />
        </>
      ) : null}
      <ActionCardModal
        visible={feedback.visible}
        icon={feedback.icon}
        title={feedback.title}
        message={feedback.message}
        actions={feedback.actions}
        onClose={closeFeedback}
      />
      {!usuarioEsCocinero ? (
        <VoiceOrderPreviewModal
          visible={voiceOrder.visible}
          transcript={voiceOrder.transcript}
          onChangeTranscript={voiceOrder.setTranscript}
          parsed={voiceOrder.parsed}
          interpreting={voiceOrder.interpreting}
          submitting={voiceOrder.submitting}
          onClose={voiceOrder.close}
          onInterpret={voiceOrder.interpret}
          onConfirm={voiceOrder.confirm}
        />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.panelBg,
  },
  listContent: {
    padding: 16,
    paddingTop: 30,
    paddingBottom: 150,
    width: '100%',
    maxWidth: 860,
    alignSelf: 'center',
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  header: {
    backgroundColor: colors.overlayDarkCard,
    borderRadius: 24,
    padding: 18,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.overlayDarkBorder,
    shadowColor: colors.shadowSlate,
    shadowOpacity: 0.18,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 18,
    elevation: 4,
  },
  breadcrumb: {
    color: colors.textCloud,
    fontSize: 12,
    marginBottom: 8,
  },
  title: {
    fontWeight: '800',
    fontSize: 22,
    color: colors.btnPrimaryText,
  },
  subtitle: {
    color: colors.textIce,
    marginTop: 6,
  },
  estado: {
    color: colors.btnPrimaryText,
    fontWeight: '700',
  },
  estadoPill: {
    alignSelf: 'flex-start',
    marginTop: 10,
    backgroundColor: colors.primary,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
  },
  notes: {
    color: colors.textCloud,
    marginTop: 10,
  },
  addBtn: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    borderRadius: 18,
    paddingVertical: 12,
    shadowColor: colors.shadowPrimary,
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 14,
    elevation: 3,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'stretch',
    gap: 10,
    marginBottom: 10,
  },
  voiceRow: {
    marginBottom: 16,
  },
  headerActionButton: {
    flex: 1,
    marginBottom: 0,
    minHeight: 80,
    paddingHorizontal: 8,
  },
  actionIconWrap: {
    width: 28,
    height: 28,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.overlayLightSoft,
    marginBottom: 6,
  },
  addBtnText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 16,
  },
  editPedidoBtn: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.textSlate,
    borderRadius: 18,
    paddingVertical: 12,
    shadowColor: colors.shadowSlate,
    shadowOpacity: 0.12,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 14,
    elevation: 3,
  },
  editPedidoBtnText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 16,
  },
  sectionTitle: {
    fontWeight: '800',
    fontSize: 16,
    marginBottom: 10,
    color: colors.textSlate,
  },
  productoCard: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 22,
    padding: 11,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.border,
    shadowColor: colors.shadowSlate,
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 18,
    elevation: 3,
  },
  productHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 10,
    marginBottom: 8,
  },
  productTitleBlock: {
    flex: 1,
    paddingRight: 4,
  },
  productoNombre: {
    flex: 1,
    fontWeight: '800',
    color: colors.textSlate,
    fontSize: 14,
    lineHeight: 18,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
  },
  badgeSuccess: {
    backgroundColor: colors.statusEntregadoBg,
  },
  badgePending: {
    backgroundColor: colors.warningBgSoft,
  },
  badgeText: {
    fontWeight: '700',
    fontSize: 11,
  },
  badgeSuccessText: {
    color: colors.statusEntregadoText,
  },
  badgePendingText: {
    color: colors.warningTextDark,
  },
  metaGrid: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 4,
  },
  metaBox: {
    flex: 1,
    backgroundColor: colors.surfaceSoft,
    borderRadius: 16,
    paddingVertical: 8,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  metaLabel: {
    color: colors.textMuted,
    fontSize: 10,
    marginBottom: 3,
    textTransform: 'uppercase',
    fontWeight: '700',
  },
  metaValue: {
    color: colors.textSlate,
    fontWeight: '800',
    fontSize: 13,
  },
  metaMoneyValue: {
    color: colors.successText,
    fontWeight: '900',
    fontSize: 13,
  },
  productObs: {
    color: colors.textSlateSoft,
    marginTop: 4,
    lineHeight: 16,
    fontSize: 11,
  },
  actionRow: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 10,
  },
  editBtn: {
    flex: 1,
    backgroundColor: colors.infoBg,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.primary,
    paddingVertical: 8,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 6,
  },
  editBtnDisabled: {
    opacity: 0.55,
  },
  editBtnText: {
    color: colors.primaryDark,
    fontWeight: '800',
  },
  deleteBtn: {
    flex: 1,
    backgroundColor: `${colors.red}10`,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: `${colors.red}25`,
    paddingVertical: 8,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 6,
  },
  deleteBtnDisabled: {
    opacity: 0.55,
  },
  deleteBtnText: {
    color: colors.red,
    fontWeight: '800',
  },
  servirBtn: {
    marginTop: 10,
    backgroundColor: colors.buttonSuccessBg,
    borderRadius: 14,
    paddingVertical: 9,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  servirBtnDisabled: {
    opacity: 0.55,
  },
  servirBtnText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  headerActionDisabled: {
    opacity: 0.55,
  },
  emptyText: {
    textAlign: 'center',
    color: colors.textMuted,
    paddingVertical: 40,
  },
  inlineLoader: {
    paddingVertical: 34,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  inlineLoaderText: {
    color: colors.textMuted,
    fontWeight: '600',
  },
  totalBox: {
    marginTop: 8,
    backgroundColor: colors.surfaceCard,
    borderRadius: 22,
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  totalLabel: {
    color: colors.textSlateSoft,
    fontWeight: '700',
    fontSize: 16,
  },
  totalValue: {
    color: colors.successText,
    fontWeight: '900',
    fontSize: 22,
  },
  errorText: {
    color: colors.dangerText,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 12,
  },
});
