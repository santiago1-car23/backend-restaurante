import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const memoryStore = new Map<string, string>();

const isWeb = Platform.OS === 'web';

const getLocalStorage = () => {
  if (typeof window === 'undefined') {
    return null;
  }
  try {
    return window.localStorage;
  } catch {
    return null;
  }
};

const appStorage = {
  async getItem(key: string): Promise<string | null> {
    if (isWeb) {
      const ls = getLocalStorage();
      if (ls) {
        return ls.getItem(key);
      }
      return memoryStore.get(key) ?? null;
    }
    return SecureStore.getItemAsync(key);
  },

  async setItem(key: string, value: string): Promise<void> {
    if (isWeb) {
      const ls = getLocalStorage();
      if (ls) {
        ls.setItem(key, value);
        return;
      }
      memoryStore.set(key, value);
      return;
    }
    await SecureStore.setItemAsync(key, value);
  },

  async removeItem(key: string): Promise<void> {
    if (isWeb) {
      const ls = getLocalStorage();
      if (ls) {
        ls.removeItem(key);
        return;
      }
      memoryStore.delete(key);
      return;
    }
    await SecureStore.deleteItemAsync(key);
  },
};

export default appStorage;
