import * as ExpoSpeechRecognition from 'expo-speech-recognition';

type StartListeningOptions = {
  lang?: string;
  timeoutMs?: number;
};

type LiveListeningSession = {
  stop: () => Promise<string>;
  cancel: () => Promise<void>;
};

const mapErrorMessage = (error: any) => {
  const code = error?.error || error?.code;

  if (code === 'not-allowed') {
    return 'No se concedieron permisos de microfono/voz.';
  }
  if (code === 'no-speech') {
    return 'No detectamos voz. Intenta hablar mas cerca del microfono.';
  }
  if (code === 'service-not-allowed') {
    return 'El servicio de reconocimiento de voz no esta disponible en este dispositivo.';
  }
  if (error?.message) {
    return error.message;
  }
  return 'No fue posible iniciar el reconocimiento de voz.';
};

const getModule = () => {
  const moduleRef = (ExpoSpeechRecognition as any)?.ExpoSpeechRecognitionModule;
  return moduleRef ?? null;
};

const isAvailable = () => {
  const moduleRef = getModule();
  if (!moduleRef) {
    return false;
  }
  try {
    return Boolean(moduleRef.isRecognitionAvailable?.());
  } catch {
    return false;
  }
};

export const speechService = {
  isAvailable,

  async startLiveListening(options: StartListeningOptions = {}): Promise<LiveListeningSession> {
    const lang = options.lang || 'es-CO';

    const moduleRef = getModule();

    if (!moduleRef || !isAvailable()) {
      throw new Error(
        'Reconocimiento de voz no disponible en esta build. Usa Development Build o ingresa el texto manualmente.'
      );
    }

    const permissions = await moduleRef.requestPermissionsAsync();
    if (!permissions.granted) {
      throw new Error('Permisos de microfono/voz denegados por el usuario.');
    }

    let latestTranscript = '';
    let settled = false;

    let resultSub: any;
    let errorSub: any;
    let endSub: any;

    const completion = new Promise<string>((resolve, reject) => {
      const cleanup = () => {
        resultSub?.remove?.();
        errorSub?.remove?.();
        endSub?.remove?.();
      };

      const finishResolve = (value: string) => {
        if (settled) return;
        settled = true;
        cleanup();
        resolve(value.trim());
      };

      const finishReject = (message: string) => {
        if (settled) return;
        settled = true;
        cleanup();
        reject(new Error(message));
      };

      resultSub = moduleRef.addListener('result', (event: any) => {
        const transcript = event?.results?.[0]?.transcript || '';
        if (!transcript) return;
        latestTranscript = transcript;
      });

      errorSub = moduleRef.addListener('error', (event: any) => {
        finishReject(mapErrorMessage(event));
      });

      endSub = moduleRef.addListener('end', () => {
        if (latestTranscript.trim()) {
          finishResolve(latestTranscript);
          return;
        }
        finishReject('No detectamos una frase valida. Puedes intentar de nuevo o escribir el pedido.');
      });

      try {
        moduleRef.start({
          lang,
          interimResults: true,
          continuous: true,
          maxAlternatives: 1,
          addsPunctuation: true,
        });
      } catch (error: any) {
        finishReject(mapErrorMessage(error));
      }
    });

    return {
      stop: async () => {
        try {
          moduleRef.stop();
        } catch {
          // Silencioso.
        }
        return completion;
      },
      cancel: async () => {
        try {
          moduleRef.abort();
        } catch {
          // Silencioso.
        }
      },
    };
  },

  async startListening(options: StartListeningOptions = {}) {
    const timeoutMs = options.timeoutMs ?? 10000;
    const liveSession = await speechService.startLiveListening(options);
    return new Promise<string>((resolve, reject) => {
      setTimeout(async () => {
        try {
          const transcript = await liveSession.stop();
          resolve(transcript);
        } catch (error) {
          reject(error);
        }
      }, timeoutMs);
    });
  },
};

export default speechService;
