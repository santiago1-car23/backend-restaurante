import React from 'react';
import {
  ActivityIndicator,
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
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../../constants/colors';
import type { VoiceOrderParseResult } from '../types';

type Props = {
  visible: boolean;
  transcript: string;
  onChangeTranscript: (value: string) => void;
  parsed: VoiceOrderParseResult;
  interpreting: boolean;
  submitting: boolean;
  onClose: () => void;
  onInterpret: () => void;
  onConfirm: () => void;
};

export default function VoiceOrderPreviewModal({
  visible,
  transcript,
  onChangeTranscript,
  parsed,
  interpreting,
  submitting,
  onClose,
  onInterpret,
  onConfirm,
}: Props) {
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
              <View style={styles.headerCopy}>
                <Text style={styles.title}>Asistente por voz</Text>
                <Text style={styles.subtitle}>
                  Escribe o pega lo que dijo el cliente y el sistema intentara armar el pedido.
                </Text>
              </View>
              <TouchableOpacity onPress={onClose} style={styles.closeButton} activeOpacity={0.85}>
                <Text style={styles.closeText}>Cerrar</Text>
              </TouchableOpacity>
            </View>

            <ScrollView
              contentContainerStyle={styles.scrollContent}
              keyboardShouldPersistTaps="handled"
              showsVerticalScrollIndicator={false}
            >
              <View style={styles.notice}>
                <Ionicons name="mic-outline" size={18} color={colors.primary} />
                <Text style={styles.noticeText}>
                  Mantén presionado el botón de voz para hablar y suelta para transcribir. También puedes escribir el pedido manualmente.
                </Text>
              </View>

              <Text style={styles.label}>Frase detectada</Text>
              <TextInput
                value={transcript}
                onChangeText={onChangeTranscript}
                placeholder="Ejemplo: dos aguas y un corriente con pollo"
                placeholderTextColor={colors.textMuted}
                multiline
                style={styles.input}
              />

              <TouchableOpacity
                style={[styles.interpretButton, !transcript.trim() && styles.buttonDisabled]}
                onPress={onInterpret}
                disabled={!transcript.trim() || submitting}
              >
                {interpreting ? (
                  <Text style={styles.interpretButtonText}>Reinterpretar</Text>
                ) : (
                  <Text style={styles.interpretButtonText}>Interpretar pedido</Text>
                )}
              </TouchableOpacity>

              {interpreting ? (
                <>
                  <Text style={styles.sectionTitle}>Pedido entendido</Text>
                  {parsed.items.length ? (
                    parsed.items.map((item, index) => (
                      <View key={`${item.label}-${index}`} style={styles.itemCard}>
                        <Text style={styles.itemLabel}>{item.label}</Text>
                        <Text style={styles.itemMeta}>{item.rawText}</Text>
                      </View>
                    ))
                  ) : (
                    <View style={styles.emptyBox}>
                      <Text style={styles.emptyText}>No pude reconocer productos claros en esa frase.</Text>
                    </View>
                  )}

                  {parsed.unmatched.length ? (
                    <>
                      <Text style={styles.sectionTitle}>Partes por revisar</Text>
                      {parsed.unmatched.map((part, index) => (
                        <View key={`${part}-${index}`} style={styles.unmatchedCard}>
                          <Text style={styles.unmatchedText}>{part}</Text>
                        </View>
                      ))}
                    </>
                  ) : null}
                </>
              ) : null}
            </ScrollView>

            <View style={styles.footer}>
              <TouchableOpacity style={styles.secondaryButton} onPress={onClose} disabled={submitting}>
                <Text style={styles.secondaryButtonText}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.primaryButton,
                  (!parsed.items.length || !interpreting || submitting) && styles.buttonDisabled,
                ]}
                onPress={onConfirm}
                disabled={!parsed.items.length || !interpreting || submitting}
              >
                {submitting ? (
                  <ActivityIndicator color={colors.btnPrimaryText} />
                ) : (
                  <Text style={styles.primaryButtonText}>Agregar al pedido</Text>
                )}
              </TouchableOpacity>
            </View>
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
    maxHeight: '94%',
    width: '100%',
    maxWidth: 760,
    alignSelf: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 12,
    marginBottom: 14,
  },
  headerCopy: {
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.textSlate,
  },
  subtitle: {
    color: colors.textMuted,
    marginTop: 4,
    fontSize: 11,
    lineHeight: 16,
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
  closeText: {
    color: colors.textSlate,
    fontWeight: '700',
    fontSize: 12,
    textAlign: 'center',
  },
  scrollContent: {
    paddingBottom: 18,
  },
  notice: {
    flexDirection: 'row',
    gap: 10,
    alignItems: 'flex-start',
    backgroundColor: colors.infoBg,
    borderRadius: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: colors.primary,
    marginBottom: 14,
  },
  noticeText: {
    flex: 1,
    color: colors.primaryDark,
    fontSize: 12,
    lineHeight: 18,
    fontWeight: '600',
  },
  label: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.textSlateSoft,
    marginBottom: 8,
  },
  input: {
    minHeight: 108,
    backgroundColor: colors.surfaceCard,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 12,
    paddingVertical: 12,
    color: colors.textSlate,
    textAlignVertical: 'top',
    marginBottom: 12,
  },
  interpretButton: {
    backgroundColor: colors.textSlate,
    borderRadius: 14,
    paddingVertical: 13,
    alignItems: 'center',
    marginBottom: 14,
  },
  interpretButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: colors.textSlate,
    marginBottom: 8,
  },
  itemCard: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 10,
  },
  itemLabel: {
    color: colors.textSlate,
    fontWeight: '800',
    marginBottom: 4,
  },
  itemMeta: {
    color: colors.textMuted,
    fontSize: 12,
  },
  unmatchedCard: {
    backgroundColor: `${colors.red}10`,
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: `${colors.red}25`,
    marginBottom: 10,
  },
  unmatchedText: {
    color: colors.red,
    fontWeight: '700',
  },
  emptyBox: {
    backgroundColor: colors.surfaceCard,
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 10,
  },
  emptyText: {
    color: colors.textMuted,
    textAlign: 'center',
  },
  footer: {
    flexDirection: 'row',
    gap: 10,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: colors.surfaceCard,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: 14,
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: colors.textSlate,
    fontWeight: '800',
  },
  primaryButton: {
    flex: 1.2,
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: colors.btnPrimaryText,
    fontWeight: '800',
  },
  buttonDisabled: {
    opacity: 0.55,
  },
});
