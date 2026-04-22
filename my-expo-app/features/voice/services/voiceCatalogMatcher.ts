import type { CatalogoPedido, Producto } from '../../pedidos/services/pedidosService';
import type { VoiceOrderItem, VoiceOrderParseResult } from '../types';

type FieldConfig = {
  options?: string[];
  keywords: string[];
  fallback?: string;
};

// 🔢 NÚMEROS
const numberWords: Record<string, number> = {
  un: 1, una: 1, uno: 1,
  dos: 2, tres: 3, cuatro: 4,
  cinco: 5, seis: 6, siete: 7,
  ocho: 8, nueve: 9, diez: 10,
};

// 🧠 PALABRAS CLAVE
const stopWords = new Set(['de', 'del', 'la', 'el', 'los', 'las', 'para']);
const negativeKeywords = ['sin', 'no', 'quita'];
const extraKeywords = ['con', 'extra', 'agrega'];
const modifiersList = ['poco', 'poquito', 'mucho', 'para llevar'];
const orderIntentWords = new Set([
  'dame', 'deme', 'demen', 'quiero', 'quisiera', 'regalame', 'regaleme',
  'me', 'das', 'porfa', 'porfavor', 'favor', 'un', 'una', 'unos', 'unas',
]);

// 🧼 NORMALIZAR
const normalizeText = (value: string) =>
  value.toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\w\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const tokenize = (value: string) =>
  normalizeText(value)
    .split(' ')
    .filter(token => token && !stopWords.has(token));

const canonicalToken = (token: string) => {
  if (token.length <= 3) {
    return token;
  }

  if (token.endsWith('es') && token.length > 4) {
    return token.slice(0, -2);
  }

  if (token.endsWith('s') && token.length > 4) {
    return token.slice(0, -1);
  }

  return token;
};

const canonicalizeTokens = (tokens: string[]) => tokens.map(canonicalToken);

const cleanupOrderIntent = (value: string) =>
  tokenize(value)
    .filter(token => !orderIntentWords.has(token))
    .join(' ')
    .trim();

// 🔢 CANTIDAD
const extractQuantity = (segment: string) => {
  const tokens = normalizeText(segment).split(' ').filter(Boolean);
  for (const token of tokens) {
    if (!isNaN(Number(token))) {
      return Number(token);
    }
    if (numberWords[token]) {
      return numberWords[token];
    }
  }
  return 1;
};

// ❌ NEGACIONES
const hasNegation = (segment: string, word: string) =>
  new RegExp(`(sin|no|quita)\\s+${word}`).test(normalizeText(segment));

// ➕ EXTRAS
const hasExtra = (segment: string, word: string) =>
  new RegExp(`(con|extra|agrega)\\s+${word}`).test(normalizeText(segment));

// 🧠 MODIFICADORES
const extractModifiers = (segment: string) => {
  const normalized = normalizeText(segment);
  return modifiersList.filter(m => normalized.includes(m));
};

// 🔥 SIMILITUD SIMPLE
const similarity = (a: string, b: string) => {
  let matches = 0;
  const len = Math.min(a.length, b.length);
  for (let i = 0; i < len; i++) {
    if (a[i] === b[i]) matches++;
  }
  return matches / Math.max(a.length, b.length);
};

// 🔍 MATCH OPCIONES
const findOptionAdvanced = (segment: string, options: string[] = []) => {
  const normalized = normalizeText(segment);
  const segmentTokens = tokenize(segment);

  let best = '';
  let bestScore = 0;

  for (const opt of options || []) {
    const optNorm = normalizeText(opt);
    const optionTokens = tokenize(opt);

    let score = 0;
    if (normalized.includes(optNorm)) score += 2;
    if (similarity(normalized, optNorm) > 0.6) score += 1;
    if (optionTokens.length && optionTokens.every(token => segmentTokens.includes(token))) {
      score += 2;
    } else if (optionTokens.some(token => segmentTokens.includes(token))) {
      score += 1;
    }

    if (score > bestScore) {
      bestScore = score;
      best = opt;
    }
  }

  return best;
};

