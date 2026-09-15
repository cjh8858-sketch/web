import path from "path";

export const CONFIG = {
  // 포트
  PORT: parseInt(process.env.PORT || "4123"),

  // 기본값 (설정 테이블에서 오버라이드 가능)
  DEFAULTS: {
    dryRun: true,                    // 연습 모드 기본값: ON
    killSwitch: false,                // 전체 중단: OFF
    visibility: "private",            // 공개 범위: 비공개 (절대 변경 금지)
    dailyPublishLimit: 3,             // 하루 발행 수
    minPublishIntervalMin: 30,        // 발행 간격 (분)
    scrapeTopN: 8,                    // 수집 상위 N개
    imageCandidates: 10,              // 이미지 후보 수
    cfImageSteps: 6,                  // AI 이미지 생성 스텝
    showBrowser: false,               // 브라우저 보기
    claudeTimeoutSec: 180,            // Claude 타임아웃 (초)
    claudeConcurrency: 2,             // Claude 동시 실행 수
  },

  // 범위 클램프
  LIMITS: {
    dryRun: undefined,
    killSwitch: undefined,
    visibility: ["public", "neighbor", "both", "private"],
    dailyPublishLimit: [1, 50],
    minPublishIntervalMin: [0, 720],
    scrapeTopN: [3, 30],
    imageCandidates: [3, 20],
    cfImageSteps: [1, 8],
    showBrowser: undefined,
    claudeTimeoutSec: [30, 900],
    claudeConcurrency: [1, 6],
  },

  // 경로
  DATA_DIR: path.resolve(process.cwd(), "data"),
  DB_PATH: path.resolve(process.cwd(), "data", "app.db"),
  NAVER_SESSION_PATH: path.resolve(process.cwd(), "data", "naver_session.json"),
  IMAGES_DIR: path.resolve(process.cwd(), "data", "images"),

  // 네이버 에디터 URL
  NAVER_BLOG_WRITE_URL: "https://blog.naver.com/{blogId}?Redirect=Write&categoryNo=0",

  // 타임아웃
  LOGIN_TIMEOUT_SEC: 300,
  PUBLISH_TIMEOUT_SEC: 900,

  // SSE 폴링
  SSE_POLL_INTERVAL_MS: 1000,

  // 이미지 수집
  IMAGE_MIN_SIZE: 3000,  // 바이트
  IMAGE_LAZY_LOAD_SCROLL: 2200,  // 스크롤 픽셀

  // 파일 선택 타임아웃 (폴더 선택 대화상자)
  FOLDER_DIALOG_TIMEOUT_MS: 120000,

  // 폴더 선택 대화상자
  FOLDER_DIALOG: {
    mac: 'osascript -e \'POSIX path of (choose folder with prompt "사진 폴더를 선택하세요")\'',
    win: `powershell -NoProfile -STA -Command "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.FolderBrowserDialog; $f.Description = '사진 폴더를 선택하세요'; if ($f.ShowDialog() -eq 'OK') { $f.SelectedPath }"`,
  },
};
