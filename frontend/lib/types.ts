export type LanguageCode = "zh" | "en" | "ja" | "ko" | "fr" | "de" | "es";

export interface UploadResponse {
  id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  duration_seconds: number;
  sample_rate: number;
  channels: number;
  denoised: boolean;
  vad_segments: Array<{ start: number; end: number }>;
  speaker_features: Record<string, number>;
  detected_language: string | null;
  prompt_text: string | null;
  normalized_media_url: string;
  created_at: string;
  updated_at: string;
}

export interface Speaker {
  id: string;
  name: string;
  favorite: boolean;
  upload_id: string | null;
  engine: string;
  voice_signature: Record<string, string | number>;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Generation {
  id: string;
  speaker: Speaker;
  text: string;
  language: LanguageCode;
  voice_similarity: number;
  emotion: number;
  emotion_label: "Happy" | "Sad" | "Excited" | "Calm" | "Serious";
  speed: number;
  pitch: number;
  stability: number;
  output_format: "wav";
  engine: string;
  status: string;
  audio_url: string;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