const isOptionNegated = (segment: string, option: string) => {
  const normalizedSegment = normalizeText(segment);
  const optionTokens = tokenize(option);

  if (!optionTokens.length) {
    return false;
  }

  const optionPattern = optionTokens.map(token => escapeRegex(token)).join('\\s+');
  return new RegExp(`\\b(?:sin|no|quita)\\s+${optionPattern}\\b`).test(normalizedSegment);
};

const findOptionWithoutNegation = (segment: string, options: string[] = []) => {
  const filteredOptions = (options || []).filter(option => !isOptionNegated(segment, option));
  return findOptionAdvanced(segment, filteredOptions);
};

const resolveFieldValue = (segment: string, config: FieldConfig) => {
  const options = config.options || [];
  if (!options.length) {
    return '';
  }

  const normalizedSegment = normalizeText(segment);
  const explicitKeyword = config.keywords.some(keyword => normalizedSegment.includes(keyword));

  for (const keyword of config.keywords) {
    const keywordIndex = normalizedSegment.indexOf(keyword);
    if (keywordIndex === -1) {
      continue;
    }

    const matched = findOptionWithoutNegation(
      normalizedSegment.slice(keywordIndex + keyword.length).trim(),
      options
    );
    if (matched) {
      return matched;
    }
  }

  const fallbackMatch = findOptionWithoutNegation(segment, options);
  if (fallbackMatch) {
    return fallbackMatch;
  }

  if (explicitKeyword) {
    return config.fallback || '';
  }

  return '';
};

const resolveFieldFromCatalog = (
  segment: string,
  options: string[] = [],
  keywords: string[] = [],
  fallback = ''
) => {
  if (!options.length) {
    return '';
  }

  const directMatch = findOptionWithoutNegation(segment, options);
  if (directMatch) {
    return directMatch;
  }

  return resolveFieldValue(segment, {
    options,
    keywords,
    fallback,
  });
};

const removeMatchedOption = (value: string, option?: string) => {
  if (!option) {
    return value;
  }

  const normalized = normalizeText(value);
  const optionPattern = tokenize(option).map(token => escapeRegex(token)).join('\\s+');
  return normalized.replace(new RegExp(`\\b${optionPattern}\\b`, 'g'), ' ').replace(/\s+/g, ' ').trim();
};

const escapeRegex = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const isBreakfastContinuation = (segment: string, catalogo: CatalogoPedido) => {
  const normalized = normalizeText(segment);
  if (!normalized) {
    return false;
  }

  if (normalized.includes('bebida') || normalized.includes('principal') || normalized.includes('acompanante')) {
    return true;
  }

  return Boolean(
    findOptionAdvanced(segment, catalogo.menu_desayuno?.principales) ||
      findOptionAdvanced(segment, catalogo.menu_desayuno?.bebidas)
  );
};

const isCorrienteContinuation = (segment: string, catalogo: CatalogoPedido) => {
  const normalized = normalizeText(segment);
  if (!normalized) {
    return false;
  }

  if (
    normalized.includes('sopa') ||
    normalized.includes('principio') ||
    normalized.includes('proteina') ||
    normalized.includes('acompanante')
  ) {
    return true;
  }

  return Boolean(
    findOptionAdvanced(segment, catalogo.menu_corriente?.proteina) ||
      findOptionAdvanced(segment, catalogo.menu_corriente?.principio) ||
      findOptionAdvanced(segment, catalogo.menu_corriente?.sopas)
  );
};

// 🔄 REEMPLAZOS
const extractReplacement = (segment: string) => {
  const match = normalizeText(segment).match(/cambia(?:me)?\s+(.*?)\s+por\s+(.*)/);
  return match ? { from: match[1], to: match[2] } : null;
};

