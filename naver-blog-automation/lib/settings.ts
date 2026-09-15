import { getDb, runQuery, runQueryOne, runUpdate } from "@/lib/db";
import { CONFIG } from "@/config";
import { AllSettings, SettingsKeySchema } from "@/lib/types";

// 초기화 - 기본값 설정
export function initializeSettings() {
  const db = getDb();

  for (const [key, value] of Object.entries(CONFIG.DEFAULTS)) {
    const existing = runQueryOne<{ value: string }>(
      "SELECT value FROM settings WHERE key = ?",
      [key]
    );

    if (!existing) {
      db.prepare("INSERT INTO settings (key, value) VALUES (?, ?)").run(
        key,
        String(value)
      );
    }
  }
}

// 모든 설정 가져오기
export function getSettings(): AllSettings {
  const rows = runQuery<{ key: string; value: string }>(
    "SELECT key, value FROM settings"
  );

  const result: AllSettings = {};
  for (const row of rows) {
    const key = row.key;
    const value = row.value;

    // 타입별로 파싱
    if (
      key === "dryRun" ||
      key === "killSwitch" ||
      key === "showBrowser"
    ) {
      result[key] = value === "true" || value === "1";
    } else if (
      key === "dailyPublishLimit" ||
      key === "minPublishIntervalMin" ||
      key === "scrapeTopN" ||
      key === "imageCandidates" ||
      key === "cfImageSteps" ||
      key === "claudeTimeoutSec" ||
      key === "claudeConcurrency"
    ) {
      result[key] = parseInt(value, 10);
    } else {
      result[key] = value;
    }
  }

  return result;
}

// 단일 설정 가져오기
export function getSetting(key: string): string | number | boolean | undefined {
  const row = runQueryOne<{ value: string }>(
    "SELECT value FROM settings WHERE key = ?",
    [key]
  );

  if (!row) return undefined;

  const value = row.value;

  if (key === "dryRun" || key === "killSwitch" || key === "showBrowser") {
    return value === "true" || value === "1";
  } else if (
    key === "dailyPublishLimit" ||
    key === "minPublishIntervalMin" ||
    key === "scrapeTopN" ||
    key === "imageCandidates" ||
    key === "cfImageSteps" ||
    key === "claudeTimeoutSec" ||
    key === "claudeConcurrency"
  ) {
    return parseInt(value, 10);
  }

  return value;
}

// 설정 저장 (범위 클램프 포함)
export function setSetting(key: string, value: any): void {
  // 키 검증
  try {
    SettingsKeySchema.parse(key);
  } catch {
    throw new Error(`Invalid setting key: ${key}`);
  }

  let clampedValue = String(value);

  // 범위 클램프
  const limits = (CONFIG.LIMITS as any)[key];
  if (Array.isArray(limits) && limits.length === 2) {
    const [min, max] = limits;
    let numValue = parseInt(clampedValue, 10);
    numValue = Math.max(min, Math.min(max, numValue));
    clampedValue = String(numValue);
  }

  // visibility는 enum 검증
  if (
    key === "visibility" &&
    !["public", "neighbor", "both", "private"].includes(clampedValue)
  ) {
    throw new Error(`Invalid visibility value: ${clampedValue}`);
  }

  const db = getDb();
  db.prepare("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)").run(
    key,
    clampedValue
  );
}

// 모든 설정 리셋
export function resetSettings(): void {
  const db = getDb();
  db.prepare("DELETE FROM settings").run();
  initializeSettings();
}
