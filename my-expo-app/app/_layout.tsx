import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack, usePathname, useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import React, { useMemo, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import 'react-native-reanimated';

import { useColorScheme } from '@/hooks/use-color-scheme';
import { AuthProvider, useAuth } from '../context/AuthContext';
import FloatingActionDock from '../features/pedidos/components/FloatingActionDock';
import useNotificationPushSync from '../features/notificaciones/hooks/useNotificationPushSync';
import AppBackground from '../features/ui/AppBackground';
import { colors } from '../constants/colors';
import { isCocinero } from '@/features/auth/roleUtils';

type DockAction = React.ComponentProps<typeof FloatingActionDock>['actions'][number];

function AppShell() {
  const pathname = usePathname();
  const router = useRouter();
  const { token, logout, user } = useAuth();
  useNotificationPushSync(token);
  const [dockOpen, setDockOpen] = useState(false);
  const usuarioEsCocinero = isCocinero(user);

  const showDock = Boolean(token) && pathname !== '/login';

  React.useEffect(() => {
    if (!token || !usuarioEsCocinero) {
      return;
    }

    const allowed =
      pathname === '/login' ||
      pathname === '/pedidos' ||
      pathname === '/' ||
      pathname.startsWith('/detalle');

    if (!allowed) {
      router.replace('/pedidos');
    }
  }, [pathname, router, token, usuarioEsCocinero]);

  const actions = useMemo(() => {
    const result: DockAction[] = [
      {
        key: 'pedidos',
        label: 'Pedidos',
        icon: 'grid-outline' as const,
        color: colors.dockNew,
        onPress: () => {
          setDockOpen(false);
          if (pathname === '/pedidos') {
            router.replace('/pedidos');
            return;
          }
          router.push('/pedidos');
        },
      },
    ];

    if (!usuarioEsCocinero) {
      result.push(
        {
          key: 'ajustes',
          label: 'Ajustes',
          icon: 'settings-outline' as const,
          color: colors.buttonTealBg,
          onPress: () => {
            setDockOpen(false);
            if (pathname === '/ajustes') {
              router.replace('/ajustes' as any);
              return;
            }
            router.push('/ajustes' as any);
          },
        },
        {
          key: 'notificaciones',
          label: 'Alertas',
          icon: 'notifications-outline' as const,
          color: colors.buttonWarningBg,
          onPress: () => {
            setDockOpen(false);
            if (pathname === '/notificaciones') {
              router.replace('/notificaciones' as any);
              return;
            }
            router.push('/notificaciones' as any);
          },
        }
      );
    }

    result.push({
      key: 'volver',
      label: 'Volver',
      icon: 'arrow-back-outline' as const,
      color: colors.dockRefresh,
      onPress: () => {
        setDockOpen(false);
        if (pathname === '/pedidos') {
          router.replace('/pedidos');
          return;
        }
        router.back();
      },
    });

    result.push({
      key: 'salir',
      label: 'Salir',
      icon: 'log-out-outline' as const,
      color: colors.dockExit,
      onPress: async () => {
        setDockOpen(false);
        await logout();
        router.replace('/login');
      },
    });

    return result;
  }, [logout, pathname, router, usuarioEsCocinero]);

  return (
    <View style={styles.container}>
      <AppBackground />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: styles.stackContent,
          animation: 'fade',
        }}
      />
      {showDock ? (
        <FloatingActionDock
          open={dockOpen}
          onToggle={() => setDockOpen(prev => !prev)}
          actions={actions}
        />
      ) : null}
    </View>
  );
}

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <AuthProvider>
      <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
        <AppShell />
        <StatusBar style="auto" />
      </ThemeProvider>
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  stackContent: {
    backgroundColor: 'transparent',
  },
});