// 🍽️ CORRIENTE
const buildCorrienteItem = (segment: string, catalogo: CatalogoPedido, quantity: number): VoiceOrderItem => {
  const menu = catalogo.menu_corriente;

  let proteina = resolveFieldFromCatalog(
    segment,
    menu?.proteina,
    ['proteina', 'carne', 'pollo', 'cerdo', 'res', 'pescado']
  );
  let sopa = resolveFieldFromCatalog(
    segment,
    menu?.sopas,
    ['sopa', 'caldo', 'consome'],
    menu?.sopa || ''
  );
  let principio = resolveFieldFromCatalog(
    segment,
    menu?.principio,
    ['principio']
  );

  if (hasNegation(segment, 'sopa')) sopa = '';
  if (hasNegation(segment, 'principio')) principio = '';

  const replacement = extractReplacement(segment);
  if (replacement && replacement.from.includes('sopa')) {
    sopa = replacement.to;
  }

  const extras = [];
  if (hasExtra(segment, 'aguacate')) extras.push('aguacate');
  if (hasExtra(segment, 'huevo')) extras.push('huevo');

  const modifiers = extractModifiers(segment);

  const note = [...modifiers, ...extras,
    sopa === '' ? 'sin sopa' : '',
    principio === '' ? 'sin principio' : ''
  ].filter(Boolean).join(', ') || undefined;

  return {
    kind: 'corriente',
    quantity,
    label: `${quantity} Corriente${proteina ? ` con ${proteina}` : ''}${sopa ? ` · sopa ${sopa}` : ''}`,
    rawText: segment,
    proteina: proteina || undefined,
    sopa: sopa || undefined,
    principio: principio || undefined,
    acompanante: menu?.acompanante || undefined,
    note,
  };
};


