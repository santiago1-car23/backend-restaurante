export type VoiceOrderItem =
  | {
      kind: 'producto';
      quantity: number;
      label: string;
      productoId: number;
      productName: string;
      rawText: string;
      note?: string;
    }
  | {
      kind: 'corriente';
      quantity: number;
      label: string;
      rawText: string;
      proteina?: string;
      sopa?: string;
      principio?: string;
      acompanante?: string;
      note?: string;
    }
  | {
      kind: 'desayuno';
      quantity: number;
      label: string;
      rawText: string;
      principal?: string;
      bebida?: string;
      acompanante?: string;
      note?: string;
    };

export type VoiceOrderParseResult = {
  transcript: string;
  items: VoiceOrderItem[];
  unmatched: string[];
};
