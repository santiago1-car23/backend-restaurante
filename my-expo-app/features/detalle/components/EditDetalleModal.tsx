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
import type { CatalogoPedido, DetallePedido, Producto } from '../../pedidos/services/pedidosService';

type CorrienteForm = {
  sopa: string;
  principio: string;
  proteina: string;
  acompanante: string;
};

type Props = {
  visible: boolean;
  detalle: DetallePedido | null;
  catalogo: CatalogoPedido | null;
  selectedProductId: number | null;
  cantidad: string;
  observaciones: string;
  corriente: CorrienteForm;
  loading: boolean;
  onChangeProduct: (id: number) => void;
  onChangeCantidad: (value: string) => void;
  onChangeObservaciones: (value: string) => void;
  onChangeCorriente: (field: keyof CorrienteForm, value: string) => void;
  onClose: () => void;
  onSave: () => void;
};

function OptionGroup({
  title,
  options,
  value,
  onSelect,
}: {
  title: string;
  options: string[];
  value: string;
  onSelect: (value: string) => void;
}) {
  if (!options.length) {
    return null;
  }

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.chipWrap}>
        {options.map(option => {
          const selected = value === option;
          return (
            <TouchableOpacity
              key={`${title}-${option}`}
              style={[styles.chip, selected && styles.chipActive]}
              onPress={() => onSelect(option)}
            >
              <Text style={[styles.chipText, selected && styles.chipTextActive]}>{option}</Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

function ProductPicker({
  products,
  selectedId,
  onSelect,
}: {
  products: Producto[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Producto</Text>
      <View style={styles.productList}>
        {products.map(product => {
          const selected = selectedId === product.id;
          const priceText = product.precio_formateado || String(product.precio);
          return (
            <TouchableOpacity
              key={product.id}
              style={[styles.productCard, selected && styles.productCardSelected]}
              onPress={() => onSelect(product.id)}
            >
              <Text style={[styles.productName, selected && styles.productNameSelected]}>{product.nombre}</Text>
              <Text style={[styles.productMeta, selected && styles.productNameSelected]}>{priceText}</Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

export default function EditDetalleModal({
  visible,
  detalle,
  catalogo,
  selectedProductId,
  cantidad,
  observaciones,
  corriente,
  loading,
  onChangeProduct,
  onChangeCantidad,
  onChangeObservaciones,
  onChangeCorriente,
  onClose,
  onSave,
}: Props) {
  const isCorriente = detalle?.producto_nombre.toLowerCase() === 'menu corriente';
  const products = catalogo?.productos ?? [];

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
              <View style={styles.headerCopy}>
                <Text style={styles.title}>Editar producto</Text>
                <Text style={styles.subtitle}>Ajusta cantidad, notas y opciones como en la web</Text>
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
              <View style={styles.highlightCard}>
                <Text style={styles.highlightLabel}>Detalle seleccionado</Text>
                <Text style={styles.highlightValue}>{detalle?.producto_nombre ?? 'Producto'}</Text>
              </View>

              {!isCorriente ? (
                <ProductPicker
                  products={products}
                  selectedId={selectedProductId}
                  onSelect={onChangeProduct}
                />
              ) : null}

              {isCorriente && catalogo?.menu_corriente ? (
                <View style={styles.menuBox}>
                  <OptionGroup
                    title="Sopa"
                    options={['Sin sopa', ...catalogo.menu_corriente.sopas]}
                    value={corriente.sopa}
                    onSelect={value => onChangeCorriente('sopa', value)}
                  />
                  <OptionGroup
                    title="Principio"
                    options={catalogo.menu_corriente.principio}
                    value={corriente.principio}
                    onSelect={value => onChangeCorriente('principio', value)}
                  />
                  <OptionGroup
                    title="Proteina"
                    options={catalogo.menu_corriente.proteina}
                    value={corriente.proteina}
                    onSelect={value => onChangeCorriente('proteina', value)}
                  />
                  <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Acompanante</Text>
                    <TextInput
                      value={corriente.acompanante}
                      onChangeText={value => onChangeCorriente('acompanante', value)}
                      style={styles.input}
                      placeholder="Acompanante"
                      placeholderTextColor={colors.textMuted}
                    />
                  </View>
                </View>
              ) : null}

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Cantidad</Text>
                <TextInput
                  value={cantidad}
                  onChangeText={onChangeCantidad}
                  keyboardType="numeric"
                  style={styles.input}
                  placeholder="1"
                  placeholderTextColor={colors.textMuted}
                />
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Observaciones</Text>
                <TextInput
                  value={observaciones}
                  onChangeText={onChangeObservaciones}
                  style={styles.textarea}
                  placeholder="Notas del item..."
                  placeholderTextColor={colors.textMuted}
                  multiline
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
                  <Text style={styles.saveButtonText}>Guardar detalle</Text>
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
    maxHeight: '96%',
    width: '100%',
    maxWidth: 760,
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
  headerCopy: {
    flex: 1,
    paddingRight: 6,
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
    lineHeight: 16,
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
    alignSelf: 'flex-start',
    flexShrink: 0,
  },
  highlightCard: {
    backgroundColor: colors.overlayDarkCard,
    borderRadius: 18,
    padding: 14,
    marginBottom: 14,
  },
  highlightLabel: {
    color: colors.textCloud,
    fontWeight: '700',
    fontSize: 12,
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  highlightValue: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
    fontSize: 18,
  },
  section: {
    marginBottom: 14,
  },
  sectionTitle: {
    color: colors.textSlateSoft,
    fontWeight: '700',
    marginBottom: 8,
  },
  productList: {
    gap: 8,
  },
  productCard: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  productCardSelected: {
    backgroundColor: colors.infoBg,
    borderColor: colors.primary,
  },
  productName: {
    color: colors.textSlate,
    fontWeight: '800',
    marginBottom: 4,
  },
  productNameSelected: {
    color: colors.primaryDark,
  },
  productMeta: {
    color: colors.successText,
    fontWeight: '600',
  },
  menuBox: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 14,
  },
  chipWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    backgroundColor: colors.border,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 999,
  },
  chipActive: {
    backgroundColor: colors.primary,
  },
  chipText: {
    color: colors.textSlateSoft,
    fontWeight: '700',
    fontSize: 12,
  },
  chipTextActive: {
    color: colors.btnPrimaryText,
  },
  input: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: colors.textSlate,
  },
  textarea: {
    minHeight: 100,
    backgroundColor: colors.surfaceCard,
    borderRadius: 14,
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
