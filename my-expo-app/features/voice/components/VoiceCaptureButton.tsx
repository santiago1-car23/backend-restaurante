import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../../constants/colors';

type Props = {
  disabled?: boolean;
  listening?: boolean;
  onPress: () => void;
  onLongPress?: () => void;
  onPressOut?: () => void;
};

export default function VoiceCaptureButton({
  disabled,
  listening,
  onPress,
  onLongPress,
  onPressOut,
}: Props) {
  return (
    <TouchableOpacity
      style={[styles.button, disabled && styles.buttonDisabled]}
      onPress={onPress}
      onLongPress={onLongPress}
      onPressOut={onPressOut}
      delayLongPress={220}
      activeOpacity={0.9}
      disabled={disabled}
    >
      <View style={styles.iconWrap}>
        <Ionicons name={listening ? 'radio-outline' : 'mic-outline'} size={18} color={colors.btnPrimaryText} />
      </View>
      <Text style={styles.text}>
        {disabled ? 'Bloqueado' : listening ? 'Escuchando... suelta para enviar' : 'Mantén para hablar'}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: colors.textSlate,
    borderRadius: 18,
    paddingVertical: 13,
    paddingHorizontal: 14,
    shadowColor: colors.shadowSlate,
    shadowOpacity: 0.12,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 14,
    elevation: 3,
  },
  buttonDisabled: {
    opacity: 0.55,
  },
  iconWrap: {
    width: 28,
    height: 28,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.overlayLightSoft,
  },
  text: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
    fontSize: 12,
    textAlign: 'center',
  },
});
