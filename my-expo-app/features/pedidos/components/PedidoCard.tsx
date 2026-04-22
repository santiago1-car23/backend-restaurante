import React, { memo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../../constants/colors';

interface PedidoCardProps {
  id?: number;
  mesa: string;
  estado: string;
  total: number | string;
  totalFormateado?: string;
  mesero: string;
  hora: string;
  tieneFactura?: boolean;
  onDelete?: () => void;
}

const PedidoCard = ({
  id,
  mesa,
  estado,
  total,
  totalFormateado,
  mesero,
  hora,
  tieneFactura,
  onDelete,
}: PedidoCardProps) => {
  const totalValue = typeof total === 'number' ? total : Number(total) || 0;
  const totalTexto = totalFormateado || `$${totalValue.toFixed(2)}`;

  // Lógica de estados simplificada
  const getStatusConfig = () => {
    const est = (estado || '').toLowerCase();
    if (tieneFactura) return { label: 'Pagado', color: colors.statusPagadoText, bg: colors.statusPagadoBg };
    if (['pendiente', 'en preparación', 'en_preparacion'].includes(est)) 
      return { label: 'En curso', color: colors.statusPendienteText, bg: colors.statusPendienteBg };
    if (est === 'listo') return { label: 'Listo', color: colors.statusListoText, bg: colors.statusListoBg };
    return { label: estado, color: colors.statusEntregadoText, bg: colors.statusEntregadoBg };
  };

  const status = getStatusConfig();

  return (
    <View style={styles.card}>
      {/* Header: ID y Estado */}
      <View style={styles.header}>
        <Text style={styles.folio}>#{id ?? '--'}</Text>
        <View style={[styles.statusPill, { backgroundColor: status.bg }]}>
          <View style={[styles.dot, { backgroundColor: status.color }]} />
          <Text style={[styles.statusText, { color: status.color }]}>{status.label}</Text>
        </View>
      </View>

      {/* Body: Mesa y Mesero */}
      <View style={styles.body}>
        <View>
          <Text style={styles.mesaLabel}>Mesa</Text>
          <Text style={styles.mesaNumber}>{mesa}</Text>
        </View>
        <View style={styles.meseroInfo}>
          <Ionicons name="person-circle-outline" size={18} color={colors.textMuted} />
          <Text style={styles.meseroName}>{mesero}</Text>
        </View>
      </View>

      <View style={styles.divider} />

      {/* Footer: Hora y Total */}
      <View style={styles.footer}>
        <View style={styles.timeGroup}>
          <Ionicons name="time-outline" size={14} color={colors.textMuted} />
          <Text style={styles.horaText}>{hora}</Text>
        </View>
        <View style={styles.priceGroup}>
          {tieneFactura && <Ionicons name="receipt" size={16} color={colors.statusPagadoText} style={{marginRight: 4}} />}
          <Text style={styles.totalText}>{totalTexto}</Text>
        </View>
      </View>

      {onDelete ? (
        <View style={styles.actionsRow}>
          {onDelete ? (
            <TouchableOpacity
              style={[styles.actionBtn, styles.deleteBtn, tieneFactura && styles.deleteBtnDisabled]}
              onPress={onDelete}
              activeOpacity={0.9}
              disabled={tieneFactura}
            >
              <Ionicons name="trash-outline" size={15} color={colors.red} />
              <Text style={[styles.actionText, styles.deleteText]}>
                {tieneFactura ? 'Bloqueado' : 'Eliminar'}
              </Text>
            </TouchableOpacity>
          ) : null}
        </View>
      ) : null}
    </View>
  );
};

export default memo(PedidoCard);

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF', // O colors.surfaceCard
    borderRadius: 16,
    padding: 11,
    marginBottom: 8,
    // Sombra más suave y moderna
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.03)',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  folio: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.textMuted,
    letterSpacing: 0.5,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 20,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  body: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: 8,
  },
  mesaLabel: {
    fontSize: 11,
    color: colors.textMuted,
    marginBottom: 2,
  },
  mesaNumber: {
    fontSize: 19,
    fontWeight: '800',
    color: colors.textSlate,
  },
  meseroInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#F8F9FA',
    paddingVertical: 4,
    paddingHorizontal: 6,
    borderRadius: 8,
  },
  meseroName: {
    fontSize: 12,
    color: colors.textSlate,
    fontWeight: '500',
  },
  divider: {
    height: 1,
    backgroundColor: '#F1F3F5',
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  actionsRow: {
    marginTop: 10,
    flexDirection: 'row',
    gap: 10,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
    width: '100%',
  },
  deleteBtn: {
    backgroundColor: 'rgba(244, 67, 54, 0.08)',
    borderColor: colors.red,
  },
  deleteBtnDisabled: {
    opacity: 0.55,
  },
  actionText: {
    fontSize: 12,
    fontWeight: '800',
  },
  deleteText: {
    color: colors.red,
  },
  timeGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  horaText: {
    fontSize: 11,
    color: colors.textMuted,
  },
  priceGroup: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  totalText: {
    fontSize: 15,
    fontWeight: '800',
    color: colors.successText,
  },
});
