import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../../../constants/colors';

export default function EmptyState() {
  return (
    <View style={styles.container}>
      <Text style={styles.icon}>🧾</Text>
      <Text style={styles.text}>No hay pedidos activos en este momento.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', justifyContent: 'center', paddingVertical: 60 },
  icon: { fontSize: 60, color: colors.border },
  text: { color: colors.textMuted, fontSize: 16, marginTop: 16, textAlign: 'center' },
});
