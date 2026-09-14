import { Metadata } from "next";

export const metadata: Metadata = {
  title: "대시보드 - 네이버 블로그 자동화",
};

export default function HomePage() {
  return (
    <main style={{ padding: "2rem" }}>
      <h1>🚀 네이버 블로그 자동화</h1>
      <p>AI가 글을 쓰고 자동으로 발행해주는 도구입니다.</p>
      <p>개발 중...</p>
    </main>
  );
}
