// constants/colors.ts
export const colors = {
  // ========================
  // Colores principales
  // ========================
  primary: '#0093af',          // Color principal
  primaryDark: '#007f96',      // Variación oscura
  accent: '#f59e0b',           // Color de acento

    // ========================
    // Rojo principal (de la web)
    // ========================
    red: '#f31000',             // Rojo principal
    redDark: '#b71c1c',         // Rojo oscuro

  // ========================
  // Fondos y superficies
  // ========================
  bgBody: '#f7f9fc',
  bgSidebar: '#ffffff',
  bgBodyDark: '#111827',
  bgSidebarDark: '#1f2937',
  lightBg: '#f8f9fa',
  panelBg: 'transparent',
  surfaceSoft: '#f8fafc',
  appBgStart: '#f4fbff',
  appBgMid: '#e5f4f9',
  appBgEnd: '#eef2ff',
  appBgOrbPrimary: 'rgba(0,147,175,0.28)',
  appBgOrbAccent: 'rgba(245,158,11,0.16)',
  appBgGrid: 'rgba(15,23,42,0.06)',
  appBgStripe: 'rgba(255,255,255,0.30)',
  surfaceCard: '#ffffff',
  surfaceCardGlass: 'rgba(255,255,255,0.72)',
  surfaceCardGlassStrong: 'rgba(255,255,255,0.80)',
  surfaceCardBorder: 'rgba(255,255,255,0.60)',
  surfaceCardBorderSoft: 'rgba(255,255,255,0.55)',
  overlayDark: 'rgba(15,23,42,0.55)',
  overlayDarkSoft: 'rgba(6,10,18,0.38)',
  overlayDarkStrong: 'rgba(18,22,30,0.72)',
  overlayDarkCard: 'rgba(15,23,42,0.92)',
  overlayDarkBorder: 'rgba(255,255,255,0.13)',
  overlayLightBorder: 'rgba(255,255,255,0.18)',
  overlayLightSoft: 'rgba(255,255,255,0.08)',
  overlayLightInput: 'rgba(255,255,255,0.07)',
  overlayPanel: 'rgba(255,255,255,0.72)',
  overlayPanelBorder: 'rgba(255,255,255,0.52)',
  overlayBackdrop: 'rgba(2,6,23,0.22)',

  // ========================
  // Texto
  // ========================
  textMain: '#1f2937',
  textMuted: '#6b7280',
  textMainDark: '#f9fafb',
  textMutedDark: '#9ca3af',
  textSlate: '#0f172a',
  textSlateSoft: '#334155',
  textIce: '#dbeafe',
  textCloud: '#cbd5e1',

  // ========================
  // Bordes y sombras
  // ========================
  border: '#e5e7eb',
  borderDark: '#374151',
  shadowBase: 'rgba(0,0,0,0.05)',
  shadowCard: 'rgba(0,0,0,0.08)',
  shadowBaseDark: 'rgba(0,0,0,0.3)',
  shadowCardDark: 'rgba(0,0,0,0.4)',
  shadow: 'rgba(0,0,0,0.1)',
  shadowCyan: '#38bdf8',
  shadowPrimary: '#0093af',
  shadowSlate: '#0f172a',
  shadowDock: '#22d3ee',

  // ========================
  // Estados / Badges
  // ========================
  success: '#0cbe56',
  warning: '#edcd02',
  dark: '#2d3436',
  statusPendienteBg: '#fff9db',
  statusPendienteText: '#856404',
  statusPendienteBorder: '#ffe066',
  statusListoBg: '#ebfbee',
  statusListoText: '#0a8e25',
  statusListoBorder: '#b2f2bb',
  statusEntregadoBg: '#e7f5ff',
  statusEntregadoText: '#0093af',
  statusEntregadoBorder: '#a5d8ff',
  statusPagadoBg: '#f3f0ff',
  statusPagadoText: '#5f3dc4',
  statusPagadoBorder: '#d0bfff',
  successBg: '#dcfce7',
  successText: '#07933d',
  warningBgSoft: '#fef3c7',
  warningTextDark: '#92400e',
  infoBg: '#e0f4f8',
  paidIcon: '#5f3dc4',
  dangerText: '#b91c1c',

  // ========================
  // Botones y elementos interactivos
  // ========================
  btnPrimaryBg: '#0093af',
  btnPrimaryHover: '#007f96',
  btnPrimaryText: '#ffffff',
  inputFocusBorder: '#0093af',
  inputFocusShadow: 'rgba(0,147,175,0.2)',
  textPrimary: '#0093af',
  buttonDarkBg: '#111827',
  buttonDarkText: '#f8fafc',
  buttonSuccessBg: '#16a34a',
  buttonTealBg: '#0f766e',
  buttonWarningBg: '#d97706',
  dockNew: '#06b6d4',
  dockRefresh: '#2563eb',
  dockExit: '#f71000',
  dockGlow: 'rgba(34,211,238,0.18)',
  dockSpec: 'rgba(224,242,254,0.22)',
  dockBorder: 'rgba(103,232,249,0.32)',
  dockLabelBorder: 'rgba(125,211,252,0.18)',

  // ========================
  // Otros
  // ========================
  sidebarWidth: 260,
  headerHeightMobile: 60,
} as const;

export type ColorTheme = typeof colors;
