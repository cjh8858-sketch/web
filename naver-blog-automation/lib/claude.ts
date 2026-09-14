import { spawn } from "child_process";
import { z } from "zod";
import { getSetting } from "@/lib/settings";

interface ClaudeResponse {
  type: string;
  result: string;
  is_error: boolean;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
  [key: string]: any;
}

interface RunClaudeOptions {
  images?: string[];
  system?: string;
  retries?: number;
  timeout?: number;
}

interface RunClaudeResult {
  ok: boolean;
  text?: string;
  error?: string;
}

interface RunClaudeJsonOptions extends RunClaudeOptions {
  retries?: number; // 기본 2회 재시도
}

interface RunClaudeJsonResult<T> {
  ok: boolean;
  data?: T;
  error?: string;
}

// Semaphore for concurrency control
class Semaphore {
  private available: number;
  private waiting: Array<() => void> = [];

  constructor(available: number) {
    this.available = available;
  }

  async acquire(): Promise<void> {
    if (this.available > 0) {
      this.available--;
      return;
    }

    return new Promise((resolve) => {
      this.waiting.push(resolve);
    });
  }

  release(): void {
    this.available++;
    const waiter = this.waiting.shift();
    if (waiter) {
      this.available--;
      waiter();
    }
  }
}

const semaphore = new Semaphore(2); // 기본값

// Claude 버전 확인
export async function checkClaude(): Promise<{
  ok: boolean;
  version?: string;
  error?: string;
}> {
  try {
    const result = await runClaude("", {
      timeout: 10000,
    });
    if (result.ok) {
      return { ok: true, version: "installed" };
    }
    return { ok: false, error: result.error };
  } catch (error) {
    return { ok: false, error: String(error) };
  }
}

// 기본 Claude 호출
export async function runClaude(
  prompt: string,
  opts: RunClaudeOptions = {}
): Promise<RunClaudeResult> {
  const concurrency = (getSetting("claudeConcurrency") as number) || 2;

  // 세마포어 크기 업데이트
  if (semaphore["available"] !== undefined) {
    semaphore["available"] = concurrency;
  }

  await semaphore.acquire();

  try {
    const timeout =
      (opts.timeout || ((getSetting("claudeTimeoutSec") as number) || 180)) *
      1000;

    return new Promise((resolve) => {
      const isWin = process.platform === "win32";
      const args = ["-p", "--output-format", "json"];

      if (opts.images && opts.images.length > 0) {
        const imageArgs = opts.images.map((img) => `@${img}`).join(" ");
        prompt = `${prompt}\n${imageArgs}`;
      }

      const proc = spawn("claude", args, {
        shell: isWin,
        timeout,
      });

      let stdout = "";
      let stderr = "";

      proc.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      proc.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      proc.on("error", (error) => {
        resolve({
          ok: false,
          error: `Failed to spawn claude: ${error.message}`,
        });
      });

      proc.on("close", (code) => {
        if (code !== 0) {
          resolve({
            ok: false,
            error: `Claude exited with code ${code}: ${stderr}`,
          });
          return;
        }

        try {
          const response = JSON.parse(stdout) as ClaudeResponse;
          if (response.is_error) {
            resolve({
              ok: false,
              error: response.result || "Claude returned an error",
            });
          } else {
            resolve({
              ok: true,
              text: response.result,
            });
          }
        } catch {
          // 파싱 실패 시 raw text 반환
          resolve({
            ok: true,
            text: stdout,
          });
        }
      });

      // stdin으로 프롬프트 전달
      proc.stdin.write(prompt);
      proc.stdin.end();
    });
  } finally {
    semaphore.release();
  }
}

// JSON 구조화 출력
export async function runClaudeJson<T>(
  prompt: string,
  schema: z.ZodType<T>,
  opts: RunClaudeJsonOptions = {}
): Promise<RunClaudeJsonResult<T>> {
  const retries = opts.retries ?? 2;
  const systemPrompt =
    (opts.system || "") +
    "\n반드시 유효한 JSON 만 출력하라. 설명/마크다운/코드펜스 없이 JSON 객체 또는 배열만 반환하라.";

  for (let attempt = 0; attempt <= retries; attempt++) {
    const result = await runClaude(prompt, {
      ...opts,
      system: systemPrompt,
    });

    if (!result.ok) {
      if (attempt === retries) {
        return { ok: false, error: result.error };
      }
      continue;
    }

    // JSON 추출
    let json: any;
    const text = result.text || "";

    try {
      // ① 코드펜스 찾기
      const fenceMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (fenceMatch) {
        json = JSON.parse(fenceMatch[1].trim());
      } else {
        // ② 첫 { 또는 [ 부터 마지막 짝 문자까지
        const start = Math.max(text.indexOf("{"), text.indexOf("["));
        if (start === -1) {
          if (attempt === retries) {
            return { ok: false, error: "No JSON found in response" };
          }
          continue;
        }

        let end = start;
        let depth = 0;
        const openChar = text[start];
        const closeChar = openChar === "{" ? "}" : "]";

        for (let i = start; i < text.length; i++) {
          if (text[i] === openChar) depth++;
          else if (text[i] === closeChar) {
            depth--;
            if (depth === 0) {
              end = i;
              break;
            }
          }
        }

        json = JSON.parse(text.substring(start, end + 1));
      }
    } catch {
      if (attempt === retries) {
        return { ok: false, error: "Failed to parse JSON from response" };
      }
      continue;
    }

    // Zod 검증
    try {
      const validated = schema.parse(json);
      return { ok: true, data: validated };
    } catch (error) {
      if (attempt === retries) {
        return { ok: false, error: `Validation failed: ${error}` };
      }
      continue;
    }
  }

  return { ok: false, error: "Max retries exceeded" };
}

// 이미지 첨부 헬퍼 (비전)
export function formatImagePath(path: string): string {
  return `@${path}`;
}
