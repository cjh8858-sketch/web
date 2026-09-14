import requests
import json
from typing import List, Dict
from routes.api_settings import get_setting

# 네이버 검색 API 엔드포인트
NAVER_NEWS_API = "https://openapi.naver.com/v1/search/news.json"
NAVER_BLOG_API = "https://openapi.naver.com/v1/search/blog.json"

def _get_naver_headers() -> dict:
    """
    네이버 오픈API 인증 헤더 생성.
    설정에서 Client ID와 Secret을 가져옴.
    """
    client_id = get_setting("naver_client_id")
    client_secret = get_setting("naver_client_secret")

    print(f"[DEBUG] DB에서 가져온 Client ID: {client_id}")
    print(f"[DEBUG] DB에서 가져온 Client Secret: {client_secret[:20] if client_secret else 'NONE'}...")

    if not client_id or not client_secret:
        raise ValueError("Naver API credentials not configured. Please set them in settings.")

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    print(f"[DEBUG] 생성된 헤더: {headers}")
    return headers

def _call_naver_api(endpoint: str, params: dict) -> dict:
    """
    네이버 검색 API 공통 호출 헬퍼.

    Args:
        endpoint: API 엔드포인트 URL
        params: 쿼리 파라미터

    Returns:
        API 응답 JSON (또는 오류 정보)
    """
    try:
        headers = _get_naver_headers()

        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        print(f"Naver API call successful: {endpoint} with query='{params.get('query')}'")
        return data

    except ValueError as e:
        print(f"Configuration error: {e}")
        raise
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise ValueError("Invalid Naver API credentials")
        elif response.status_code == 429:
            raise ValueError("Naver API rate limit exceeded (25,000 per day)")
        else:
            raise ValueError(f"Naver API error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Network error calling Naver API: {e}")
        raise ValueError(f"Network error: {str(e)}")

def search_news(query: str, display: int = 10, sort: str = "sim") -> List[Dict]:
    """
    네이버 뉴스 검색.

    Args:
        query: 검색어
        display: 반환 결과 개수 (최대 100)
        sort: 정렬 방식 ("sim" = 유사도순, "date" = 최신순)

    Returns:
        표준화된 뉴스 결과 리스트
        [
            {
                "title": str,
                "description": str,
                "link": str,
                "source_type": "news",
                "pubDate": str
            }
        ]
    """
    try:
        if not query or not query.strip():
            return []

        display = min(max(display, 1), 100)  # 1-100 범위

        params = {
            "query": query,
            "display": display,
            "sort": sort
        }

        data = _call_naver_api(NAVER_NEWS_API, params)

        results = []
        for item in data.get("items", []):
            result = {
                "title": _clean_html(item.get("title", "")),
                "description": _clean_html(item.get("description", "")),
                "link": item.get("link", ""),
                "source_type": "news",
                "pubDate": item.get("pubDate", "")
            }
            results.append(result)

        print(f"News search returned {len(results)} results")
        return results

    except Exception as e:
        print(f"Error searching news: {e}")
        raise

def search_blogs(query: str, display: int = 10, sort: str = "sim") -> List[Dict]:
    """
    네이버 블로그 검색.

    Args:
        query: 검색어
        display: 반환 결과 개수 (최대 100)
        sort: 정렬 방식 ("sim" = 유사도순, "date" = 최신순)

    Returns:
        표준화된 블로그 결과 리스트
        [
            {
                "title": str,
                "description": str,
                "link": str,
                "source_type": "blog",
                "postdate": str,
                "bloggername": str
            }
        ]
    """
    try:
        if not query or not query.strip():
            return []

        display = min(max(display, 1), 100)  # 1-100 범위

        params = {
            "query": query,
            "display": display,
            "sort": sort
        }

        data = _call_naver_api(NAVER_BLOG_API, params)

        results = []
        for item in data.get("items", []):
            result = {
                "title": _clean_html(item.get("title", "")),
                "description": _clean_html(item.get("description", "")),
                "link": item.get("link", ""),
                "source_type": "blog",
                "postdate": item.get("postdate", ""),
                "bloggername": item.get("bloggername", "")
            }
            results.append(result)

        print(f"Blog search returned {len(results)} results")
        return results

    except Exception as e:
        print(f"Error searching blogs: {e}")
        raise

def collect_source_material(keyword: str, display: int = 5) -> List[Dict]:
    """
    뉴스와 블로그 검색을 통합해 글감 자료를 수집.

    Args:
        keyword: 검색 키워드
        display: 각 검색별 반환 개수

    Returns:
        뉴스와 블로그를 섞은 소스 자료 리스트 (최대 display*2개)
    """
    try:
        if not keyword or not keyword.strip():
            return []

        materials = []

        # 뉴스 검색
        print(f"Collecting news for keyword: {keyword}")
        try:
            news_results = search_news(keyword, display=display)
            materials.extend(news_results)
        except Exception as e:
            print(f"Warning: News search failed: {e}")

        # 블로그 검색
        print(f"Collecting blogs for keyword: {keyword}")
        try:
            blog_results = search_blogs(keyword, display=display)
            materials.extend(blog_results)
        except Exception as e:
            print(f"Warning: Blog search failed: {e}")

        print(f"Total source materials collected: {len(materials)}")
        return materials

    except Exception as e:
        print(f"Error collecting source material: {e}")
        return []

def _clean_html(text: str) -> str:
    """
    HTML 태그 제거 (네이버 API는 일부 HTML 태그를 반환할 수 있음).
    """
    import re
    # 기본 HTML 태그 제거
    clean = re.sub(r'<[^>]+>', '', text)
    # HTML 엔티티 디코딩
    clean = clean.replace("&amp;", "&")
    clean = clean.replace("&lt;", "<")
    clean = clean.replace("&gt;", ">")
    clean = clean.replace("&quot;", '"')
    clean = clean.replace("&#39;", "'")
    return clean.strip()

# 테스트 헬퍼 (명령행 실행용)
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        print(f"Testing Naver API with keyword: {keyword}")

        try:
            materials = collect_source_material(keyword, display=3)
            print(f"\nCollected {len(materials)} materials:")
            for i, material in enumerate(materials, 1):
                print(f"\n{i}. [{material['source_type'].upper()}] {material['title']}")
                print(f"   Description: {material['description'][:100]}...")
                print(f"   Link: {material['link']}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python naver_search.py <keyword>")
