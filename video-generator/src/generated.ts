export type GeneratedScene = {
  eyebrow: string;
  headline: string;
  subhead: string;
  narration: string;
  visual: string;
  values: Record<string, string | number | null>;
  frames: number;
  audio: string;
};

export const generatedScenes: GeneratedScene[] = [];
export const totalFrames = 1;