// 🍳 DESAYUNO MEJORADO PRO
const buildDesayunoItem = (
  segment: string,
  catalogo: CatalogoPedido,
  quantity: number
): VoiceOrderItem => {

  const menu = catalogo.menu_desayuno;
  const normalized = normalizeText(segment);

  // 🧼 limpiar palabra desayuno
  const cleanedSegment = normalized
    .replace(/\bdesayuno\b/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  // 🔍 PRINCIPAL (más inteligente)
  let principal =
    resolveFieldFromCatalog(segment, menu?.principales, ['principal', 'desayuno']) ||
    resolveFieldFromCatalog(cleanedSegment, menu?.principales, ['principal']);

  // 🔍 BEBIDA
  let bebida =
    resolveFieldFromCatalog(segment, menu?.bebidas, ['bebida']) ||
    resolveFieldFromCatalog(cleanedSegment, menu?.bebidas, ['bebida']);

  // ❌ NEGACIONES (más completo)
  if (hasNegation(segment, 'azucar') && bebida) {
    bebida = `${bebida} sin azucar`;
  }

  if (hasNegation(segment, 'sal') && principal) {
    principal = `${principal} sin sal`;
  }

  // 🔄 REEMPLAZOS (nuevo 🔥)
  const replacement = extractReplacement(segment);
  if (replacement) {
    if (replacement.from.includes('bebida')) {
      bebida = replacement.to;
    }
    if (replacement.from.includes('principal')) {
      principal = replacement.to;
    }
  }

  // ➕ EXTRAS (más flexible)
  const extras: string[] = [];
  ['queso', 'pan', 'huevo', 'aguacate'].forEach(extra => {
    if (hasExtra(segment, extra)) extras.push(extra);
  });

  // 🧠 MODIFICADORES
  const modifiers = extractModifiers(segment);

  // 🔁 fallback inteligente (cuando no detecta)
  let residual = cleanedSegment;

  if (principal) {
    residual = removeMatchedOption(residual, principal);
  } else {
    principal = findOptionWithoutNegation(residual, menu?.principales);
    if (principal) {
      residual = removeMatchedOption(residual, principal);
    }
  }

  if (!bebida) {
    bebida = findOptionWithoutNegation(residual, menu?.bebidas);
  }

  // 🧠 evitar duplicados tipo "café café"
  if (principal && bebida && principal === bebida) {
    bebida = '';
  }

  // 🧾 NOTAS MÁS LIMPIAS
  const noteParts = [
    ...modifiers,
    ...extras
  ].filter(Boolean);

  const note = noteParts.length ? noteParts.join(', ') : undefined;

  // 🧾 LABEL BONITO
  const labelParts = [`${quantity} Desayuno`];

  if (principal) labelParts.push(principal);
  if (bebida) labelParts.push(`+ ${bebida}`);

  return {
    kind: 'desayuno',
    quantity,
    label: labelParts.join(' '),
    rawText: segment,
    principal: principal || undefined,
    bebida: bebida || undefined,
    acompanante: menu?.acompanante || undefined,
    note,
  };
};




// 🍔 PRODUCTO
const findBestProductMatch = (segment: string, products: Producto[]): Producto | null => {
  const cleanedSegment = cleanupOrderIntent(segment);
  const segmentTokens = canonicalizeTokens(tokenize(cleanedSegment));

  let best: Producto | null = null;
  let bestScore = 0;

  for (const p of products) {
    const productName = normalizeText(p.nombre);
    const productTokens = canonicalizeTokens(tokenize(productName));
    const overlap = productTokens.filter(token => segmentTokens.includes(token)).length;
    const overlapRatio = productTokens.length ? overlap / productTokens.length : 0;

    let score = similarity(cleanedSegment || normalizeText(segment), productName);

    if (cleanedSegment.includes(productName)) {
      score += 1;
    }
    if (productName.includes(cleanedSegment) && cleanedSegment.length > 2) {
      score += 0.6;
    }
    score += overlapRatio;

    if (score > bestScore) {
      bestScore = score;
      best = p;
    }
  }

  return bestScore > 0.55 ? best : null;
};

// 🚀 PARSER PRINCIPAL
export const parseVoiceOrder = (
  transcript: string,
  catalogo: CatalogoPedido | null
): VoiceOrderParseResult => {

  if (!catalogo || !transcript.trim()) {
    return { transcript, items: [], unmatched: [] };
  }

  const segments = transcript
    .split(/,|\sy\s/gi)
    .map(s => s.trim())
    .filter(Boolean);

  const items: VoiceOrderItem[] = [];
  const unmatched: string[] = [];

  let lastItem: VoiceOrderItem | null = null;

  for (const segment of segments) {

    const quantity = extractQuantity(segment);
    const normalized = normalizeText(segment);

    // 🔁 contexto
    if (normalized.includes('otro') && lastItem) {
      items.push({ ...lastItem, quantity });
      continue;
    }

    // 🍽️ corriente
    if (normalized.includes('corriente') || normalized.includes('almuerzo')) {
      const item = buildCorrienteItem(segment, catalogo, quantity);
      items.push(item);
      lastItem = item;
      continue;
    }

    // 🍳 desayuno
    if (normalized.includes('desayuno')) {
      const item = buildDesayunoItem(segment, catalogo, quantity);
      items.push(item);
      lastItem = item;
      continue;
    }

    if (lastItem?.kind === 'desayuno' && isBreakfastContinuation(segment, catalogo)) {
      const item = buildDesayunoItem(`${lastItem.rawText} ${segment}`, catalogo, lastItem.quantity);
      items[items.length - 1] = item;
      lastItem = item;
      continue;
    }

    if (lastItem?.kind === 'corriente' && isCorrienteContinuation(segment, catalogo)) {
      const item = buildCorrienteItem(`${lastItem.rawText} ${segment}`, catalogo, lastItem.quantity);
      items[items.length - 1] = item;
      lastItem = item;
      continue;
    }

    // 🍔 producto normal
    const product = findBestProductMatch(segment, catalogo.productos);

    if (product) {
      const modifiers = extractModifiers(segment);

      const item: VoiceOrderItem = {
        kind: 'producto',
        quantity,
        label: `${quantity} ${product.nombre}`,
        productoId: product.id,
        productName: product.nombre,
        rawText: segment,
        note: modifiers.join(', ') || undefined,
      };

      items.push(item);
      lastItem = item;
      continue;
    }

    unmatched.push(segment);
    lastItem = null;
  }

  return { transcript, items, unmatched };
};
