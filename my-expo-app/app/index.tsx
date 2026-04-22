import { Redirect } from 'expo-router';
import { Text, View } from 'react-native';

import { useAuth } from '../context/AuthContext';

export default function Index() {
  const { token, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <Text>Cargando...</Text>
      </View>
    );
  }

  return <Redirect href={token ? '/pedidos' : '/login'} />;
}
