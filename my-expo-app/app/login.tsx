

import React, { useState } from 'react';
import { Redirect } from 'expo-router';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Image,
  TouchableOpacity,
  ImageBackground,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { colors } from '../constants/colors';
import { useAuth } from '../context/AuthContext';


export default function LoginScreen({ navigation }: any) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const { login, loading, token } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  if (token) {
    return <Redirect href="/pedidos" />;
  }

  const handleLogin = async () => {
    setLoginError('');
    try {
      const result = await login(username, password);
      if (result !== true) {
        setLoginError('Usuario o contraseña inválido');
      }
    } catch {
      setLoginError('Usuario o contraseña inválido');
    }
  };

  return (
    <ImageBackground source={require('../assets/images/fondologin.png')} style={styles.bg} resizeMode="cover">
      <View style={styles.overlay}>
        <KeyboardAvoidingView
          style={styles.keyboardWrap}
          behavior={Platform.OS === 'ios' ? 'padding' : 'position'}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 28 : 28}
        >
          <ScrollView
            contentContainerStyle={styles.centered}
            keyboardShouldPersistTaps="handled"
            keyboardDismissMode="interactive"
          >
            <View style={[styles.glassCard, loginError ? styles.glassCardError : null]}>
              <View style={styles.brandBadge}>
                <Text style={styles.brandBadgeText}>Acceso seguro</Text>
              </View>
              <Image source={require('../assets/images/logologin.png')} style={styles.logo} resizeMode="contain" />
              <Text style={styles.title}>Bienvenido</Text>
              <Text style={styles.subtitle}>ODERIXSISTEM</Text>
              <Text style={styles.helper}>Ingresa para pedidos, mesas y cocina desde el movil.</Text>
              {loginError ? (
                <View style={styles.errorBanner}>
                  <Text style={styles.errorBannerText}>{loginError}</Text>
                </View>
              ) : null}
              <View style={styles.inputBox}>
                <TextInput
                  style={[styles.input, loginError ? styles.inputError : null]}
                  placeholder="Usuario"
                  placeholderTextColor={colors.textMutedDark}
                  value={username}
                  onChangeText={value => {
                    setUsername(value);
                    if (loginError) {
                      setLoginError('');
                    }
                  }}
                  autoCapitalize="none"
                />
              </View>
              <View style={styles.inputBox}>
                <TextInput
                  style={[styles.input, loginError ? styles.inputError : null]}
                  placeholder="Contraseña"
                  placeholderTextColor={colors.textMutedDark}
                  value={password}
                  onChangeText={value => {
                    setPassword(value);
                    if (loginError) {
                      setLoginError('');
                    }
                  }}
                  secureTextEntry={!showPassword}
                />
                <TouchableOpacity style={styles.eyeBtn} onPress={() => setShowPassword((v) => !v)}>
                  <Text style={{ color: colors.textMutedDark, fontSize: 15 }}>{showPassword ? '🙈' : '👁️'}</Text>
                </TouchableOpacity>
              </View>
              <View style={styles.rowOptions}>
                <View style={styles.rowLeft}>
                  <View style={styles.radio} />
                  <Text style={styles.remember}>Recordarme</Text>
                </View>
              </View>
              <TouchableOpacity style={styles.btnWrapper} onPress={handleLogin} disabled={loading}>
                <View style={[styles.btnGradient, { backgroundColor: colors.primary }]}> 
                  <Text style={styles.btnText}>{loading ? 'Cargando...' : 'Ingresar'}</Text>
                </View>
              </TouchableOpacity>
              <Text style={styles.powered}>Impulsado por <Text style={{ fontWeight: 'bold', color: colors.bgSidebar }}>Oderix Sistem</Text></Text>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  bg: {
    flex: 1,
    backgroundColor: colors.bgBodyDark,
  },
  overlay: {
    flex: 1,
    backgroundColor: colors.overlayDarkSoft,
  },
  keyboardWrap: {
    flex: 1,
  },
  centered: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
    paddingHorizontal: 20,
    paddingTop: 28,
    paddingBottom: 56,
  },
  glassCard: {
    width: '105%',
    maxWidth: 620,
    borderRadius: 32,
    backgroundColor: colors.overlayDarkStrong,
    borderWidth: 1.5,
    borderColor: colors.overlayDarkBorder,
    padding: 30,
    alignItems: 'center',
    shadowColor: colors.shadowBaseDark,
    shadowOpacity: 0.18,
    shadowRadius: 24,
    shadowOffset: { width: 0, height: 8 },
    marginVertical: 18,
  },
  glassCardError: {
    borderColor: colors.red,
    shadowColor: colors.redDark,
    shadowOpacity: 0.24,
  },
  brandBadge: {
    alignSelf: 'flex-start',
    backgroundColor: colors.overlayLightSoft,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
    marginBottom: 14,
  },
  brandBadgeText: {
    color: colors.textIce,
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  logo: {
    width: 132,
    height: 132,
    marginBottom: 16,
    borderRadius: 80,
    backgroundColor: colors.overlayLightSoft,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.bgSidebar,
    marginBottom: 4,
    textAlign: 'center',
    alignSelf: 'center',
  },
  subtitle: {
    color: colors.textMutedDark,
    fontSize: 15,
    letterSpacing: 1.8,
    marginBottom: 10,
    textAlign: 'center',
    alignSelf: 'center',
  },
  helper: {
    color: colors.textCloud,
    fontSize: 13,
    lineHeight: 20,
    textAlign: 'center',
    marginBottom: 22,
  },
  inputBox: {
    width: '100%',
    marginBottom: 16,
    position: 'relative',
  },
  input: {
    width: '100%',
    borderWidth: 1,
    borderColor: colors.overlayLightBorder,
    backgroundColor: colors.overlayLightInput,
    color: colors.bgSidebar,
    borderRadius: 12,
    padding: 14,
    paddingRight: 44,
    fontSize: 16,
  },
  inputError: {
    borderColor: colors.red,
    backgroundColor: 'rgba(244, 67, 54, 0.08)',
  },
  errorBanner: {
    width: '100%',
    borderRadius: 14,
    backgroundColor: 'rgba(244, 67, 54, 0.14)',
    borderWidth: 1,
    borderColor: colors.red,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 16,
  },
  errorBannerText: {
    color: '#fecaca',
    fontWeight: '700',
    textAlign: 'center',
  },
  eyeBtn: {
    position: 'absolute',
    right: 14,
    top: 0,
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    width: 32,
  },
  rowOptions: {
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 18,
  },
  rowLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  radio: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 1.5,
    borderColor: colors.textMutedDark,
    marginRight: 6,
  },
  remember: {
    color: colors.textMutedDark,
    fontSize: 14,
  },
  forgot: {
    color: colors.accent,
    fontSize: 14,
    textDecorationLine: 'underline',
  },
  btnWrapper: {
    width: '100%',
    marginTop: 8,
    marginBottom: 18,
    borderRadius: 32,
    overflow: 'hidden',
    elevation: 2,
  },
  btnGradient: {
    width: '100%',
    paddingVertical: 16,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.primaryDark,
    shadowOpacity: 0.18,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
  },
  btnText: {
    color: colors.bgSidebar,
    fontWeight: 'bold',
    fontSize: 18,
    letterSpacing: 1,
  },
  powered: {
    color: colors.bgSidebar,
    fontSize: 13,
    marginTop: 18,
    marginBottom: 0,
    textAlign: 'center',
  },
  footer: {
    color: colors.textMutedDark,
    fontSize: 11,
    textAlign: 'center',
    marginTop: 10,
    opacity: 0.7,
  },
});
