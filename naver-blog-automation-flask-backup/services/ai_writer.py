import subprocess
import json
import shutil
import threading
from typing import Dict, List, Optional
from config import Config

CLAUDE_CLI_TIMEOUT_SEC = Config.CLAUDE_CLI_TIMEOUT_SEC

# 블로그 글 구조 정의 JSON 스키마
BLOG_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "블로그 글의 제목 (50자 이내)"
        },
        "intro": {
            "type": "string",
            "description": "글의 도입부 (1-2문장, 독자의 관심을 끌 내용)"
        },
        "sections": {
            "type": "array",
            "description": "글의 주요 섹션들",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {
                        "type": "string",
                        "description": "섹션 제목"
                    },
                    "body": {
                        "type": "string",
                        "description": "섹션 본문 (2-3문단)"
                    },
                    "image_keyword": {
                        "type": "string",
                        "description": "이 섹션에 어울릴 이미지 검색 키워드"
                    }
                },
                "required": ["heading", "body", "image_keyword"]
            },
            "minItems": 2,
            "maxItems": 5
        },
        "outro": {
            "type": "string",
            "description": "글의 마무리 부분 (결론 또는 다음 글으로의 연결)"
        },
        "tags": {
            "type": "array",
            "description": "블로그 태그 (3-5개)",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["title", "intro", "sections", "outro", "tags"]
}

# Claude CLI 호출 동시성 제어 (동시에 여러 호출 방지)
claude_cli_lock = threading.Lock()

def _resolve_claude_executable() -> str:
    """
    Claude Code CLI 실행 파일 경로를 찾음.

    Returns:
        claude 실행 파일 경로

    Raises:
        FileNotFoundError: Claude CLI가 설치되지 않았을 경우
    """
    exe_path = shutil.which("claude")
    if not exe_path:
        raise FileNotFoundError(
            "Claude Code CLI not found. "
            "Please install it: https://claude.com/claude-code\n"
            "And login: claude login"
        )
    return exe_path

def build_writing_prompt(keyword: str, source_materials: List[Dict]) -> str:
    """
    수집된 뉴스/블로그 자료를 바탕으로 블로그 글 작성 프롬프트 생성.

    Args:
        keyword: 검색 키워드
        source_materials: 수집된 소스 자료 리스트

    Returns:
        Claude에 전달할 프롬프트 문자열
    """

    # 소스 자료 포맷팅
    materials_text = ""
    for i, material in enumerate(source_materials, 1):
        source_type = material.get("source_type", "").upper()
        title = material.get("title", "")
        desc = material.get("description", "")[:150]  # 길이 제한

        materials_text += f"\n{i}. [{source_type}] {title}\n   {desc}\n"

    # 프롬프트 구성
    prompt = f"""당신은 네이버 블로그를 운영하는 전문 블로거입니다.
다음 수집된 뉴스와 블로그 글들을 분석해서, "{keyword}" 주제로 새로운 블로그 글을 작성해주세요.

**작성 요구사항:**
1. 톤: 표준적인 블로그 톤 (전문적이면서도 친근한 느낌)
2. 길이: 중간 정도 (도입부 + 3-4개 섹션 + 마무리)
3. 각 섹션: 제목, 본문(2-3문단), 어울리는 이미지 검색 키워드 포함
4. SEO: 관련 태그 3-5개 추가

**수집된 소스 자료:**
{materials_text}

**출력 형식:**
반드시 다음의 JSON 스키마를 따라주세요:
{json.dumps(BLOG_POST_SCHEMA, ensure_ascii=False, indent=2)}

글을 작성할 때:
- 소스 자료의 내용을 자신의 말로 재구성해주세요
- 원본 링크는 인용하지 마세요
- 실제 네이버 블로그 글처럼 자연스럽게 작성해주세요
- 각 섹션의 image_keyword는 유명한 이미지 검색 키워드여야 합니다 (예: "Python 코딩", "머신러닝 다이어그램")
"""

    return prompt

