import requests
from typing import List, Dict, Optional
from pathlib import Path
from config import Config
from routes.api_settings import get_setting
from services.ai_writer import call_claude_cli

UNSPLASH_API = "https://api.unsplash.com/search/photos"
PIXABAY_API = "https://pixabay.com/api"

def search_unsplash(query: str, count: int = 5) -> List[Dict]:
    """
    Unsplash에서 이미지 검색.

    Args:
        query: 검색어
        count: 반환 개수

    Returns:
        [{"url": str, "description": str, "tags": str, "source": "unsplash"}, ...]
    """
    try:
        api_key = get_setting("unsplash_key")
        if not api_key:
            print("Unsplash API key not configured")
            return []

        params = {
            "query": query,
            "per_page": count,
            "client_id": api_key
        }

        response = requests.get(UNSPLASH_API, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = []

        for item in data.get("results", []):
            result = {
                "url": item.get("urls", {}).get("regular", ""),
                "description": item.get("alt_description", item.get("description", "")),
                "tags": ", ".join([t.get("title", "") for t in item.get("tags", [])[:3]]),
                "source": "unsplash"
            }
            if result["url"]:
                results.append(result)

        print(f"Unsplash search returned {len(results)} images for '{query}'")
        return results

    except requests.exceptions.RequestException as e:
        print(f"Unsplash API error: {e}")
        return []
    except Exception as e:
        print(f"Error searching Unsplash: {e}")
        return []

def search_pixabay(query: str, count: int = 5) -> List[Dict]:
    """
    Pixabay에서 이미지 검색.

    Args:
        query: 검색어
        count: 반환 개수

    Returns:
        [{"url": str, "description": str, "tags": str, "source": "pixabay"}, ...]
    """
    try:
        api_key = get_setting("pixabay_key")
        if not api_key:
            print("Pixabay API key not configured")
            return []

        params = {
            "q": query,
            "per_page": count,
            "key": api_key,
            "image_type": "photo",
            "order": "popular"
        }

        response = requests.get(PIXABAY_API, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = []

        for item in data.get("hits", []):
            result = {
                "url": item.get("webformatURL", ""),
                "description": f"Photo by {item.get('user', '')}",
                "tags": item.get("tags", ""),
                "source": "pixabay"
            }
            if result["url"]:
                results.append(result)

        print(f"Pixabay search returned {len(results)} images for '{query}'")
        return results

    except requests.exceptions.RequestException as e:
        print(f"Pixabay API error: {e}")
        return []
    except Exception as e:
        print(f"Error searching Pixabay: {e}")
        return []

def find_images_for_section(image_keyword: str, min_count: int = 3) -> List[Dict]:
    """
    섹션에 어울릴 이미지를 Unsplash 우선, 부족하면 Pixabay로 검색.

    Args:
        image_keyword: 이미지 검색 키워드
        min_count: 최소 반환 개수

    Returns:
        후보 이미지 리스트
    """
    try:
        candidates = []

        # Unsplash 우선 검색
        candidates.extend(search_unsplash(image_keyword, count=min_count))

        # Unsplash 결과가 부족하면 Pixabay로 보완
        if len(candidates) < min_count:
            shortage = min_count - len(candidates)
            candidates.extend(search_pixabay(image_keyword, count=shortage + 2))

        print(f"Found {len(candidates)} image candidates for '{image_keyword}'")
        return candidates[:min_count * 2]  # 너무 많지 않게 제한

    except Exception as e:
        print(f"Error finding images: {e}")
        return []

def judge_image_fit(section_body: str, candidates: List[Dict]) -> Dict:
    """
    후보 이미지 중에서 글 맥락과 가장 어울리는 것을 선택.
    Claude를 사용해 메타데이터 기반으로 판단.

    Args:
        section_body: 섹션 본문
        candidates: 후보 이미지 리스트

    Returns:
        {
            "selected_index": int,
            "selected_url": str,
            "reason": str
        }
    """
    try:
        if not candidates:
            return {"selected_index": -1, "selected_url": "", "reason": "No candidates"}

        if len(candidates) == 1:
            return {
                "selected_index": 0,
                "selected_url": candidates[0]["url"],
                "reason": "Only one candidate"
            }

        # 후보 이미지 정보 포맷팅
        candidates_text = ""
        for i, img in enumerate(candidates):
            candidates_text += f"\n{i}. [{img['source']}]\n"
            candidates_text += f"   Description: {img.get('description', 'N/A')}\n"
            candidates_text += f"   Tags: {img.get('tags', 'N/A')}\n"

        # Claude에 판단 요청
        judge_prompt = f"""다음 글 섹션에 어울릴 이미지를 선택해주세요.

**글 섹션:**
{section_body[:500]}

**후보 이미지:**
{candidates_text}

선택 기준:
1. 글의 주제와 관련성
2. 이미지의 시각적 품질 (메타데이터 기반)
3. 일반적인 블로그 글에 어울리는 정도

**응답 형식 (JSON):**
{{
    "selected_index": (선택한 이미지 번호, 0부터 시작),
    "reason": "선택 이유"
}}
"""

        # Claude에 판단 요청
        schema = {
            "type": "object",
            "properties": {
                "selected_index": {"type": "integer"},
                "reason": {"type": "string"}
            },
            "required": ["selected_index", "reason"]
        }

        result = call_claude_cli(judge_prompt, json_schema=schema, tools="", timeout=30)

        if not result["success"]:
            print(f"Image judgment failed: {result['error']}, using first candidate")
            return {
                "selected_index": 0,
                "selected_url": candidates[0]["url"],
                "reason": "Fallback to first candidate"
            }

        data = result["data"]
        selected_idx = data.get("selected_index", 0)

        # 범위 검사
        if selected_idx < 0 or selected_idx >= len(candidates):
            selected_idx = 0

        return {
            "selected_index": selected_idx,
            "selected_url": candidates[selected_idx]["url"],
            "reason": data.get("reason", "Selected by Claude")
        }

    except Exception as e:
        print(f"Error judging image fit: {e}")
        # Fallback: 첫 번째 이미지 선택
        if candidates:
            return {
                "selected_index": 0,
                "selected_url": candidates[0]["url"],
                "reason": "Error occurred, using first candidate"
            }
        return {"selected_index": -1, "selected_url": "", "reason": str(e)}

def download_image(url: str, dest_path: str) -> str:
    """
    이미지 URL에서 로컬 파일로 다운로드.

    Args:
        url: 이미지 URL
        dest_path: 저장 경로

    Returns:
        저장된 파일 경로 (실패시 빈 문자열)
    """
    try:
        if not url:
            return ""

        # 디렉토리 생성
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)

        # 이미지 다운로드
        response = requests.get(url, timeout=Config.IMAGE_DOWNLOAD_TIMEOUT_SEC)
        response.raise_for_status()

        # 파일 저장
        with open(dest_path, "wb") as f:
            f.write(response.content)

        print(f"Image downloaded: {dest_path}")
        return dest_path

    except requests.exceptions.RequestException as e:
        print(f"Image download error: {e}")
        return ""
    except Exception as e:
        print(f"Error saving image: {e}")
        return ""

# 테스트 헬퍼 (명령행 실행용)
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        print(f"Testing image search with keyword: {keyword}")

        try:
            candidates = find_images_for_section(keyword, min_count=3)
            print(f"\nFound {len(candidates)} candidates")

            if candidates:
                for i, img in enumerate(candidates):
                    print(f"{i+1}. {img['source']}: {img.get('description', 'N/A')}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python image_search.py <keyword>")
