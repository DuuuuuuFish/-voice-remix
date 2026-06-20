import type { Generation, Speaker, UploadResponse } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

async function handle<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(payload.detail || "Request failed");
  }
  return response.json() as Promise<T>;
}

export async function uploadReference(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return handle<UploadResponse>(
    await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    }),
  );
}

export async function createSpeaker(payload: {
  upload_id?: string;
  name: string;
  favorite?: boolean;
  base_speaker_id?: string;
  mix_with_speaker_id?: string;
  mix_ratio_primary?: number;
  notes?: string;
}) {
  return handle<Speaker>(
    await fetch(`${API_BASE}/clone`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function listSpeakers() {
  return handle<Speaker[]>(await fetch(`${API_BASE}/speakers`, { cache: "no-store" }));
}

export async function updateSpeaker(id: string, payload: Partial<Pick<Speaker, "name" | "favorite" | "notes">>) {
  return handle<Speaker>(
    await fetch(`${API_BASE}/speakers/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function deleteSpeaker(id: string) {
  return handle<{ message: string }>(
    await fetch(`${API_BASE}/speakers/${id}`, {
      method: "DELETE",
    }),
  );
}

export async function generateAudio(payload: {
  speaker_id: string;
  text: string;
  language: string;
  voice_similarity: number;
  emotion: number;
  emotion_label: string;
  speed: number;
  pitch: number;
  stability: number;
  output_format: string;
}) {
  return handle<Generation>(
    await fetch(`${API_BASE}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function listHistory() {
  return handle<Generation[]>(await fetch(`${API_BASE}/history`, { cache: "no-store" }));
}

export async function deleteHistory(id: string) {
  return handle<{ message: string }>(
    await fetch(`${API_BASE}/history/${id}`, {
      method: "DELETE",
    }),
  );
}

export async function regenerateHistory(id: string) {
  return handle<Generation>(
    await fetch(`${API_BASE}/history/${id}/regenerate`, {
      method: "POST",
    }),
  );
}

export async function downloadHistoryAudio(id: string, filename?: string) {
  const response = await fetch(`${API_BASE}/history/${id}/download`);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(payload.detail || "Request failed");
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename || `${id}.wav`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}

export function mediaUrl(url: string) {
  if (url.startsWith("http")) return url;
  return `${API_BASE.replace(/\/api$/, "")}${url}`;
}
