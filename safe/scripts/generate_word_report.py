#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전보건지킴이 활동보고서 워드 파일 생성
안전보건지킴이 사업장별 활동보고 서식 기반
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from datetime import datetime
from pathlib import Path

class SafetyReportGenerator:
    def __init__(self):
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def create_word_report(self, site_name, inspection_date, site_manager, inspector, address,
                          checkpoints_data, improvements_required, best_practices):
        """워드 보고서 생성"""

        doc = Document()

        # 문서 여백 설정
        sections = doc.sections
        for section in sections:
            section.top_margin = Cm(2)
            section.bottom_margin = Cm(2)
            section.left_margin = Cm(2)
            section.right_margin = Cm(2)

        # ===== 제목 =====
        title = doc.add_paragraph()
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        title_run = title.add_run("2026년 안전보건지킴이 현장점검 활동보고")
        title_run.font.size = Pt(16)
        title_run.font.bold = True

        # ===== 현장 개요 =====
        doc.add_paragraph("□ 현장 개요", style='Heading 2')

        # 현장 개요 테이블
        table = doc.add_table(rows=4, cols=4)
        table.style = 'Table Grid'

        # 헤더 행
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "현장명"
        hdr_cells[1].text = site_name
        hdr_cells[2].text = "점검일자"
        hdr_cells[3].text = inspection_date

        # 2행
        cells = table.rows[1].cells
        cells[0].text = "현장관계자"
        cells[1].text = site_manager
        cells[2].text = "점검자"
        cells[3].text = inspector

        # 3행
        cells = table.rows[2].cells
        cells[0].text = "현장소재지"
        cells[1].merge(cells[2])
        cells[1].text = address

        doc.add_paragraph()

        # ===== 점검내용 및 조치사항 =====
        doc.add_paragraph("□ 점검내용 및 조치사항 (항목별)", style='Heading 2')

        # 8가지 체크포인트별 점검 결과
        checkpoints = [
            "1. 작업전 TBM실시 및 근로자 안전교육",
            "2. 안전담당자(관리감독자) 현장배치 및 감독",
            "3. 안전모(턱끈 포함), 안전화 등 보호구 착용",
            "4. 신호수(유도자) 배치 여부",
            "5. 2m 이상 고소작업 시 안전대 체결",
            "6. 작업발판·통로 안전난간 견고성",
            "7. 비계 기둥 하부 침하방지 조치",
            "8. 작업장·통로 정리정돈 상태"
        ]

        for i, checkpoint in enumerate(checkpoints):
            doc.add_paragraph()
            checkpoint_heading = doc.add_paragraph(checkpoint)
            checkpoint_heading_run = checkpoint_heading.runs[0]
            checkpoint_heading_run.bold = True

            # 위험요인 및 개선사항
            doc.add_paragraph("중점관리 위험요인 및 개선사항:", style='List Bullet')
            doc.add_paragraph("[분석 내용이 입력됩니다]", style='List Bullet 2')

            # 보완 후 재점검 필요사항
            doc.add_paragraph("보완 후 재점검 필요사항:", style='List Bullet')
            doc.add_paragraph("[필요시 재점검 항목이 입력됩니다]", style='List Bullet 2')

            # 모범사례
            doc.add_paragraph("모범사례:", style='List Bullet')
            doc.add_paragraph("[우수 사례가 입력됩니다]", style='List Bullet 2')

            # 사진 영역
            doc.add_paragraph("📸 현장점검 사진 1")
            doc.add_paragraph("[사진 1]")
            doc.add_paragraph("📸 현장점검 사진 2")
            doc.add_paragraph("[사진 2]")

        # ===== 종합 조치사항 =====
        doc.add_paragraph()
        doc.add_paragraph("□ 종합 조치사항", style='Heading 2')

        summary = doc.add_paragraph()
        summary_run = summary.add_run(f"개선필요 {improvements_required}건, 모범사례 {best_practices}건")
        summary_run.bold = True
        summary_run.font.size = Pt(12)

        doc.add_paragraph()
        doc.add_paragraph("주요 위험요인 개선(물리적 안전):", style='List Bullet')
        doc.add_paragraph("난간 견고성, 안전대 체결, 기계 미작동 등 개선 내용", style='List Bullet 2')

        doc.add_paragraph("안전의식 개선(심리적 안전):", style='List Bullet')
        doc.add_paragraph("안전사고 예방을 위한 사전 TBM 안내, 안전행동 가이드", style='List Bullet 2')

        # ===== 점검 확인 =====
        doc.add_paragraph()
        doc.add_paragraph("□ 현장 점검 확인", style='Heading 2')

        confirm_table = doc.add_table(rows=4, cols=3)
        confirm_table.style = 'Table Grid'

        cells = confirm_table.rows[0].cells
        cells[0].text = "소속"
        cells[1].text = "성명"
        cells[2].text = "서명"

        cells = confirm_table.rows[1].cells
        cells[0].text = "점검자"
        cells[1].text = "경북 안전보건지킴이"
        cells[2].text = ""

        cells = confirm_table.rows[2].cells
        cells[0].text = "점검자"
        cells[1].text = "경북 안전보건지킴이"
        cells[2].text = ""

        cells = confirm_table.rows[3].cells
        cells[0].text = "현장관계자"
        cells[1].text = ""
        cells[2].text = ""

        # 생성 정보 추가
        doc.add_paragraph()
        footer = doc.add_paragraph()
        footer_run = footer.add_run(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        footer_run.font.size = Pt(10)
        footer_run.font.color.rgb = RGBColor(128, 128, 128)

        return doc

    def save_report(self, doc, site_name, inspection_date):
        """보고서 저장"""
        # 파일명 생성 (한글 제거)
        safe_site_name = site_name.replace(" ", "").replace("~", "-")
        filename = f"safety-report-{safe_site_name}-{inspection_date}.docx"
        filepath = self.reports_dir / filename

        doc.save(str(filepath))
        return filepath


def main():
    """테스트 실행"""
    generator = SafetyReportGenerator()

    # 테스트 데이터
    doc = generator.create_word_report(
        site_name="효자~상원간도로 건설공사",
        inspection_date="2026-09-15",
        site_manager="홍길동((주)두산건설)",
        inspector="경북 안전보건지킴이 5조",
        address="경북 포항시 남구 송도동 253-125번지",
        checkpoints_data={},
        improvements_required=4,
        best_practices=2
    )

    filepath = generator.save_report(doc, "효자상원간도로", "2026-09-15")
    print(f"✓ 워드 보고서 생성 완료: {filepath}")


if __name__ == "__main__":
    main()
