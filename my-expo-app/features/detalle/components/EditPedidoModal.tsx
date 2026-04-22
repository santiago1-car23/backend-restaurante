import React from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { colors } from '../../../constants/colors';
import type { Pedido } from '../../pedidos/services/pedidosService';

type Props = {
  visible: boolean;
  pedido: Pedido | null;
  estado: string;
  observaciones: string;
  loading: boolean;
  onChangeEstado: (value: string) => void;
  onChangeObservaciones: (value: string) => void;
  onClose: () => void;
  onSave: () => void;
};

const ESTADOS = [
  { value: 'pendiente', label: 'Pendiente' },
  { value: 'entregado', label: 'Servido' },
];

export default function EditPedidoModal({
  visible,
  pedido,
  estado,
  observaciones,
  loading,
  onChangeEstado,
  onChangeObservaciones,
  onClose,
  onSave,
}: Props) {
  const total = pedido ? (pedido.total_formateado || pedido.total) : '';

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
        <KeyboardAvoidingView
          style={styles.keyboardWrap}
          behavior={Platform.OS === 'ios' ? 'padding' : 'position'}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 22 : 24}
        >
          <View style={styles.container}>
            <View style={styles.header}>
              <View>
                <Text style={styles.title}>Editar pedido</Text>

              </View>
              <TouchableOpacity onPress={onClose} style={styles.closeButton} activeOpacity={0.85}>
                <Text style={styles.close}>Cerrar</Text>
              </TouchableOpacity>
            </View>

            <ScrollView
              showsVerticalScrollIndicator={false}
              keyboardShouldPersistTaps="handled"
              keyboardDismissMode="interactive"
              contentContainerStyle={styles.scrollContent}
            >
              <View style={styles.card}>
                <Text style={styles.label}>Mesa</Text>
                <Text style={styles.value}>Mesa {pedido?.mesa_numero ?? '-'}</Text>
              </View>

              <View style={styles.card}>
                <Text style={styles.label}>Total acumulado</Text>
                <Text style={styles.total}>{String(total || '$0')}</Text>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Estado</Text>
                <View style={styles.stateRow}>
                  {ESTADOS.map(item => {
                    const active = estado === item.value;
                    return (
                      <TouchableOpacity
                        key={item.value}
                        style={[styles.stateButton, active && styles.stateButtonActive]}
                        onPress={() => onChangeEstado(item.value)}
                      >
                        <Text style={[styles.stateButtonText, active && styles.stateButtonTextActive]}>
                          {item.label}
                        </Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Observaciones generales</Text>
                <TextInput
                  value={observaciones}
                  onChangeText={onChangeObservaciones}
                  style={styles.textarea}
                  multiline
                  placeholder="Notas generales para cocina o barra..."
                  placeholderTextColor={colors.textMuted}
                />
              </View>

              <TouchableOpacity
                style={[styles.saveButton, loading && styles.disabledButton]}
                onPress={onSave}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color={colors.btnPrimaryText} />
                ) : (
                  <Text style={styles.saveButtonText}>Guardar cambios</Text>
                )}
              </TouchableOpacity>
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: colors.overlayDark,
    justifyContent: 'flex-end',
  },
  keyboardWrap: {
    width: '100%',
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: colors.surfaceSoft,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 16,
    maxHeight: '95%',
    width: '100%',
    maxWidth: 720,
    alignSelf: 'center',
  },
  scrollContent: {
    paddingBottom: 28,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    gap: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.textSlate,
  },
  subtitle: {
    marginTop: 3,
    color: colors.textMuted,
    fontSize: 11,
  },
  close: {
    color: colors.textSlate,
    fontWeight: '700',
    fontSize: 12,
    textAlign: 'center',
  },
  closeButton: {
    backgroundColor: colors.surfaceCard,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 999,
    minWidth: 72,
    alignItems: 'center',
    justifyContent: 'center',
  },
  card: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  label: {
    color: colors.textMuted,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  value: {
    color: colors.textSlate,
    fontWeight: '800',
    fontSize: 16,
  },
  total: {
    color: colors.successText,
    fontWeight: '900',
    fontSize: 22,
  },
  section: {
    marginBottom: 14,
  },
  sectionTitle: {
    color: colors.textSlateSoft,
    fontWeight: '700',
    marginBottom: 8,
  },
  stateRow: {
    flexDirection: 'row',
    gap: 10,
  },
  stateButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 14,
    backgroundColor: colors.surfaceCard,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
  },
  stateButtonActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  stateButtonText: {
    color: colors.textSlate,
    fontWeight: '700',
  },
  stateButtonTextActive: {
    color: colors.btnPrimaryText,
  },
  textarea: {
    minHeight: 110,
    borderRadius: 16,
    backgroundColor: colors.surfaceCard,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 14,
    color: colors.textSlate,
    textAlignVertical: 'top',
  },
  saveButton: {
    marginTop: 4,
    marginBottom: 18,
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 15,
    alignItems: 'center',
  },
  saveButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  disabledButton: {
    opacity: 0.6,
  },
});
