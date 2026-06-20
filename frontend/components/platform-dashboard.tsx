"use client";

import { useEffect, useMemo, useRef, useState, useTransition } from "react";

import {
  createSpeaker,
  downloadHistoryAudio,
  deleteHistory,
  deleteSpeaker,
  generateAudio,
  listHistory,
  listSpeakers,
  mediaUrl,
  regenerateHistory,
  updateSpeaker,
  uploadReference,
} from "@/lib/api";
import type { Generation, LanguageCode, Speaker, UploadResponse } from "@/lib/types";

const languageOptions: Array<{ value: LanguageCode; label: string }> = [
  { value: "zh", label: "中文" },
  { value: "en", label: "English" },
  { value: "ja", label: "日本語" },
  { value: "ko", label: "한국어" },
  { value: "fr", label: "Français" },
  { value: "de", label: "Deutsch" },
  { value: "es", label: "Español" },
];

const emotionOptions = [
  { value: "Happy", label: "开心" },
  { value: "Sad", label: "悲伤" },
  { value: "Excited", label: "激动" },
  { value: "Calm", label: "平静" },
  { value: "Serious", label: "严肃" },
] as const;

const starterPrompts: Record<LanguageCode, string> = {
  zh: "你好，很高兴认识你。欢迎体验跨语言声音克隆平台。",
  en: "Hello, it is a pleasure to meet you. Welcome to the cross-lingual voice clone platform.",
  ja: "こんにちは。お会いできてうれしいです。多言語音声クローンプラットフォームへようこそ。",
  ko: "안녕하세요. 만나서 반갑습니다. 다국어 음성 클론 플랫폼에 오신 것을 환영합니다.",
  fr: "Bonjour, ravi de vous rencontrer. Bienvenue sur la plateforme de clonage vocal multilingue.",
  de: "Hallo, schoen dich kennenzulernen. Willkommen auf der mehrsprachigen Voice-Cloning-Plattform.",
  es: "Hola, encantado de conocerte. Bienvenido a la plataforma multilingue de clonacion de voz.",
};

