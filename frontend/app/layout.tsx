import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI 声音克隆平台",
  description: "基于 Next.js 与 FastAPI 的真实 CosyVoice2 多语言零样本声音克隆平台。",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
