import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Modal,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { colors } from '../../../constants/colors';

import type { CatalogoPedido, Categoria, Producto } from '../../pedidos/services/pedidosService';

type TabKey = 'productos' | 'corriente' | 'desayuno';

interface AddDetalleModalProps {
  visible: boolean;
  catalogo: CatalogoPedido | null;
  selectedProductId: number | null;
  onSelectProduct: (id: number | null) => void;
  cantidad: string;
  onChangeCantidad: (value: string) => void;
  observaciones: string;
  onChangeObservaciones: (value: string) => void;
  loading: boolean;
  onClose: () => void;
  onAgregarProducto: () => void;
  onAgregarCorriente: () => void;
  onAgregarDesayuno: () => void;
  corriente: {
    sopa: string;
    principio: string;
    proteina: string;
    acompanante: string;
  };
  onChangeCorriente: (field: 'sopa' | 'principio' | 'proteina' | 'acompanante', value: string) => void;
  desayuno: {
    principal: string;
    bebida: string;
    acompanante: string;
  };
  onChangeDesayuno: (field: 'principal' | 'bebida' | 'acompanante', value: string) => void;
}

function TabButton({
  label,
  active,
  onPress,
}: {
  label: string;
  active: boolean;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity onPress={onPress} style={[styles.tabButton, active && styles.tabButtonActive]}>
      <Text style={[styles.tabButtonText, active && styles.tabButtonTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

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
              onPress={() => onSelect(option)}
              style={[styles.chip, selected && styles.chipSelected]}
            >
              <Text style={[styles.chipText, selected && styles.chipTextSelected]}>{option}</Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

function CategoryChip({
  label,
  active,
  onPress,
}: {
  label: string;
  active: boolean;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity onPress={onPress} style={[styles.categoryChip, active && styles.categoryChipActive]}>
      <Text style={[styles.categoryChipText, active && styles.categoryChipTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

function ProductCard({
  item,
  selected,
  onPress,
}: {
  item: Producto;
  selected: boolean;
  onPress: () => void;
}) {
  const price = typeof item.precio === 'number' ? item.precio : Number(item.precio || 0);
  const priceText = item.precio_formateado || `$${price.toFixed(2)}`;

  return (
    <TouchableOpacity style={[styles.productCard, selected && styles.productCardSelected]} onPress={onPress}>
      <View style={styles.productTopRow}>
        <Text style={styles.productName}>{item.nombre}</Text>
        <Text style={styles.productPrice}>{priceText}</Text>
      </View>
      <Text style={styles.productMeta}>{item.categoria_nombre || 'Sin categoria'}</Text>
      {item.descripcion ? <Text style={styles.productDescription}>{item.descripcion}</Text> : null}
    </TouchableOpacity>
  );
}

function QuantityAndNotes({
  cantidad,
  observaciones,
  onChangeCantidad,
  onChangeObservaciones,
}: {
  cantidad: string;
  observaciones: string;
  onChangeCantidad: (value: string) => void;
  onChangeObservaciones: (value: string) => void;
}) {
  return (
    <>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Cantidad</Text>
        <TextInput
          value={cantidad}
          onChangeText={onChangeCantidad}
          keyboardType="numeric"
          style={styles.input}
          placeholder="1"
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Observaciones</Text>
        <TextInput
          value={observaciones}
          onChangeText={onChangeObservaciones}
          style={[styles.input, styles.textarea]}
          placeholder="Notas de cocina..."
          multiline
        />
      </View>
    </>
  );
}

function buildCategoryOptions(catalogo: CatalogoPedido) {
  const snacksId = catalogo.categoria_snacks_id;
  const hiddenNames = ['corriente', 'desayuno', 'snacks'];

  const regularCategories = catalogo.categorias.filter(cat => !hiddenNames.includes(cat.nombre.toLowerCase()));

  return {
    regularCategories,
    snacksCategory: snacksId ? catalogo.categorias.find(cat => cat.id === snacksId) ?? null : null,
  };
}

function filterProducts(products: Producto[], search: string, categoryId: number | null) {
  const normalizedSearch = search.trim().toLowerCase();

  return products.filter(product => {
    const matchesCategory = categoryId ? product.categoria === categoryId : true;
    const haystack = `${product.nombre} ${product.descripcion} ${product.categoria_nombre}`.toLowerCase();
    const matchesSearch = normalizedSearch ? haystack.includes(normalizedSearch) : true;
    return matchesCategory && matchesSearch;
  });
}

export default function AddDetalleModal({
  visible,
  catalogo,
  selectedProductId,
  onSelectProduct,
  cantidad,
  onChangeCantidad,
  observaciones,
  onChangeObservaciones,
  loading,
  onClose,
  onAgregarProducto,
  onAgregarCorriente,
  onAgregarDesayuno,
  corriente,
  onChangeCorriente,
  desayuno,
  onChangeDesayuno,
}: AddDetalleModalProps) {
  const [activeTab, setActiveTab] = useState<TabKey>('productos');
  const [search, setSearch] = useState('');
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);

  useEffect(() => {
    if (visible) {
      setActiveTab('productos');
      setSearch('');
      setSelectedCategoryId(null);
    }
  }, [visible]);

  const changeTab = (tab: TabKey) => {
    setActiveTab(tab);
    if (tab !== 'productos' && selectedProductId !== null) {
      onSelectProduct(null);
    }
  };

  const categoryData = useMemo(() => {
    if (!catalogo) {
      return { regularCategories: [] as Categoria[], snacksCategory: null as Categoria | null };
    }
    return buildCategoryOptions(catalogo);
  }, [catalogo]);

  const visibleProducts = useMemo(() => {
    if (!catalogo) {
      return [] as Producto[];
    }
    return filterProducts(catalogo.productos, search, selectedCategoryId);
  }, [catalogo, search, selectedCategoryId]);

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <KeyboardAvoidingView
          style={styles.keyboardWrap}
          behavior={Platform.OS === 'ios' ? 'padding' : 'position'}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 22 : 24}
        >
          <View style={styles.container}>
            <View style={styles.header}>
              <View>
                <Text style={styles.title}>Agregar al pedido</Text>

              </View>
              <TouchableOpacity onPress={onClose} style={styles.closeButton} activeOpacity={0.85}>
                <Text style={styles.close}>Cerrar</Text>
              </TouchableOpacity>
            </View>

            {!catalogo ? (
              <View style={styles.loaderBox}>
                <ActivityIndicator size="large" color={colors.primary} />
              </View>
            ) : (
              <>
                <View style={styles.tabRow}>
                  <TabButton label="Productos" active={activeTab === 'productos'} onPress={() => changeTab('productos')} />
                  <TabButton label="Corriente" active={activeTab === 'corriente'} onPress={() => changeTab('corriente')} />
                  <TabButton label="Desayuno" active={activeTab === 'desayuno'} onPress={() => changeTab('desayuno')} />
                </View>

                <ScrollView
                  showsVerticalScrollIndicator={false}
                  keyboardShouldPersistTaps="handled"
                  keyboardDismissMode="interactive"
                  contentContainerStyle={styles.scrollContent}
                >
                  {activeTab === 'productos' ? (
                    <>
                      <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Filtrar por categoria</Text>
                        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.categoryRow}>
                          <CategoryChip label="Todos" active={selectedCategoryId === null} onPress={() => setSelectedCategoryId(null)} />
                          {categoryData.snacksCategory ? (
                            <CategoryChip
                              label={categoryData.snacksCategory.nombre}
                              active={selectedCategoryId === categoryData.snacksCategory.id}
                              onPress={() => setSelectedCategoryId(categoryData.snacksCategory!.id)}
                            />
                          ) : null}
                          {categoryData.regularCategories.map(category => (
                            <CategoryChip
                              key={category.id}
                              label={category.nombre}
                              active={selectedCategoryId === category.id}
                              onPress={() => setSelectedCategoryId(category.id)}
                            />
                          ))}
                        </ScrollView>
                      </View>

                      <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Buscar producto</Text>
                        <TextInput
                          value={search}
                          onChangeText={setSearch}
                          style={styles.input}
                          placeholder="Buscar por nombre o descripcion"
                        />
                      </View>

                      <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Productos disponibles</Text>
                        {visibleProducts.length ? (
                          <FlatList
                            data={visibleProducts}
                            keyExtractor={item => item.id.toString()}
                            scrollEnabled={false}
                            renderItem={({ item }) => (
                              <ProductCard
                                item={item}
                                selected={selectedProductId === item.id}
                                onPress={() => onSelectProduct(item.id)}
                              />
                            )}
                          />
                        ) : (
                          <View style={styles.emptyBox}>
                            <Text style={styles.emptyText}>No hay productos para ese filtro.</Text>
                          </View>
                        )}
                      </View>

                      <QuantityAndNotes
                        cantidad={cantidad}
                        observaciones={observaciones}
                        onChangeCantidad={onChangeCantidad}
                        onChangeObservaciones={onChangeObservaciones}
                      />

                      <TouchableOpacity
                        style={[styles.primaryButton, loading && styles.disabledButton]}
                        onPress={onAgregarProducto}
                        disabled={loading}
                      >
                        {loading ? <ActivityIndicator color={colors.btnPrimaryText} /> : <Text style={styles.primaryButtonText}>Agregar producto</Text>}
                      </TouchableOpacity>
                    </>
                  ) : null}

                  {activeTab === 'corriente' ? (
                    catalogo.menu_corriente ? (
                      <View style={styles.box}>
                        <Text style={styles.boxTitle}>Opciones Corriente</Text>
                        <View style={styles.priceBanner}>
                          <Text style={styles.priceBannerLabel}>Precios del dia</Text>
                          <Text style={styles.priceBannerValue}>
                            Sopa {catalogo.menu_corriente.precio_sopa_formateado || catalogo.menu_corriente.precio_sopa}
                          </Text>
                          <Text style={styles.priceBannerValue}>
                            Bandeja {catalogo.menu_corriente.precio_bandeja_formateado || catalogo.menu_corriente.precio_bandeja}
                          </Text>
                          <Text style={styles.priceBannerValue}>
                            Completo {catalogo.menu_corriente.precio_completo_formateado || catalogo.menu_corriente.precio_completo}
                          </Text>
                        </View>
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
                          />
                        </View>
                        <QuantityAndNotes
                          cantidad={cantidad}
                          observaciones={observaciones}
                          onChangeCantidad={onChangeCantidad}
                          onChangeObservaciones={onChangeObservaciones}
                        />
                        <TouchableOpacity
                          style={[styles.secondaryButton, loading && styles.disabledButton]}
                          onPress={onAgregarCorriente}
                          disabled={loading}
                        >
                          <Text style={styles.secondaryButtonText}>Agregar corriente</Text>
                        </TouchableOpacity>
                      </View>
                    ) : (
                      <View style={styles.emptyBox}>
                        <Text style={styles.emptyText}>No hay menu corriente configurado para hoy.</Text>
                      </View>
                    )
                  ) : null}

                  {activeTab === 'desayuno' ? (
                    catalogo.menu_desayuno ? (
                      <View style={styles.box}>
                        <Text style={styles.boxTitle}>Opciones Desayuno</Text>
                        <View style={styles.priceBanner}>
                          <Text style={styles.priceBannerLabel}>Precio del desayuno</Text>
                          <Text style={styles.priceBannerValue}>
                            {catalogo.menu_desayuno.precio_desayuno_formateado || catalogo.menu_desayuno.precio_desayuno}
                          </Text>
                        </View>
                        <OptionGroup
                          title="Principal"
                          options={catalogo.menu_desayuno.principales}
                          value={desayuno.principal}
                          onSelect={value => onChangeDesayuno('principal', value)}
                        />
                        <OptionGroup
                          title="Bebida"
                          options={catalogo.menu_desayuno.bebidas}
                          value={desayuno.bebida}
                          onSelect={value => onChangeDesayuno('bebida', value)}
                        />
                        <View style={styles.section}>
                          <Text style={styles.sectionTitle}>Acompanante</Text>
                          <TextInput
                            value={desayuno.acompanante}
                            onChangeText={value => onChangeDesayuno('acompanante', value)}
                            style={styles.input}
                            placeholder="Acompanante"
                          />
                        </View>
                        <QuantityAndNotes
                          cantidad={cantidad}
                          observaciones={observaciones}
                          onChangeCantidad={onChangeCantidad}
                          onChangeObservaciones={onChangeObservaciones}
                        />
                        <TouchableOpacity
                          style={[styles.warningButton, loading && styles.disabledButton]}
                          onPress={onAgregarDesayuno}
                          disabled={loading}
                        >
                          <Text style={styles.warningButtonText}>Agregar desayuno</Text>
                        </TouchableOpacity>
                      </View>
                    ) : (
                      <View style={styles.emptyBox}>
                        <Text style={styles.emptyText}>No hay menu desayuno configurado para hoy.</Text>
                      </View>
                    )
                  ) : null}
                </ScrollView>
              </>
            )}
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
    paddingBottom: 30,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
    gap: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.textSlate,
  },
  subtitle: {
    color: colors.textMuted,
    marginTop: 3,
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
  loaderBox: {
    paddingVertical: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 14,
    backgroundColor: colors.border,
    borderRadius: 18,
    padding: 4,
  },
  tabButton: {
    flex: 1,
    paddingVertical: 11,
    borderRadius: 14,
    alignItems: 'center',
  },
  tabButtonActive: {
    backgroundColor: colors.textSlate,
  },
  tabButtonText: {
    color: colors.textSlateSoft,
    fontWeight: '700',
    fontSize: 13,
  },
  tabButtonTextActive: {
    color: colors.btnPrimaryText,
  },
  section: {
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.textSlateSoft,
    marginBottom: 8,
  },
  categoryRow: {
    gap: 8,
    paddingRight: 12,
  },
  categoryChip: {
    paddingHorizontal: 12,
    paddingVertical: 9,
    borderRadius: 999,
    backgroundColor: colors.border,
  },
  categoryChipActive: {
    backgroundColor: colors.primary,
  },
  categoryChipText: {
    color: colors.textSlateSoft,
    fontSize: 12,
    fontWeight: '700',
  },
  categoryChipTextActive: {
    color: colors.btnPrimaryText,
  },
  productCard: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 14,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  productCardSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.infoBg,
  },
  productTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 12,
  },
  productName: {
    flex: 1,
    fontWeight: '800',
    color: colors.textSlate,
    marginBottom: 4,
  },
  productMeta: {
    color: colors.textMuted,
    fontSize: 12,
  },
  productDescription: {
    color: colors.textSlateSoft,
    fontSize: 12,
    marginTop: 6,
  },
  productPrice: {
    color: colors.successText,
    fontWeight: '800',
  },
  input: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 12,
    paddingVertical: 12,
    color: colors.textSlate,
  },
  textarea: {
    minHeight: 84,
    textAlignVertical: 'top',
  },
  primaryButton: {
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 18,
  },
  primaryButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  secondaryButton: {
    marginTop: 10,
    backgroundColor: colors.buttonTealBg,
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  warningButton: {
    marginTop: 10,
    backgroundColor: colors.buttonWarningBg,
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 12,
  },
  warningButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  disabledButton: {
    opacity: 0.6,
  },
  chipWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: colors.border,
  },
  chipSelected: {
    backgroundColor: colors.primary,
  },
  chipText: {
    color: colors.textSlateSoft,
    fontSize: 12,
    fontWeight: '700',
  },
  chipTextSelected: {
    color: colors.btnPrimaryText,
  },
  box: {
    marginTop: 4,
    marginBottom: 16,
    backgroundColor: colors.surfaceCard,
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
  },
  boxTitle: {
    fontWeight: '800',
    color: colors.textSlate,
    marginBottom: 12,
    fontSize: 16,
  },
  priceBanner: {
    backgroundColor: colors.surfaceSoft,
    borderRadius: 14,
    padding: 12,
    marginBottom: 12,
  },
  priceBannerLabel: {
    color: colors.textSlateSoft,
    fontSize: 12,
    fontWeight: '700',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  priceBannerValue: {
    color: colors.successText,
    fontWeight: '800',
    marginBottom: 2,
  },
  emptyBox: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 16,
  },
  emptyText: {
    color: colors.textMuted,
    textAlign: 'center',
  },
});
