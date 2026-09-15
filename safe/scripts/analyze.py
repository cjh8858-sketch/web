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

        html = f"""
        <div class="photo-card">
            <div class="photo-image">사진 {photo_num}: [이미지 업로드 필요]</div>
            <div class="photo-content">
                <div class="photo-title">점검 구역 {photo_num}</div>
                <div class="analysis-section">
                    <div class="section-title">종합 평가</div>
                    <p style="font-size: 13px; color: #555; margin: 10px 0;">
                        사진 분석을 위해 실제 이미지가 필요합니다.<br>
                        Claude의 Vision 기능을 사용하여 자동 분석됩니다.
                    </p>
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

        # 개선사항 목록 생성 (예시)
        improvements = [
            "난간 안전성 점검 및 필요시 보수",
            "모든 근로자의 안전모 착용 확인 및 지도",
            "작업장 정리정돈 강화 - 폐기물 정리",
            "전기배선 상태 점검 및 누전차단기 동작 확인"
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

        return filepath


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