const style = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(180deg, #f3f6ff 0%, #eaf0ff 100%)",
    color: "#0f172a",
    padding: "24px 16px 40px",
    fontFamily: '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", system-ui, sans-serif',
  } satisfies React.CSSProperties,
  wrap: {
    maxWidth: "1440px",
    margin: "0 auto",
  } satisfies React.CSSProperties,
  hero: {
    display: "grid",
    gap: "16px",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    alignItems: "start",
  } satisfies React.CSSProperties,
  lower: {
    display: "grid",
    gap: "16px",
    gridTemplateColumns: "minmax(320px, 0.9fr) minmax(420px, 1.1fr)",
    marginTop: "16px",
  } satisfies React.CSSProperties,
  card: {
    background: "rgba(255,255,255,0.94)",
    border: "1px solid #dbe4ff",
    borderRadius: "24px",
    boxShadow: "0 18px 48px rgba(15, 23, 42, 0.08)",
    padding: "20px",
  } satisfies React.CSSProperties,
  darkCard: {
    background: "#0f172a",
    color: "#fff",
    border: "1px solid #1e293b",
    borderRadius: "24px",
    boxShadow: "0 18px 48px rgba(15, 23, 42, 0.18)",
    padding: "20px",
  } satisfies React.CSSProperties,
  badge: {
    display: "inline-flex",
    alignItems: "center",
    borderRadius: "999px",
    background: "#e8edff",
    color: "#3347d6",
    fontSize: "12px",
    fontWeight: 700,
    padding: "6px 12px",
    marginBottom: "12px",
  } satisfies React.CSSProperties,
  heading: {
    fontSize: "30px",
    lineHeight: 1.15,
    fontWeight: 800,
    marginBottom: "8px",
  } satisfies React.CSSProperties,
  sub: {
    color: "#475569",
    fontSize: "14px",
    lineHeight: 1.6,
  } satisfies React.CSSProperties,
  sectionTitle: {
    fontSize: "24px",
    lineHeight: 1.2,
    fontWeight: 800,
    marginBottom: "8px",
  } satisfies React.CSSProperties,
  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: 700,
    marginBottom: "8px",
    color: "#334155",
  } satisfies React.CSSProperties,
  input: {
    width: "100%",
    minHeight: "44px",
    borderRadius: "14px",
    border: "1px solid #cbd5e1",
    background: "#fff",
    padding: "10px 14px",
    fontSize: "14px",
    color: "#0f172a",
  } satisfies React.CSSProperties,
  textarea: {
    width: "100%",
    minHeight: "180px",
    borderRadius: "18px",
    border: "1px solid #cbd5e1",
    background: "#fff",
    padding: "14px",
    fontSize: "15px",
    lineHeight: 1.6,
    color: "#0f172a",
    resize: "vertical",
  } satisfies React.CSSProperties,
  button: {
    minHeight: "46px",
    borderRadius: "14px",
    border: "none",
    background: "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
    color: "#fff",
    fontWeight: 700,
    fontSize: "14px",
    padding: "0 18px",
    cursor: "pointer",
  } satisfies React.CSSProperties,
  buttonDisabled: {
    opacity: 0.55,
    cursor: "not-allowed",
  } satisfies React.CSSProperties,
  secondaryButton: {
    minHeight: "40px",
    borderRadius: "12px",
    border: "1px solid rgba(255,255,255,0.18)",
    background: "rgba(255,255,255,0.08)",
    color: "#fff",
    fontWeight: 700,
    fontSize: "14px",
    padding: "0 14px",
    cursor: "pointer",
  } satisfies React.CSSProperties,
  dropzone: {
    borderRadius: "18px",
    border: "1px dashed #818cf8",
    background: "rgba(238,242,255,0.88)",
    padding: "20px",
    minHeight: "160px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    gap: "8px",
  } satisfies React.CSSProperties,
  grid2: {
    display: "grid",
    gap: "12px",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  } satisfies React.CSSProperties,
  status: {
    borderRadius: "18px",
    background: "#020617",
    color: "#cbd5e1",
    padding: "16px 18px",
    marginTop: "12px",
  } satisfies React.CSSProperties,
  player: {
    borderRadius: "20px",
    background: "#020617",
    color: "#fff",
    padding: "18px",
  } satisfies React.CSSProperties,
  infoBox: {
    borderRadius: "16px",
    border: "1px solid #dbe4ff",
    background: "#fff",
    padding: "14px",
    marginTop: "14px",
  } satisfies React.CSSProperties,
  item: {
    borderRadius: "16px",
    border: "1px solid #e2e8f0",
    background: "#fff",
    padding: "14px",
  } satisfies React.CSSProperties,
  selectedItem: {
    borderRadius: "16px",
    border: "1px solid #818cf8",
    background: "#eef2ff",
    padding: "14px",
  } satisfies React.CSSProperties,
  row: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "12px",
  } satisfies React.CSSProperties,
  mini: {
    color: "#64748b",
    fontSize: "13px",
    lineHeight: 1.5,
  } satisfies React.CSSProperties,
};

