import React from 'react';
import { ActivityIndicator, Modal, Pressable, StyleSheet, Text, View, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../constants/colors';

type ActionTone = 'primary' | 'danger' | 'neutral';

export type ActionCardButton = {
  label: string;
  onPress: () => void | Promise<void>;
  tone?: ActionTone;
  loading?: boolean;
};

type Props = {
  visible: boolean;
  icon?: keyof typeof Ionicons.glyphMap;
  title: string;
  message: string;
  onClose: () => void;
  actions: ActionCardButton[];
};

// Helper para limpiar el render y manejar estilos de botones
const getButtonStyle = (tone: ActionTone = 'primary') => {
  const stylesMap = {
    danger: { bg: colors.red + '15', text: colors.red, border: 'transparent' }, // Fondo suave para peligro
    neutral: { bg: colors.surfaceSoft, text: colors.textSlate, border: 'transparent' },
    primary: { bg: colors.primary, text: '#FFFFFF', border: 'transparent' },
  };
  return stylesMap[tone];
};

export default function ActionCardModal({ visible, icon, title, message, onClose, actions }: Props) {
  return (
    <Modal visible={visible} animationType="fade" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
        
        <View style={styles.card}>
          {/* Icono más estilizado */}
          {icon && (
            <View style={styles.iconContainer}>
              <View style={styles.iconBg} />
              <Ionicons name={icon} size={32} color={colors.primary} />
            </View>
          )}

          <Text style={styles.title}>{title}</Text>
          <Text style={styles.message}>{message}</Text>

          <View style={styles.actionStack}>
            {actions.map((action, index) => {
              const style = getButtonStyle(action.tone);
              const isPrimary = action.tone === 'primary' || !action.tone;

              return (
                <TouchableOpacity
                  key={`${action.label}-${index}`}
                  activeOpacity={0.7}
                  onPress={action.onPress}
                  disabled={action.loading}
                  style={[
                    styles.button,
                    { backgroundColor: style.bg },
                    isPrimary && styles.primaryShadow
                  ]}
                >
                  {action.loading ? (
                    <ActivityIndicator color={style.text} size="small" />
                  ) : (
                    <Text style={[styles.buttonText, { color: style.text }]}>
                      {action.label}
                    </Text>
                  )}
                </TouchableOpacity>
              );
            })}
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)', // Oscurecido más suave
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  card: {
    width: '100%',
    maxWidth: 340, // Un poco más estrecho se ve más elegante
    backgroundColor: '#FFFFFF',
    borderRadius: 32,
    padding: 24,
    alignItems: 'center', // Centrado de contenido
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 10,
  },
  iconContainer: {
    width: 64,
    height: 64,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  iconBg: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: colors.primary,
    opacity: 0.1,
    borderRadius: 22,
    transform: [{ rotate: '15deg' }], // Toque moderno
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.textSlate,
    textAlign: 'center',
    marginBottom: 10,
  },
  message: {
    fontSize: 15,
    color: colors.textSlateSoft,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 28,
    paddingHorizontal: 10,
  },
  actionStack: {
    width: '100%',
    gap: 12,
  },
  button: {
    width: '100%',
    height: 56,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryShadow: {
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '700',
  },
});