def call_claude_cli(prompt: str, json_schema: Optional[Dict] = None,
                   tools: str = "", timeout: int = CLAUDE_CLI_TIMEOUT_SEC) -> Dict:
    """
    Claude Code CLI를 -p(non-interactive) 모드로 호출.

    Args:
        prompt: 프롬프트 문자열 (stdin으로 전달)
        json_schema: JSON 스키마 (구조화된 출력 강제, 선택사항)
        tools: 활성화할 도구 (예: "", "Read", "Browser")
        timeout: 타임아웃 시간(초)

    Returns:
        {
            "success": bool,
            "data": 결과 (스키마가 있으면 파싱된 JSON, 없으면 텍스트),
            "error": 오류 메시지 (실패시만)
        }
    """
    with claude_cli_lock:  # 동시 실행 방지
        try:
            exe_path = _resolve_claude_executable()

            # 명령행 구성
            cmd = [exe_path, "-p", "--output-format", "json"]

            if tools:
                cmd.extend(["--tools", tools])

            if json_schema:
                cmd.extend(["--json-schema", json.dumps(json_schema, ensure_ascii=False)])

            print(f"Calling Claude CLI with timeout {timeout}s...")

            # 서브프로세스 실행 (stdin으로 프롬프트 전달)
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout
            )

            # 표준 출력 파싱
            if result.returncode != 0:
                print(f"Claude CLI error (returncode {result.returncode})")
                print(f"stderr: {result.stderr}")
                return {
                    "success": False,
                    "error": f"Claude CLI error: {result.stderr}"
                }

            # JSON 응답 파싱
            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"Failed to parse Claude CLI response: {e}")
                return {
                    "success": False,
                    "error": f"Invalid response format: {str(e)}"
                }

            # 응답 체크
            if response.get("is_error"):
                error_msg = response.get("result", "Unknown error")
                print(f"Claude returned error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }

            # 결과 추출
            result_text = response.get("result", "")

            # JSON 스키마가 있으면 파싱
            if json_schema:
                try:
                    data = json.loads(result_text)
                    print("Claude CLI call successful with JSON schema")
                    return {
                        "success": True,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    print(f"Failed to parse structured output: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to parse JSON output: {str(e)}"
                    }
            else:
                print("Claude CLI call successful")
                return {
                    "success": True,
                    "data": result_text
                }

        except subprocess.TimeoutExpired:
            print(f"Claude CLI timeout after {timeout}s")
            return {
                "success": False,
                "error": f"Timeout after {timeout} seconds"
            }
        except FileNotFoundError as e:
            print(f"Claude CLI not found: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            print(f"Error calling Claude CLI: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

def generate_blog_post(keyword: str, source_materials: List[Dict]) -> Dict:
    """
    수집된 자료를 바탕으로 Claude가 블로그 글을 작성.

    Args:
        keyword: 검색 키워드
        source_materials: 수집된 뉴스/블로그 자료

    Returns:
        {
            "success": bool,
            "data": 생성된 글 (JSON 형식),
            "error": 오류 메시지 (실패시만)
        }
    """
    try:
        if not source_materials:
            return {
                "success": False,
                "error": "No source materials provided"
            }

        # 프롬프트 생성
        prompt = build_writing_prompt(keyword, source_materials)

        # Claude CLI 호출
        result = call_claude_cli(
            prompt=prompt,
            json_schema=BLOG_POST_SCHEMA,
            tools="",  # 도구 사용 불필요
            timeout=CLAUDE_CLI_TIMEOUT_SEC
        )

        if not result["success"]:
            return result

        # 결과 검증
        post = result["data"]
        if not isinstance(post, dict):
            return {
                "success": False,
                "error": "Invalid post structure"
            }

        print(f"Blog post generated: {post.get('title', 'N/A')}")
        return {
            "success": True,
            "data": post
        }

    except Exception as e:
        print(f"Error generating blog post: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# 테스트 헬퍼 (명령행 실행용)
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        print(f"Testing AI writer with keyword: {keyword}")

        # 테스트 소스 자료
        test_materials = [
            {
                "title": f"Introduction to {keyword}",
                "description": "Learn the basics of this topic",
                "source_type": "news",
                "link": "https://example.com/1"
            },
            {
                "title": f"Advanced {keyword} techniques",
                "description": "Deep dive into advanced concepts",
                "source_type": "blog",
                "link": "https://example.com/2"
            }
        ]

        try:
            result = generate_blog_post(keyword, test_materials)
            if result["success"]:
                post = result["data"]
                print(f"\nGenerated post:")
                print(f"Title: {post.get('title')}")
                print(f"Intro: {post.get('intro')}")
                print(f"Sections: {len(post.get('sections', []))}")
                print(f"Tags: {post.get('tags')}")
            else:
                print(f"Error: {result['error']}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python ai_writer.py <keyword>")
