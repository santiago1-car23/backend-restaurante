import React from 'react';

export default function useNotificationPushSync(_token: string | null) {
  React.useEffect(() => {
    // Native: no-op. Integracion de notificaciones push removida.
  }, []);
}
