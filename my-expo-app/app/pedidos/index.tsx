import React, { useCallback, useMemo, useState } from 'react';
import { useFocusEffect, useIsFocused } from '@react-navigation/native';
import { View, FlatList, StyleSheet, RefreshControl, TouchableOpacity, Text, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Redirect, useRouter } from 'expo-router';
import PedidoModal from '../../features/pedidos/components/PedidoModal';
import EmptyState from '../../features/pedidos/components/EmptyState';
import usePedidos from '../../features/pedidos/hooks/usePedidos';
import PedidoCard from '../../features/pedidos/components/PedidoCard';
import pedidosService, { Mesa } from '../../features/pedidos/services/pedidosService';
import notificacionesService, { Notificacion } from '../../features/notificaciones/services/notificacionesService';
import notificacionesSettingsService from '../../features/notificaciones/services/notificacionesSettingsService';
import { useAuth } from '../../context/AuthContext';
import { colors } from '../../constants/colors';
import ActionCardModal, { ActionCardButton } from '../../features/ui/ActionCardModal';
import { isCocinero } from '@/features/auth/roleUtils';

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

const parsePedidoId = (url: string) => {
  const match = /[?&]id=(\d+)/.exec(url || '');
  return match?.[1] || null;
};

export default function PedidosScreen() {
  const { token, loading: authLoading, user } = useAuth();
  const usuarioEsCocinero = isCocinero(user);
  const {
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
  } = usePedidos();
  const isFocused = useIsFocused();
  const router = useRouter();
  const [modalVisible, setModalVisible] = useState(false);
  const [mesas, setMesas] = useState<Mesa[]>([]);
  const [mesaSeleccionada, setMesaSeleccionada] = useState<number | null>(null);
  const [creando, setCreando] = useState(false);
  const [cargandoMesas, setCargandoMesas] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackState>(initialFeedbackState);
  const [topNotification, setTopNotification] = useState<Notificacion | null>(null);
  const [showTopNotification, setShowTopNotification] = useState(false);
  const topNotificationTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastShownNotificationRef = React.useRef<number | null>(null);

  const closeFeedback = useCallback(() => {
    setFeedback(initialFeedbackState);
  }, []);

  const fetchMesas = useCallback(async () => {
    setCargandoMesas(true);
    try {
      const data = await pedidosService.getMesasDisponibles();
      setMesas(data);
    } catch (err: any) {
      setFeedback({
        visible: true,
        icon: 'grid-outline',
        title: 'Mesas no disponibles',
        message: err?.response?.data?.detail || 'No se pudieron cargar las mesas disponibles.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      setMesas([]);
    } finally {
      setCargandoMesas(false);
    }
  }, [closeFeedback]);

  const abrirModal = useCallback(async () => {
    setMesaSeleccionada(null);
    setModalVisible(true);
    await fetchMesas();
  }, [fetchMesas]);

  const crearPedido = useCallback(async () => {
    if (!mesaSeleccionada) return;
    setCreando(true);
    try {
      const pedido = await pedidosService.abrirPedido(mesaSeleccionada);
      setModalVisible(false);
      await fetchPedidos();
      setFeedback({
        visible: true,
        icon: 'checkmark-circle-outline',
        title: 'Pedido creado',
        message: 'El pedido fue creado correctamente y ya esta listo para tomar productos.',
        actions: [
          {
            label: 'Ver pedido',
            onPress: () => {
              closeFeedback();
              router.push({ pathname: '/detalle', params: { id: String(pedido.id) } });
            },
            tone: 'primary',
          },
          {
            label: 'Seguir aqui',
            onPress: closeFeedback,
            tone: 'neutral',
          },
        ],
      });
    } catch (err: any) {
      const message =
        err?.response?.data?.mesa_id?.[0] ||
        err?.response?.data?.detail ||
        'No se pudo abrir el pedido.';
      setFeedback({
        visible: true,
        icon: 'alert-circle-outline',
        title: 'No se pudo crear',
        message,
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    } finally {
      setCreando(false);
    }
  }, [closeFeedback, fetchPedidos, mesaSeleccionada, router]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchPedidos();
    setRefreshing(false);
  }, [fetchPedidos]);

  const editarPedido = useCallback((pedidoId: number) => {
    router.push({ pathname: '/detalle', params: { id: String(pedidoId) } });
  }, [router]);

  const eliminarPedido = useCallback((pedidoId: number, tieneFactura?: boolean) => {
    if (tieneFactura) {
      setFeedback({
        visible: true,
        icon: 'receipt-outline',
        title: 'Pedido pagado',
        message: 'No puedes eliminar un pedido que ya fue pagado.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
      return;
    }

    setFeedback({
      visible: true,
      icon: 'trash-outline',
      title: 'Eliminar pedido',
      message: 'Esta accion eliminara el pedido y liberara su mesa si no tiene otro pedido activo.',
      actions: [
        { label: 'Cancelar', onPress: closeFeedback, tone: 'neutral' },
        {
          label: 'Eliminar',
          tone: 'danger',
          onPress: async () => {
            closeFeedback();
            try {
              await pedidosService.eliminarPedido(pedidoId);
              await fetchPedidos();
              setFeedback({
                visible: true,
                icon: 'checkmark-circle-outline',
                title: 'Pedido eliminado',
                message: 'El pedido se elimino correctamente.',
                actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
              });
            } catch (err: any) {
              setFeedback({
                visible: true,
                icon: 'alert-circle-outline',
                title: 'No se pudo eliminar',
                message: err?.response?.data?.detail || 'No se pudo eliminar el pedido.',
                actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
              });
            }
          },
        },
      ],
    });
  }, [closeFeedback, fetchPedidos]);

  React.useEffect(() => {
    if (!token) {
      return;
    }
    fetchPedidos();
  }, [fetchPedidos, token]);

  useFocusEffect(
    useCallback(() => {
      if (!token) {
        return undefined;
      }

      const patch = pedidosService.consumePedidoListPatch();
      if (patch) {
        patchPedido(patch);
      }

      fetchPedidos();
      return undefined;
    }, [fetchPedidos, patchPedido, token])
  );

  React.useEffect(() => {
    if (!isFocused || !token) {
      return undefined;
    }

    const intervalId = setInterval(() => {
      fetchPedidos();
    }, 3000);

    return () => clearInterval(intervalId);
  }, [fetchPedidos, isFocused, token]);

  React.useEffect(() => {
    if (!isFocused || !token) {
      return undefined;
    }

    const revisarNotificaciones = async () => {
      try {
        const enabled = await notificacionesSettingsService.getEnabled();
        if (!enabled) {
          return;
        }
        const notificaciones = await notificacionesService.getNotificaciones();
        const ultimaNoLeida = notificaciones.find(item => !item.leida);
        if (!ultimaNoLeida) {
          return;
        }
        if (ultimaNoLeida.id === lastShownNotificationRef.current) {
          return;
        }

        lastShownNotificationRef.current = ultimaNoLeida.id;
        setTopNotification(ultimaNoLeida);
        setShowTopNotification(true);

        if (topNotificationTimeoutRef.current) {
          clearTimeout(topNotificationTimeoutRef.current);
        }
        topNotificationTimeoutRef.current = setTimeout(() => {
          setShowTopNotification(false);
        }, 5500);
      } catch {
        // Evitar ruido visual si falla el polling de notificaciones.
      }
    };

    revisarNotificaciones();
    const intervalId = setInterval(revisarNotificaciones, 3000);

    return () => clearInterval(intervalId);
  }, [isFocused, token]);

  React.useEffect(() => () => {
    if (topNotificationTimeoutRef.current) {
      clearTimeout(topNotificationTimeoutRef.current);
    }
  }, []);

  const abrirNotificacionSuperior = useCallback(async () => {
    if (!topNotification) {
      return;
    }
    setShowTopNotification(false);
    try {
      if (!topNotification.leida) {
        await notificacionesService.marcarLeida(topNotification.id);
      }
    } catch {
      // Silencioso.
    }
    const pedidoId = parsePedidoId(topNotification.url);
    if (pedidoId) {
      router.push({ pathname: '/detalle', params: { id: pedidoId } });
      return;
    }
    router.push('/notificaciones' as any);
  }, [router, topNotification]);

  const header = useMemo(
    () => (
      <View style={styles.header}>
        <View style={styles.headerGlow} />
        <View style={styles.headerCopy}>
          <View style={styles.breadcrumbPill}>
            <Text style={styles.breadcrumb}>Dashboard / Operaciones</Text>
          </View>
          <Text style={styles.headerTitle}>Pedidos</Text>
          <Text style={styles.headerSubtitle}>
            {user?.first_name ? `Panel activo para ${user.first_name}` : 'Monitor de ordenes activas'}
          </Text>
        </View>
        <View style={styles.headerActions}>
          {!usuarioEsCocinero ? (
            <TouchableOpacity style={styles.newOrderButton} onPress={abrirModal} activeOpacity={0.9}>
              <Text style={styles.newOrderButtonText}>Nuevo pedido</Text>
            </TouchableOpacity>
          ) : null}
          <View style={styles.statusChip}>
            <Text style={styles.statusChipValue}>{totalCount || pedidos.length}</Text>
            <Text style={styles.statusChipText}>activos</Text>
          </View>
        </View>
      </View>
    ),
    [abrirModal, pedidos.length, totalCount, user?.first_name, usuarioEsCocinero]
  );

  const renderItem = useCallback(
    ({ item }: { item: (typeof pedidos)[number] }) => (
      <TouchableOpacity
        activeOpacity={0.9}
        onPress={() => editarPedido(item.id)}
      >
        <PedidoCard
          id={item.id}
          mesa={`Mesa ${item.mesa_numero}`}
          estado={item.estado_display}
          total={item.total}
          totalFormateado={item.total_formateado}
          mesero={item.mesero_nombre}
          hora={item.hora}
          tieneFactura={item.tiene_factura}
          onDelete={usuarioEsCocinero ? undefined : () => eliminarPedido(item.id, item.tiene_factura)}
        />
      </TouchableOpacity>
    ),
    [editarPedido, eliminarPedido, usuarioEsCocinero]
  );

  const keyExtractor = useCallback((item: (typeof pedidos)[number]) => item.id.toString(), []);

  if (!authLoading && !token) {
    return <Redirect href="/login" />;
  }

  return (
    <View style={styles.container}>
      {!usuarioEsCocinero && showTopNotification && topNotification ? (
        <View style={styles.topNotificationWrap}>
          <TouchableOpacity style={styles.topNotificationCard} activeOpacity={0.92} onPress={abrirNotificacionSuperior}>
            <View style={styles.topNotificationIconWrap}>
              <Ionicons name="notifications-outline" size={18} color={colors.textSlate} />
            </View>
            <View style={styles.topNotificationCopy}>
              <Text style={styles.topNotificationTitle}>Nuevo aviso</Text>
              <Text style={styles.topNotificationMessage} numberOfLines={2}>
                {topNotification.mensaje}
              </Text>
            </View>
            <TouchableOpacity
              style={styles.topNotificationClose}
              onPress={() => setShowTopNotification(false)}
              hitSlop={8}
            >
              <Ionicons name="close" size={16} color={colors.textMuted} />
            </TouchableOpacity>
          </TouchableOpacity>
        </View>
      ) : null}

      <FlatList
        data={pedidos}
        keyExtractor={keyExtractor}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        removeClippedSubviews
        initialNumToRender={8}
        maxToRenderPerBatch={8}
        windowSize={7}
        updateCellsBatchingPeriod={50}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary]} />
        }
        ListEmptyComponent={
          loading ? null : !error ? <EmptyState /> : null
        }
        ListHeaderComponent={header}
        ListFooterComponent={
          hasNext || page > 1 ? (
            <View style={styles.loadActionsRow}>
              {page > 1 ? (
                <TouchableOpacity
                  style={[styles.loadLessButton, loadingMore && styles.loadButtonDisabled]}
                  onPress={fetchLessPedidos}
                  disabled={loadingMore}
                  activeOpacity={0.9}
                >
                  <Text style={styles.loadLessButtonText}>Cargar menos</Text>
                </TouchableOpacity>
              ) : null}
              {hasNext ? (
                <TouchableOpacity
                  style={[styles.loadMoreButton, loadingMore && styles.loadButtonDisabled]}
                  onPress={fetchMorePedidos}
                  disabled={loadingMore}
                  activeOpacity={0.9}
                >
                  {loadingMore ? (
                    <ActivityIndicator color={colors.btnPrimaryText} />
                  ) : (
                    <Text style={styles.loadMoreButtonText}>Cargar más</Text>
                  )}
                </TouchableOpacity>
              ) : null}
            </View>
          ) : null
        }
      />
      {!usuarioEsCocinero ? (
        <PedidoModal
          visible={modalVisible}
          mesas={mesas}
          cargandoMesas={cargandoMesas}
          mesaSeleccionada={mesaSeleccionada}
          creando={creando}
          onSelectMesa={setMesaSeleccionada}
          onClose={() => setModalVisible(false)}
          onCrear={crearPedido}
        />
      ) : null}

      <ActionCardModal
        visible={feedback.visible}
        icon={feedback.icon}
        title={feedback.title}
        message={feedback.message}
        actions={feedback.actions}
        onClose={closeFeedback}
      />
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
    paddingTop: 42,
    paddingBottom: 140,
    width: '100%',
    maxWidth: 860,
    alignSelf: 'center',
  },
  topNotificationWrap: {
    position: 'absolute',
    top: 10,
    left: 0,
    right: 0,
    zIndex: 40,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  topNotificationCard: {
    width: '100%',
    maxWidth: 860,
    minHeight: 68,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.surfaceCardBorder,
    backgroundColor: colors.surfaceCardGlassStrong,
    paddingVertical: 10,
    paddingHorizontal: 10,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    shadowColor: colors.shadowSlate,
    shadowOpacity: 0.12,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 16,
    elevation: 5,
  },
  topNotificationIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#c7f9d7',
  },
  topNotificationCopy: {
    flex: 1,
  },
  topNotificationTitle: {
    fontSize: 12,
    fontWeight: '900',
    color: colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  topNotificationMessage: {
    marginTop: 2,
    fontSize: 13,
    color: colors.textSlate,
    fontWeight: '700',
    lineHeight: 18,
  },
  topNotificationClose: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceSoft,
  },
  header: {
    overflow: 'hidden',
    marginBottom: 12,
    paddingHorizontal: 20,
    paddingVertical: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.surfaceCardGlassStrong,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.surfaceCardBorder,
    shadowColor: colors.shadowCyan,
    shadowOpacity: 0.12,
    shadowOffset: { width: 0, height: 14 },
    shadowRadius: 24,
    elevation: 5,
  },
  headerGlow: {
    position: 'absolute',
    top: -20,
    right: -10,
    width: 150,
    height: 150,
    borderRadius: 999,
    backgroundColor: colors.dockGlow,
  },
  headerCopy: {
    flex: 1,
    paddingRight: 16,
  },
  headerActions: {
    alignItems: 'flex-end',
    gap: 10,
  },
  breadcrumbPill: {
    alignSelf: 'flex-start',
    marginBottom: 10,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
    backgroundColor: colors.overlayLightSoft,
    borderWidth: 1,
    borderColor: colors.overlayPanelBorder,
  },
  breadcrumb: {
    color: colors.textSlateSoft,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.4,
  },
  headerTitle: {
    fontSize: 25,
    fontWeight: '900',
    color: colors.primary,
    letterSpacing: -1,
  },
  headerSubtitle: {
    marginTop: 5,
    color: colors.textMuted,
    fontSize: 12,
    textAlign: 'left',
  },
  newOrderButton: {
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 10,
    shadowColor: colors.shadowPrimary,
    shadowOpacity: 0.18,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 12,
    elevation: 3,
  },
  newOrderButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
    fontSize: 12,
    letterSpacing: 0.3,
    textTransform: 'uppercase',
  },
  statusChip: {
    minWidth: 96,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderRadius: 20,
    backgroundColor: colors.buttonDarkBg,
    borderWidth: 1,
    borderColor: colors.overlayDarkBorder,
    shadowColor: colors.shadowSlate,
    shadowOpacity: 0.18,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 16,
    elevation: 4,
  },
  statusChipValue: {
    color: colors.textIce,
    fontSize: 24,
    fontWeight: '900',
    lineHeight: 28,
  },
  statusChipText: {
    color: colors.textCloud,
    fontWeight: '700',
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  loadActionsRow: {
    marginTop: 10,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 10,
  },
  loadMoreButton: {
    minWidth: 150,
    backgroundColor: colors.textSlate,
    borderRadius: 16,
    paddingVertical: 14,
    paddingHorizontal: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadLessButton: {
    minWidth: 150,
    backgroundColor: colors.surfaceSoft,
    borderRadius: 16,
    paddingVertical: 14,
    paddingHorizontal: 18,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  loadButtonDisabled: {
    opacity: 0.7,
  },
  loadMoreButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
    fontSize: 13,
  },
  loadLessButtonText: {
    color: colors.textSlate,
    fontWeight: '800',
    fontSize: 13,
  },
});
