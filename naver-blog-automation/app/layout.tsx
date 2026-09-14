import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "네이버 블로그 자동화",
  description: "AI가 글을 쓰고 자동으로 발행해주는 네이버 블로그 관리 도구",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
