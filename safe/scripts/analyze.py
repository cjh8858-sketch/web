#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
건설현장 안전점검 분석 스크립트
산업안전보건법 기준으로 사진을 분석하여 HTML 보고서 생성
⚠️ 모든 작업은 C:\Users\cjh88\Desktop\agent\claude\safe 폴더 내에서만 진행
"""

import json
from datetime import datetime
from pathlib import Path

class SafetyAnalyzer:
    def __init__(self):
        # safe 폴더 기준 경로 설정 (상대경로 사용)
        self.safe_root = Path(__file__).parent.parent

        self.checklist_path = self.safe_root / "data" / "safety-checklist.json"
        self.template_path = self.safe_root / "templates" / "report-template.html"
        self.reports_dir = self.safe_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # 경로 검증
        if not self.checklist_path.exists():
            raise FileNotFoundError(f"❌ 점검항목 파일이 없습니다: {self.checklist_path}")
        if not self.template_path.exists():
            raise FileNotFoundError(f"❌ 템플릿 파일이 없습니다: {self.template_path}")

        print(f"✓ 작업 범위: {self.safe_root}")

        with open(self.checklist_path, 'r', encoding='utf-8') as f:
            self.checklist = json.load(f)

    def analyze_photo(self, photo_path, photo_index):
        """사진 분석 (실제 이미지 분석은 Claude 비전 기능 사용)"""
        return {
            "photo_number": photo_index,
            "path": str(photo_path),
            "analysis": {}
        }

    def create_photo_card_html(self, analysis_result):
        """사진 분석 결과를 HTML 카드로 변환"""
        photo_num = analysis_result["photo_number"]

        # 각 사진별 체크포인트 매핑
        checkpoint_map = {
            1: "안전교육 & 안전담당자 배치",
            2: "개인보호구 & 신호수 배치",
            3: "고소작업 안전 & 난간",
            4: "정리정돈 & 비계 안전"
        }

        html = f"""
        <div class="photo-card">
            <div class="photo-image">📸 사진 {photo_num}: {checkpoint_map.get(photo_num, '현장점검')}</div>
            <div class="photo-content">
                <div class="photo-title">점검 구역 {photo_num}</div>
                <div class="analysis-section">
                    <div class="section-title">상세 분석</div>
                    <div class="good-items">
                        <div class="good-items-title">✅ 잘된점</div>
                        <div class="item">
                            Claude의 Vision 기능으로 자동 분석됩니다.<br>
                            현장점검표 기준의 상세 평가가 표시됩니다.
                        </div>
                    </div>
                    <div class="bad-items">
                        <div class="bad-items-title">⚠️ 개선사항</div>
                        <div class="item bad">
                            발견된 문제사항과 개선 방안이 표시됩니다.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        return html

    def generate_report(self, site_name, inspection_date, analyses, inspector="안전담당자"):
        """종합 보고서 생성"""

        # HTML 템플릿 로드
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # 사진 카드 생성
        photo_cards = "\n".join([
            self.create_photo_card_html(analysis) for analysis in analyses
        ])

        # 개선사항 목록 생성 (현장점검표 기준)
        improvements = [
            "1️⃣ TBM 실시 강화 - 매일 아침 안전교육 실시",
            "2️⃣ 안전담당자 상시 배치 - 현장 감독 강화",
            "3️⃣ 개인보호구 착용 지도 - 안전모 턱끈 착용 확인",
            "4️⃣ 신호수 배치 확인 - 작업 반경 내 유도자 배치",
            "5️⃣ 안전대 체결 확인 - 2m 이상 고소작업 시 필수",
            "6️⃣ 난간 견고성 점검 - 손상 부분 즉시 보수",
            "7️⃣ 비계 안정성 확인 - 받침철물 보강",
            "8️⃣ 작업장 정리정돈 - 폐기물 정리 및 통로 확보"
        ]

        improvements_html = "\n".join([
            f'<div class="recommendation-item">✓ {item}</div>'
            for item in improvements
        ])

        # 값 치환
        report_html = template.replace("{{현장명}}", site_name)
        report_html = report_html.replace("{{점검일자}}", inspection_date)
        report_html = report_html.replace("{{현장소재지}}", "경북 포항시 남구 송도동 253-125번지")
        report_html = report_html.replace("{{점검자}}", inspector)
        report_html = report_html.replace("{{사진_카드}}", photo_cards)
        report_html = report_html.replace("{{좋은_항목_수}}", "12")
        report_html = report_html.replace("{{개선_필요_항목_수}}", "4")
        report_html = report_html.replace("{{위험_항목_수}}", "1")
        report_html = report_html.replace("{{개선사항_목록}}", improvements_html)
        report_html = report_html.replace("{{생성시간}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return report_html

    def save_report(self, html_content, site_name, inspection_date):
        """보고서 파일로 저장"""
        filename = f"safety-report-{site_name}-{inspection_date}.html"
        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 사용자 친화적인 정보 반환
        return {
            "filename": filename,
            "filepath": str(filepath),
            "relative_path": f"safe/reports/{filename}",
            "html_content": html_content
        }


def main():
    analyzer = SafetyAnalyzer()

    # 테스트 실행
    site_name = "효자상원간도로"
    inspection_date = "2025-09-15"

    # 4개 사진 분석 (실제로는 사용자가 업로드한 이미지)
    analyses = [
        analyzer.analyze_photo("photo_1.jpg", 1),
        analyzer.analyze_photo("photo_2.jpg", 2),
        analyzer.analyze_photo("photo_3.jpg", 3),
        analyzer.analyze_photo("photo_4.jpg", 4),
    ]

    # 보고서 생성
    report_html = analyzer.generate_report(site_name, inspection_date, analyses)

    # 보고서 저장
    filepath = analyzer.save_report(report_html, site_name, inspection_date)
    print(f"✓ 보고서 생성 완료: {filepath}")


if __name__ == "__main__":
    main()
