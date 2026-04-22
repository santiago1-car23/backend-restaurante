import React, { useMemo, useState } from 'react';
import { Image, ScrollView, StyleSheet, Switch, Text, TouchableOpacity, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Redirect } from 'expo-router';

import { colors } from '@/constants/colors';
import { useAuth } from '@/context/AuthContext';
import ActionCardModal, { ActionCardButton } from '@/features/ui/ActionCardModal';
import notificacionesSettingsService from '@/features/notificaciones/services/notificacionesSettingsService';
import { isCocinero } from '@/features/auth/roleUtils';

type FeedbackState = {
  visible: boolean;
  icon?: keyof typeof Ionicons.glyphMap;
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

type SettingRowProps = {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  subtitle?: string;
  accentColor?: string;
  rightNode?: React.ReactNode;
  onPress?: () => void;
};

function SettingRow({
  icon,
  title,
  subtitle,
  accentColor = colors.infoBg,
  rightNode,
  onPress,
}: SettingRowProps) {
  const Container = onPress ? TouchableOpacity : View;

  return (
    <Container style={styles.row} activeOpacity={0.85} onPress={onPress}>
      <View style={[styles.rowIconWrap, { backgroundColor: accentColor }]}>
        <Ionicons name={icon} size={18} color={colors.textSlate} />
      </View>
      <View style={styles.rowCopy}>
        <Text style={styles.rowTitle}>{title}</Text>
        {subtitle ? <Text style={styles.rowSubtitle}>{subtitle}</Text> : null}
      </View>
      {rightNode ? rightNode : <Ionicons name="chevron-forward-outline" size={18} color={colors.textMuted} />}
    </Container>
  );
}

export default function AjustesScreen() {
  const { token, loading: authLoading, user } = useAuth();
  const usuarioEsCocinero = isCocinero(user);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [themeMode, setThemeMode] = useState<'Claro' | 'Oscuro'>('Claro');
  const [language, setLanguage] = useState<'Español' | 'English'>('Español');
  const [feedback, setFeedback] = useState<FeedbackState>(initialFeedbackState);

  const closeFeedback = () => setFeedback(initialFeedbackState);

  const fullName = useMemo(() => {
    const firstName = user?.first_name?.trim?.() || '';
    const lastName = user?.last_name?.trim?.() || '';
    const merged = `${firstName} ${lastName}`.trim();
    return merged || user?.username || 'Usuario';
  }, [user?.first_name, user?.last_name, user?.username]);

  const profileEmail = user?.email || `${user?.username || 'usuario'}@oderixsistem.com`;
  const avatarSource = { uri: `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=e0f4f8&color=0f172a&size=256` };

  const showSoon = (title: string, message: string, icon: keyof typeof Ionicons.glyphMap) => {
    setFeedback({
      visible: true,
      icon,
      title,
      message,
      actions: [{ label: 'Entendido', onPress: closeFeedback, tone: 'primary' }],
    });
  };

  const handleThemeToggle = () => {
    setThemeMode(prev => (prev === 'Claro' ? 'Oscuro' : 'Claro'));
  };

  const handleLanguageToggle = () => {
    setLanguage(prev => (prev === 'Español' ? 'English' : 'Español'));
  };

  React.useEffect(() => {
    let active = true;
    const loadSettings = async () => {
      const enabled = await notificacionesSettingsService.getEnabled();
      if (active) {
        setNotificationsEnabled(enabled);
      }
    };
    loadSettings();
    return () => {
      active = false;
    };
  }, []);

  const handleNotificationToggle = async (value: boolean) => {
    setNotificationsEnabled(value);
    await notificacionesSettingsService.setEnabled(value);
  };

  if (!authLoading && !token) {
    return <Redirect href="/login" />;
  }

  if (!authLoading && token && usuarioEsCocinero) {
    return <Redirect href="/pedidos" />;
  }

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.headerCard}>
          <View style={styles.avatarOuter}>
            <Image source={avatarSource} style={styles.avatar} />
          </View>
          <TouchableOpacity
            style={styles.editProfileFab}
            onPress={() => showSoon('Editar perfil', 'Esta acción estará conectada con edición de perfil en una siguiente iteración.', 'create-outline')}
          >
            <Ionicons name="create-outline" size={14} color={colors.btnPrimaryText} />
          </TouchableOpacity>
          <Text style={styles.name}>{fullName}</Text>
          <Text style={styles.email}>{profileEmail}</Text>
        </View>

        <Text style={styles.sectionTitle}>Cuenta</Text>
        <View style={styles.card}>
          <SettingRow
            icon="person-outline"
            title="Editar perfil"
            accentColor="#dedcff"
            onPress={() => showSoon('Editar perfil', 'Esta acción estará conectada con edición de perfil en una siguiente iteración.', 'person-outline')}
          />
          <SettingRow
            icon="lock-closed-outline"
            title="Seguridad y contraseña"
            accentColor="#dedcff"
            onPress={() => showSoon('Seguridad', 'Aquí podrás cambiar contraseña y reforzar seguridad de la cuenta.', 'shield-checkmark-outline')}
          />
        </View>

        <Text style={styles.sectionTitle}>Preferencias</Text>
        <View style={styles.card}>
          <SettingRow
            icon="notifications-outline"
            title="Notificaciones"
            accentColor="#c7f9d7"
            rightNode={(
              <Switch
                value={notificationsEnabled}
                onValueChange={handleNotificationToggle}
                thumbColor={colors.btnPrimaryText}
                trackColor={{ false: '#cbd5e1', true: colors.primary }}
              />
            )}
          />
          <SettingRow
            icon="contrast-outline"
            title="Tema"
            accentColor="#c7f9d7"
            rightNode={(
              <TouchableOpacity style={styles.badgeButton} onPress={handleThemeToggle} activeOpacity={0.85}>
                <Ionicons
                  name={themeMode === 'Claro' ? 'sunny-outline' : 'moon-outline'}
                  size={14}
                  color={colors.textSlate}
                />
                <Text style={styles.badgeButtonText}>{themeMode}</Text>
              </TouchableOpacity>
            )}
          />
          <SettingRow
            icon="language-outline"
            title="Idioma"
            accentColor="#c7f9d7"
            rightNode={(
              <TouchableOpacity style={styles.badgeButton} onPress={handleLanguageToggle} activeOpacity={0.85}>
                <Text style={styles.badgeButtonText}>{language}</Text>
              </TouchableOpacity>
            )}
          />
        </View>

        <Text style={styles.sectionTitle}>Soporte</Text>
        <View style={styles.card}>
          <SettingRow
            icon="help-circle-outline"
            title="Ayuda y centro de soporte"
            accentColor="#eceff4"
            onPress={() => showSoon('Centro de soporte', 'Aquí verás guías y contacto de soporte.', 'help-buoy-outline')}
          />
          <SettingRow
            icon="document-text-outline"
            title="Términos y condiciones"
            accentColor="#eceff4"
            onPress={() => showSoon('Términos y condiciones', 'Pronto mostraremos los términos completos dentro de la app.', 'document-text-outline')}
          />
        </View>
      </ScrollView>

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
  content: {
    paddingHorizontal: 16,
    paddingTop: 34,
    paddingBottom: 150,
    width: '100%',
    maxWidth: 860,
    alignSelf: 'center',
  },
  headerCard: {
    alignItems: 'center',
    backgroundColor: colors.surfaceCardGlassStrong,
    borderRadius: 26,
    borderWidth: 1,
    borderColor: colors.surfaceCardBorder,
    paddingTop: 26,
    paddingBottom: 20,
    marginBottom: 16,
    position: 'relative',
    overflow: 'hidden',
  },
  avatarOuter: {
    width: 108,
    height: 108,
    borderRadius: 54,
    borderWidth: 3,
    borderColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.surfaceCard,
  },
  avatar: {
    width: 94,
    height: 94,
    borderRadius: 47,
  },
  editProfileFab: {
    position: 'absolute',
    top: 98,
    left: '50%',
    marginLeft: 28,
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    borderWidth: 2,
    borderColor: colors.surfaceCard,
  },
  name: {
    marginTop: 12,
    fontSize: 30,
    fontWeight: '900',
    color: colors.textSlate,
    letterSpacing: -0.8,
  },
  email: {
    marginTop: 2,
    fontSize: 13,
    color: colors.textMuted,
    fontWeight: '600',
  },
  sectionTitle: {
    marginTop: 8,
    marginBottom: 8,
    marginLeft: 6,
    fontSize: 14,
    fontWeight: '800',
    color: colors.textSlateSoft,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
  },
  card: {
    backgroundColor: colors.surfaceCardGlassStrong,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.surfaceCardBorderSoft,
    paddingVertical: 8,
    paddingHorizontal: 10,
    marginBottom: 12,
    gap: 2,
    shadowColor: colors.shadowBase,
    shadowOpacity: 0.14,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 16,
    elevation: 3,
  },
  row: {
    minHeight: 62,
    borderRadius: 16,
    paddingHorizontal: 10,
    paddingVertical: 10,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  rowIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rowCopy: {
    flex: 1,
  },
  rowTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: colors.textSlate,
  },
  rowSubtitle: {
    marginTop: 2,
    fontSize: 12,
    color: colors.textMuted,
  },
  badgeButton: {
    minWidth: 92,
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 999,
    backgroundColor: colors.surfaceSoft,
    borderWidth: 1,
    borderColor: colors.border,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  badgeButtonText: {
    fontSize: 12,
    fontWeight: '800',
    color: colors.textSlateSoft,
    textTransform: 'uppercase',
  },
});