export function PlatformDashboard() {
  const [upload, setUpload] = useState<UploadResponse | null>(null);
  const [speakerName, setSpeakerName] = useState("我的克隆音色");
  const [speakers, setSpeakers] = useState<Speaker[]>([]);
  const [selectedSpeakerId, setSelectedSpeakerId] = useState("");
  const [mixSpeakerId, setMixSpeakerId] = useState("");
  const [mixRatio, setMixRatio] = useState(70);
  const [text, setText] = useState(starterPrompts.zh);
  const [language, setLanguage] = useState<LanguageCode>("zh");
  const [voiceSimilarity, setVoiceSimilarity] = useState(80);
  const [emotion, setEmotion] = useState(50);
  const [emotionLabel, setEmotionLabel] = useState<(typeof emotionOptions)[number]["value"]>("Calm");
  const [speed, setSpeed] = useState(1);
  const [pitch, setPitch] = useState(0);
  const [stability, setStability] = useState(75);
  const [outputFormat] = useState<"wav">("wav");
  const [history, setHistory] = useState<Generation[]>([]);
  const [currentAudio, setCurrentAudio] = useState<Generation | null>(null);
  const [status, setStatus] = useState("系统就绪");
  const [isPending, startTransition] = useTransition();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const pendingPlayIdRef = useRef<string | null>(null);

  async function refreshAll() {
    const [speakerList, historyList] = await Promise.all([listSpeakers(), listHistory()]);
    setSpeakers(speakerList);
    setHistory(historyList);
    setSelectedSpeakerId((current) => current || speakerList[0]?.id || "");
    setCurrentAudio((current) => current || historyList[0] || null);
  }

  useEffect(() => {
    startTransition(() => {
      refreshAll().catch((error: Error) => setStatus(error.message));
    });
  }, []);

  useEffect(() => {
    setText(starterPrompts[language]);
  }, [language]);

  useEffect(() => {
    if (!currentAudio || !audioRef.current) return;
    const audio = audioRef.current;
    audio.pause();
    audio.load();

    if (pendingPlayIdRef.current !== currentAudio.id) return;

    const playCurrentAudio = () => {
      const playPromise = audio.play();
      if (playPromise && typeof playPromise.catch === "function") {
        playPromise.catch((error) => {
          console.error("audio play failed", error);
          setStatus("Audio loaded. If playback does not start automatically, use the player controls.");
        });
      }
      pendingPlayIdRef.current = null;
    };

    audio.addEventListener("canplay", playCurrentAudio, { once: true });
    return () => {
      audio.removeEventListener("canplay", playCurrentAudio);
    };
  }, [currentAudio?.id]);

  const selectedSpeaker = useMemo(
    () => speakers.find((item) => item.id === selectedSpeakerId) ?? null,
    [selectedSpeakerId, speakers],
  );

  async function handleUpload(file: File) {
    setStatus("正在上传参考音频...");
    const result = await uploadReference(file);
    setUpload(result);
    const [speakerList, historyList] = await Promise.all([listSpeakers(), listHistory()]);
    setSpeakers(speakerList);
    setHistory(historyList);
    setSelectedSpeakerId((current) => current || speakerList[0]?.id || "");
    setCurrentAudio((current) => current || historyList[0] || null);
    setStatus(`已上传 ${result.original_filename}，VAD 分段：${result.vad_segments.length} 段。`);
  }

  async function handleClone() {
    if (!upload && !selectedSpeakerId) {
      setStatus("请先上传参考音频或选择已有音色。");
      return;
    }

    setStatus("正在创建音色档案...");
    const payload = upload
      ? {
          upload_id: upload.id,
          name: speakerName,
          mix_with_speaker_id: mixSpeakerId || undefined,
          mix_ratio_primary: mixRatio,
        }
      : {
          base_speaker_id: selectedSpeakerId,
          name: speakerName,
          mix_with_speaker_id: mixSpeakerId || undefined,
          mix_ratio_primary: mixRatio,
        };
    const speaker = await createSpeaker(payload);
    const updated = await listSpeakers();
    setSpeakers(updated);
    setSelectedSpeakerId(speaker.id);
    setStatus(`音色“${speaker.name}”已创建完成。`);
  }

  async function handleGenerate() {
    if (!selectedSpeakerId) {
      setStatus("请先选择音色。");
      return;
    }

    setStatus("正在生成语音...");
    const result = await generateAudio({
      speaker_id: selectedSpeakerId,
      text,
      language,
      voice_similarity: voiceSimilarity,
      emotion,
      emotion_label: emotionLabel,
      speed,
      pitch,
      stability,
      output_format: outputFormat,
    });

    const updated = await listHistory();
    setHistory(updated);
    setCurrentAudio(result);
    setStatus(`生成完成，已更新播放器。文件：${result.id}.wav`);
  }

  async function handleFavorite(speaker: Speaker) {
    const result = await updateSpeaker(speaker.id, { favorite: !speaker.favorite });
    setSpeakers((current) => current.map((item) => (item.id === result.id ? result : item)));
  }

  async function handleDeleteSpeaker(id: string) {
    await deleteSpeaker(id);
    const updated = await listSpeakers();
    setSpeakers(updated);
    setSelectedSpeakerId((current) => (current === id ? updated[0]?.id || "" : current));
  }

  async function handleDeleteHistory(id: string) {
    await deleteHistory(id);
    const updated = await listHistory();
    setHistory(updated);
    setCurrentAudio((current) => (current?.id === id ? updated[0] || null : current));
  }

  async function handleRegenerate(id: string) {
    setStatus("正在重新生成...");
    const result = await regenerateHistory(id);
    const updated = await listHistory();
    setHistory(updated);
    setCurrentAudio(result);
    setStatus(`重新生成完成，已切换到新音频：${result.id}.wav`);
  }

  async function handlePlayHistory(item: Generation) {
    pendingPlayIdRef.current = item.id;
    setCurrentAudio(item);
    setStatus(`宸插垏鎹㈠埌鍘嗗彶闊抽锛?{item.id}.wav`);

    if (currentAudio?.id === item.id && audioRef.current) {
      try {
        await audioRef.current.play();
      } catch (error) {
        console.error("audio play failed", error);
        setStatus("Audio loaded. If playback does not start automatically, use the player controls.");
      } finally {
        pendingPlayIdRef.current = null;
      }
    }
  }

  return (
    <main style={style.page}>
      <div style={style.wrap}>
        <div style={{ marginBottom: "18px" }}>
          <div style={style.badge}>真实 CosyVoice2 多语言声音克隆</div>
          <h1 style={style.heading}>AI 声音克隆平台</h1>
          <p style={style.sub}>上传参考音频、创建音色档案，并生成真实的 wav 输出结果。</p>
        </div>

        <section style={style.hero}>
          <div style={style.card}>
            <div style={style.badge}>上传与克隆</div>
            <h2 style={style.sectionTitle}>参考音频</h2>
            <p style={style.sub}>支持 5 到 30 秒参考音频，自动完成归一化、VAD 和说话人特征提取。</p>

            <label style={{ ...style.dropzone, marginTop: "16px" }}>
              <div style={{ fontSize: "32px" }}>🎙</div>
              <div style={{ fontWeight: 700 }}>拖入或选择 `wav / mp3 / m4a`，最大 20MB</div>
              <div style={style.mini}>上传成功后会在下方显示文件信息和特征提取结果。</div>
              <input
                type="file"
                accept=".wav,.mp3,.m4a,audio/*"
                style={{ marginTop: "8px" }}
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (!file) return;
                  startTransition(() => {
                    handleUpload(file).catch((error: Error) => setStatus(error.message));
                  });
                }}
              />
            </label>

            <div style={{ ...style.darkCard, marginTop: "16px" }}>
              <div style={style.label}>音色名称</div>
              <input style={style.input} value={speakerName} onChange={(event) => setSpeakerName(event.target.value)} />

              <div style={{ ...style.grid2, marginTop: "14px" }}>
                <div>
                  <div style={style.label}>音色混合</div>
                  <select style={style.input} value={mixSpeakerId} onChange={(event) => setMixSpeakerId(event.target.value)}>
                    <option value="">不启用混合</option>
                    {speakers.map((speaker) => (
                      <option key={speaker.id} value={speaker.id}>
                        {speaker.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <div style={style.label}>主音色占比</div>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={mixRatio}
                    onChange={(event) => setMixRatio(Number(event.target.value))}
                    style={{ width: "100%" }}
                  />
                  <div style={{ marginTop: "6px", color: "#cbd5e1", fontSize: "13px" }}>{mixRatio}% / {100 - mixRatio}%</div>
                </div>
              </div>

              <button
                disabled={isPending}
                style={{ ...style.button, ...(isPending ? style.buttonDisabled : {}), width: "100%", marginTop: "16px" }}
                onClick={() => startTransition(() => handleClone().catch((error: Error) => setStatus(error.message)))}
              >
                {isPending ? "处理中..." : "创建音色档案"}
              </button>
            </div>

            {upload ? (
              <div style={style.infoBox}>
                <div style={style.row}>
                  <strong>{upload.original_filename}</strong>
                  <span style={style.mini}>{upload.duration_seconds.toFixed(1)} 秒</span>
                </div>
                <div style={{ ...style.mini, marginTop: "8px" }}>采样率：{upload.sample_rate} Hz，声道：{upload.channels}</div>
                <div style={{ ...style.mini, marginTop: "8px" }}>
                  基频：{upload.speaker_features.pitch_hz ?? "--"} Hz，亮度：{upload.speaker_features.brightness ?? "--"}
                </div>
                <div style={{ ...style.mini, marginTop: "8px" }}>
                  提示文本：{upload.prompt_text || "暂未获得自动转写结果。"}
                </div>
              </div>
            ) : null}
          </div>

          <div style={style.card}>
            <div style={style.badge}>跨语言生成</div>
            <h2 style={style.sectionTitle}>文本工作台</h2>
            <p style={style.sub}>使用真实 CosyVoice2 进行 Zero-shot 和跨语言生成，输出固定为 wav。</p>

            <div style={{ ...style.grid2, marginTop: "16px" }}>
              <div>
                <div style={style.label}>音色</div>
                <select style={style.input} value={selectedSpeakerId} onChange={(event) => setSelectedSpeakerId(event.target.value)}>
                  <option value="">请选择音色</option>
                  {speakers.map((speaker) => (
                    <option key={speaker.id} value={speaker.id}>
                      {speaker.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <div style={style.label}>目标语言</div>
                <select style={style.input} value={language} onChange={(event) => setLanguage(event.target.value as LanguageCode)}>
                  {languageOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ marginTop: "14px" }}>
              <div style={style.label}>输入文本</div>
              <div style={{ ...style.mini, marginBottom: "8px" }}>如果你想自己控制断句，请直接按回车换行。每一行都会被当作一个独立语音片段生成。</div>
              <textarea style={style.textarea} value={text} onChange={(event) => setText(event.target.value)} />
            </div>

            <div style={{ ...style.grid2, marginTop: "14px" }}>
              <div>
                <div style={style.label}>情绪预设</div>
                <select style={style.input} value={emotionLabel} onChange={(event) => setEmotionLabel(event.target.value as (typeof emotionOptions)[number]["value"])}>
                  {emotionOptions.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <div style={style.label}>输出格式</div>
                <div style={{ ...style.input, display: "flex", alignItems: "center" }}>wav</div>
              </div>
            </div>

            <button
              disabled={isPending}
              style={{ ...style.button, ...(isPending ? style.buttonDisabled : {}), width: "100%", marginTop: "16px" }}
              onClick={() => startTransition(() => handleGenerate().catch((error: Error) => setStatus(error.message)))}
            >
              {isPending ? "生成中..." : "生成语音"}
            </button>

            <div style={style.status}>
              <div style={{ color: "#fff", fontWeight: 700, marginBottom: "6px" }}>CosyVoice2 真实推理状态</div>
              <div>{status}</div>
            </div>
          </div>

          <div style={style.darkCard}>
            <div style={{ ...style.badge, background: "rgba(255,255,255,0.08)", color: "#fff" }}>参数控制</div>
            <h2 style={{ ...style.sectionTitle, color: "#fff" }}>语音调节</h2>
            <p style={{ color: "#cbd5e1", fontSize: "14px", lineHeight: 1.6 }}>
              当前保存并显示所有请求参数，其中真实映射到 CosyVoice2 的核心参数是语速。
            </p>

            <div style={{ marginTop: "16px" }}>
              <div style={style.label}>音色相似度 {voiceSimilarity}</div>
              <input type="range" min={0} max={100} value={voiceSimilarity} onChange={(event) => setVoiceSimilarity(Number(event.target.value))} style={{ width: "100%" }} />
            </div>
            <div style={{ marginTop: "12px" }}>
              <div style={style.label}>情绪强度 {emotion}</div>
              <input type="range" min={0} max={100} value={emotion} onChange={(event) => setEmotion(Number(event.target.value))} style={{ width: "100%" }} />
            </div>
            <div style={{ marginTop: "12px" }}>
              <div style={style.label}>语速 {speed.toFixed(1)}x</div>
              <input type="range" min={0.5} max={2} step={0.1} value={speed} onChange={(event) => setSpeed(Number(event.target.value))} style={{ width: "100%" }} />
            </div>
            <div style={{ marginTop: "12px" }}>
              <div style={style.label}>音高 {pitch}</div>
              <input type="range" min={-12} max={12} value={pitch} onChange={(event) => setPitch(Number(event.target.value))} style={{ width: "100%" }} />
            </div>
            <div style={{ marginTop: "12px" }}>
              <div style={style.label}>稳定度 {stability}</div>
              <input type="range" min={0} max={100} value={stability} onChange={(event) => setStability(Number(event.target.value))} style={{ width: "100%" }} />
            </div>

            {selectedSpeaker ? (
              <div style={{ marginTop: "16px", borderRadius: "16px", background: "rgba(255,255,255,0.08)", padding: "14px" }}>
                <div style={{ fontWeight: 700, marginBottom: "8px" }}>{selectedSpeaker.name}</div>
                <div style={{ color: "#cbd5e1", fontSize: "13px", lineHeight: 1.5 }}>音色族：{String(selectedSpeaker.voice_signature.voice_family ?? "custom")}</div>
                <div style={{ color: "#cbd5e1", fontSize: "13px", lineHeight: 1.5 }}>基频：{String(selectedSpeaker.voice_signature.pitch_hz ?? "--")}</div>
                <div style={{ color: "#cbd5e1", fontSize: "13px", lineHeight: 1.5 }}>建议语速：{String(selectedSpeaker.voice_signature.speed_hint ?? "--")}</div>
              </div>
            ) : null}
          </div>
        </section>

        <section style={style.lower}>
          <div style={style.card}>
            <div style={style.badge}>音色管理</div>
            <h2 style={style.sectionTitle}>已保存音色</h2>
            <p style={style.sub}>管理真实上传得到的音色，支持收藏、删除和复用。</p>

            <div style={{ display: "grid", gap: "12px", marginTop: "16px" }}>
              {speakers.map((speaker) => (
                <div key={speaker.id} style={selectedSpeakerId === speaker.id ? style.selectedItem : style.item}>
                  <div style={style.row}>
                    <button
                      style={{ background: "transparent", border: "none", textAlign: "left", padding: 0, flex: 1, color: "#0f172a" }}
                      onClick={() => setSelectedSpeakerId(speaker.id)}
                    >
                      <div style={{ fontWeight: 700 }}>{speaker.name}</div>
                      <div style={style.mini}>{speaker.engine}</div>
                    </button>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <button
                        style={{ ...style.button, minHeight: "36px", padding: "0 10px", background: speaker.favorite ? "#dc2626" : "#475569" }}
                        onClick={() => handleFavorite(speaker)}
                      >
                        收藏
                      </button>
                      <button
                        style={{ ...style.button, minHeight: "36px", padding: "0 10px", background: "#111827" }}
                        onClick={() => startTransition(() => handleDeleteSpeaker(speaker.id).catch((error: Error) => setStatus(error.message)))}
                      >
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={style.card}>
            <div style={style.badge}>试听与历史</div>
            <h2 style={style.sectionTitle}>播放器与生成记录</h2>
            <p style={style.sub}>试听、下载、删除和重新生成真实的 `wav` 输出结果。</p>

            <div style={{ ...style.player, marginTop: "16px" }}>
              {currentAudio ? (
                <>
                  <div style={style.row}>
                    <div>
                      <div style={{ color: "#94a3b8", fontSize: "13px" }}>{currentAudio.speaker.name}</div>
                      <div style={{ fontWeight: 700, marginTop: "4px" }}>
                        {languageOptions.find((item) => item.value === currentAudio.language)?.label}
                      </div>
                    </div>
                    <div style={{ color: "#cbd5e1", fontSize: "13px" }}>{currentAudio.output_format.toUpperCase()}</div>
                  </div>
                  <audio
                    key={currentAudio.id}
                    ref={audioRef}
                    controls
                    preload="metadata"
                    style={{ width: "100%", marginTop: "14px" }}
                    src={mediaUrl(currentAudio.audio_url)}
                  />
                  <div style={{ marginTop: "14px" }}>
                    <a
                      href={mediaUrl(currentAudio.audio_url)}
                      download
                      onClick={(event) => {
                        event.preventDefault();
                        downloadHistoryAudio(currentAudio.id, `${currentAudio.id}.wav`).catch((error: Error) => setStatus(error.message));
                      }}
                    >
                      <button style={style.secondaryButton}>下载音频</button>
                    </a>
                  </div>
                </>
              ) : (
                <div style={{ color: "#94a3b8" }}>先生成一条语音，这里会显示真实输出结果。</div>
              )}
            </div>

            <div style={{ display: "grid", gap: "12px", marginTop: "16px" }}>
              {history.map((item) => (
                <div key={item.id} style={style.item}>
                  <div style={style.row}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 700 }}>{item.speaker.name}</div>
                      <div style={style.mini}>
                        {languageOptions.find((option) => option.value === item.language)?.label} ·{" "}
                        {emotionOptions.find((emotionOption) => emotionOption.value === item.emotion_label)?.label ?? item.emotion_label} ·{" "}
                        {new Date(item.created_at).toLocaleString()}
                      </div>
                      <div style={{ ...style.mini, marginTop: "8px", color: "#334155" }}>{item.text}</div>
                    </div>
                    <div style={{ display: "flex", gap: "8px", alignItems: "start" }}>
                      <button
                        style={{ ...style.button, minHeight: "36px", padding: "0 10px" }}
                        onClick={() => {
                          handlePlayHistory(item).catch((error: Error) => setStatus(error.message));
                          setStatus(`已切换到历史音频：${item.id}.wav`);
                        }}
                      >
                        播放
                      </button>
                      <button
                        style={{ ...style.button, minHeight: "36px", padding: "0 10px", background: "#475569" }}
                        onClick={() => startTransition(() => handleRegenerate(item.id).catch((error: Error) => setStatus(error.message)))}
                      >
                        重生
                      </button>
                      <button
                        style={{ ...style.button, minHeight: "36px", padding: "0 10px", background: "#111827" }}
                        onClick={() => startTransition(() => handleDeleteHistory(item.id).catch((error: Error) => setStatus(error.message)))}
                      >
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
