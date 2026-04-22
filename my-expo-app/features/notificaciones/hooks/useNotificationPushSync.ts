import React from 'react';

export default function useNotificationPushSync(_token: string | null) {
  React.useEffect(() => {
    // Web: no-op. Las notificaciones de sistema se gestionan en nativo.
  }, []);
}
