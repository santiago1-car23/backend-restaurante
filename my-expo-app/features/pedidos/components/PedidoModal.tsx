import React from 'react';
import { Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, FlatList } from 'react-native';
import type { Mesa } from '../services/pedidosService';
import { colors } from '../../../constants/colors';

interface PedidoModalProps {
  visible: boolean;
  mesas: Mesa[];
  cargandoMesas?: boolean;
  mesaSeleccionada: number | null;
  creando: boolean;
  onSelectMesa: (id: number) => void;
  onClose: () => void;
  onCrear: () => void;
}

export default function PedidoModal({
  visible,
  mesas,
  cargandoMesas = false,
  mesaSeleccionada,
  creando,
  onSelectMesa,
  onClose,
  onCrear,
}: PedidoModalProps) {
  return (
    <Modal visible={visible} animationType="fade" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.content}>
          <View style={styles.header}>
            <Text style={styles.title}>Nueva Orden</Text>
            <TouchableOpacity onPress={onClose}><Text style={styles.close}>✖️</Text></TouchableOpacity>
          </View>
          <Text style={styles.subtitle}>Selecciona la mesa para abrir el pedido:</Text>
          {cargandoMesas ? (
            <ActivityIndicator size="large" color={colors.primary} style={{ marginVertical: 40 }} />
          ) : mesas.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyTitle}>No hay mesas libres</Text>
              <Text style={styles.emptyText}>
                Ahora mismo no hay mesas disponibles para abrir un nuevo pedido.
              </Text>
            </View>
          ) : (
            <FlatList
              data={mesas}
              keyExtractor={item => item.id.toString()}
              numColumns={2}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[styles.mesaItem, mesaSeleccionada === item.id && styles.mesaItemSelected]}
                  onPress={() => onSelectMesa(item.id)}
                >
                  <Text style={styles.mesaNum}>{item.numero}</Text>
                  <Text style={styles.mesaCap}>{item.capacidad} personas</Text>
                  <Text style={styles.mesaEstado}>{item.estado_display}</Text>
                </TouchableOpacity>
              )}
              style={{ maxHeight: 350 }}
              showsVerticalScrollIndicator={false}
            />
          )}
          <View style={styles.actions}>
            <TouchableOpacity onPress={onClose} style={[styles.btn, styles.btnCancel]}><Text style={styles.btnCancelText}>Cancelar</Text></TouchableOpacity>
            <TouchableOpacity onPress={onCrear} style={[styles.btn, styles.btnSubmit, (!mesaSeleccionada || creando) && styles.btnDisabled]} disabled={!mesaSeleccionada || creando}>
              {creando ? <ActivityIndicator color={colors.btnPrimaryText} /> : <Text style={styles.btnSubmitText}>Crear Pedido</Text>}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: colors.overlayDark, justifyContent: 'center', alignItems: 'center', padding: 20 },
  content: { backgroundColor: colors.surfaceCard, borderRadius: 24, padding: 24, width: '100%', maxWidth: 400 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  title: { fontWeight: '800', fontSize: 22, color: colors.textMain },
  close: { fontSize: 24, color: colors.textMuted },
  subtitle: { color: colors.textMuted, fontSize: 14, marginBottom: 20 },
  emptyState: {
    paddingVertical: 28,
    paddingHorizontal: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceSoft,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.border,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: colors.textSlate,
    marginBottom: 6,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 13,
    textAlign: 'center',
    lineHeight: 20,
  },
  mesaItem: { flex: 1, backgroundColor: colors.lightBg, padding: 16, borderRadius: 16, marginBottom: 12, marginHorizontal: 4, alignItems: 'center', borderWidth: 2, borderColor: 'transparent' },
  mesaItemSelected: { backgroundColor: colors.infoBg, borderColor: colors.primary },
  mesaNum: { fontWeight: '900', fontSize: 24, color: colors.textMain, marginBottom: 4 },
  mesaCap: { fontSize: 12, color: colors.textMuted, marginBottom: 2 },
  mesaEstado: { fontSize: 11, color: colors.textMuted, textTransform: 'uppercase', fontWeight: 'bold' },
  actions: { flexDirection: 'row', marginTop: 24, gap: 12 },
  btn: { flex: 1, paddingVertical: 14, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  btnCancel: { backgroundColor: colors.lightBg },
  btnCancelText: { color: colors.textMuted, fontWeight: 'bold', fontSize: 15 },
  btnSubmit: { backgroundColor: colors.primary },
  btnDisabled: { backgroundColor: colors.border },
  btnSubmitText: { color: colors.btnPrimaryText, fontWeight: 'bold', fontSize: 15 },
});
