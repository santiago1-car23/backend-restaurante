import appStorage from '@/services/appStorage';

const KEY_ENABLED = 'notifications_enabled';
const KEY_LAST_NOTIFIED = 'notifications_last_notified_id';

const toBool = (value: string | null) => value !== '0';

const notificacionesSettingsService = {
  async getEnabled(): Promise<boolean> {
    const stored = await appStorage.getItem(KEY_ENABLED);
    return toBool(stored);
  },

  async setEnabled(enabled: boolean): Promise<void> {
    await appStorage.setItem(KEY_ENABLED, enabled ? '1' : '0');
  },

  async getLastNotifiedId(): Promise<number | null> {
    const stored = await appStorage.getItem(KEY_LAST_NOTIFIED);
    if (!stored) {
      return null;
    }
    const parsed = Number(stored);
    return Number.isFinite(parsed) ? parsed : null;
  },

  async setLastNotifiedId(id: number): Promise<void> {
    await appStorage.setItem(KEY_LAST_NOTIFIED, String(id));
  },
};

export default notificacionesSettingsService;
