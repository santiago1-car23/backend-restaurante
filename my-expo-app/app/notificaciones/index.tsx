import React, { useCallback, useMemo, useState } from 'react';
import { ActivityIndicator, FlatList, RefreshControl, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { Redirect, useRouter } from 'expo-router';

import { colors } from '@/constants/colors';
import { useAuth } from '@/context/AuthContext';
import ActionCardModal, { ActionCardButton } from '@/features/ui/ActionCardModal';
import notificacionesService, { Notificacion } from '@/features/notificaciones/services/notificacionesService';
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

const formatearFecha = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const parsePedidoId = (url: string) => {
  const match = /[?&]id=(\d+)/.exec(url || '');
  return match?.[1] || null;
};

export default function NotificacionesScreen() {
  const router = useRouter();
  const { token, loading: authLoading, user } = useAuth();
  const usuarioEsCocinero = isCocinero(user);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [updatingAll, setUpdatingAll] = useState(false);
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [feedback, setFeedback] = useState<FeedbackState>(initialFeedbackState);

  const closeFeedback = useCallback(() => setFeedback(initialFeedbackState), []);

  const unreadCount = useMemo(() => notificaciones.filter(item => !item.leida).length, [notificaciones]);

  const loadNotificaciones = useCallback(async () => {
    try {
      const data = await notificacionesService.getNotificaciones();
      setNotificaciones(data);
    } catch (err: any) {
      setFeedback({
        visible: true,
        icon: 'notifications-outline',
        title: 'No se pudieron cargar',
        message: err?.response?.data?.detail || 'No pudimos cargar tus notificaciones.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [closeFeedback]);

  const syncNotificacionesSilencioso = useCallback(async () => {
    try {
      const data = await notificacionesService.getNotificaciones();
      setNotificaciones(data);
    } catch {
      // Silencioso para no molestar al usuario en cada tick.
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      if (!token) {
        return undefined;
      }
      setLoading(true);
      loadNotificaciones();

      const intervalId = setInterval(() => {
        syncNotificacionesSilencioso();
      }, 4000);

      return () => clearInterval(intervalId);
    }, [loadNotificaciones, syncNotificacionesSilencioso, token])
  );

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadNotificaciones();
  }, [loadNotificaciones]);

  const handleMarcarLeida = useCallback(async (item: Notificacion) => {
    if (item.leida) return;
    try {
      await notificacionesService.marcarLeida(item.id);
      setNotificaciones(prev =>
        prev.map(current => (current.id === item.id ? { ...current, leida: true } : current))
      );
    } catch {
      // Silencioso para evitar ruido de UX al tocar.
    }
  }, []);

  const handleAbrir = useCallback(async (item: Notificacion) => {
    await handleMarcarLeida(item);
    const pedidoId = parsePedidoId(item.url);
    if (pedidoId) {
      router.push({ pathname: '/detalle', params: { id: pedidoId } });
    }
  }, [handleMarcarLeida, router]);

  const handleMarcarTodas = useCallback(async () => {
    if (!unreadCount) {
      return;
    }
    setUpdatingAll(true);
    try {
      await notificacionesService.marcarTodasLeidas();
      setNotificaciones(prev => prev.map(item => ({ ...item, leida: true })));
    } catch (err: any) {
      setFeedback({
        visible: true,
        icon: 'alert-circle-outline',
        title: 'No se pudo actualizar',
        message: err?.response?.data?.detail || 'No pudimos marcar todas como leídas.',
        actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
      });
    } finally {
      setUpdatingAll(false);
    }
  }, [closeFeedback, unreadCount]);

  if (!authLoading && !token) {
    return <Redirect href="/login" />;
  }

  if (!authLoading && token && usuarioEsCocinero) {
    return <Redirect href="/pedidos" />;
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={notificaciones}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary]} />}
        ListHeaderComponent={(
          <View style={styles.headerCard}>
            <Text style={styles.breadcrumb}>Ajustes / Notificaciones</Text>
            <Text style={styles.title}>Notificaciones</Text>
            <Text style={styles.subtitle}>
              {unreadCount > 0 ? `${unreadCount} sin leer` : 'Todo al día'}
            </Text>
            <TouchableOpacity
              style={[styles.markAllButton, (!unreadCount || updatingAll) && styles.markAllDisabled]}
              activeOpacity={0.9}
              disabled={!unreadCount || updatingAll}
              onPress={handleMarcarTodas}
            >
              {updatingAll ? (
                <ActivityIndicator color={colors.btnPrimaryText} />
              ) : (
                <>
                  <Ionicons name="checkmark-done-outline" size={16} color={colors.btnPrimaryText} />
                  <Text style={styles.markAllText}>Marcar todas</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        )}
        renderItem={({ item }) => (
          <TouchableOpacity style={[styles.card, !item.leida && styles.cardUnread]} activeOpacity={0.9} onPress={() => handleAbrir(item)}>
            <View style={[styles.iconWrap, !item.leida ? styles.iconWrapUnread : null]}>
              <Ionicons name="restaurant-outline" size={18} color={colors.textSlate} />
            </View>
            <View style={styles.copy}>
              <Text style={styles.message}>{item.mensaje}</Text>
              <Text style={styles.date}>{formatearFecha(item.creada)}</Text>
            </View>
            {!item.leida ? <View style={styles.unreadDot} /> : <Ionicons name="chevron-forward-outline" size={16} color={colors.textMuted} />}
          </TouchableOpacity>
        )}
        ListEmptyComponent={(
          <View style={styles.empty}>
            <Ionicons name="notifications-off-outline" size={28} color={colors.textMuted} />
            <Text style={styles.emptyText}>No tienes notificaciones todavía.</Text>
          </View>
        )}
      />

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
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    padding: 16,
    paddingTop: 34,
    paddingBottom: 150,
    width: '100%',
    maxWidth: 860,
    alignSelf: 'center',
    gap: 10,
  },
  headerCard: {
    marginBottom: 6,
    borderRadius: 24,
    padding: 18,
    backgroundColor: colors.surfaceCardGlassStrong,
    borderWidth: 1,
    borderColor: colors.surfaceCardBorder,
  },
  breadcrumb: {
    color: colors.textMuted,
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  title: {
    marginTop: 6,
    fontSize: 27,
    fontWeight: '900',
    color: colors.primary,
    letterSpacing: -0.8,
  },
  subtitle: {
    marginTop: 2,
    color: colors.textSlateSoft,
    fontWeight: '600',
  },
  markAllButton: {
    marginTop: 12,
    minHeight: 42,
    borderRadius: 14,
    backgroundColor: colors.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  markAllDisabled: {
    opacity: 0.6,
  },
  markAllText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  card: {
    borderRadius: 18,
    backgroundColor: colors.surfaceCardGlassStrong,
    borderWidth: 1,
    borderColor: colors.surfaceCardBorderSoft,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  cardUnread: {
    borderColor: colors.primary,
    backgroundColor: '#ebfbff',
  },
  iconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceSoft,
  },
  iconWrapUnread: {
    backgroundColor: '#b8eef7',
  },
  copy: {
    flex: 1,
  },
  message: {
    color: colors.textSlate,
    fontWeight: '700',
    fontSize: 13,
  },
  date: {
    marginTop: 4,
    color: colors.textMuted,
    fontSize: 11,
  },
  unreadDot: {
    width: 9,
    height: 9,
    borderRadius: 99,
    backgroundColor: colors.primary,
  },
  empty: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 34,
    gap: 8,
  },
  emptyText: {
    color: colors.textMuted,
    fontWeight: '600',
  },
});
