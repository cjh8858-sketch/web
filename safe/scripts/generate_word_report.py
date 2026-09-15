#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전보건지킴이 활동보고서 워드 파일 생성
정확한 양식: 안전보건지킴이 사업장별 활동보고 서식 (변경 금지)
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from datetime import datetime
from pathlib import Path

class SafetyReportGenerator:
    def __init__(self):
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def create_word_report(self, site_name, inspection_date, site_manager, inspector, address):
        """정확한 양식에 따른 워드 보고서 생성"""

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
        title_run.font.size = Pt(14)
        title_run.font.bold = True

        doc.add_paragraph()

        # ===== 현장 개요 =====
        doc.add_paragraph("□ 현장 개요")

        # 현장 개요 테이블 (정확한 양식: 3행 x 4열)
        table = doc.add_table(rows=3, cols=4)
        table.style = 'Table Grid'

        # 1행: 현장명, 점검일자
        cells = table.rows[0].cells
        cells[0].text = "현장명"
        cells[1].text = site_name
        cells[2].text = "점검일자"
        cells[3].text = inspection_date

        # 2행: 현장관계자, 점검자
        cells = table.rows[1].cells
        cells[0].text = "현장관계자"
        cells[1].text = site_manager
        cells[2].text = "점 검 자"
        cells[3].text = inspector

        # 3행: 현장소재지
        cells = table.rows[2].cells
        cells[0].text = "현장소재지"
        cells[1].merge(cells[2])
        cells[1].text = address

        doc.add_paragraph()

        # ===== 점검내용 및 조치사항 =====
        doc.add_paragraph("□ 점검내용 및 조치사항 (항목별)")

        # 8가지 체크포인트 (정확한 현장점검표 양식)
        checkpoints = [
            "○ 작업전 TBM실시 및 근로자 안전교육 상태",
            "○ 안전담당자(관리감독자) 현장배치 여부 및 현장 지휘·감독 상태",
            "○ 안전모(턱끈 포함), 안전화 등 보호구 지급·착용 상태",
            "○ 굴삭기, 지게차 등 작업 반경 내 신호수(유도자) 배치 여부",
            "○ 2m 이상 고소작업 시 안전대 체결 여부 확인",
            "○ 작업발판 및 통로 단부에 안전난간이 견고한지 여부",
            "○ 비계 기둥 하부에 침하방지 조치(받침철물 등) 상태",
            "○ 작업장 및 이동 통로에 넘어질 우려가 되는 자재, 폐기물 정리 상태"
        ]

        for i, checkpoint in enumerate(checkpoints):
            p = doc.add_paragraph(checkpoint)
            p.paragraph_format.left_indent = Cm(0.3)

            # 내용 테이블 (2행 x 2열: 좌측 우측)
            content_table = doc.add_table(rows=2, cols=2)
            content_table.style = 'Table Grid'

            # 1행: 위험요인 및 개선사항
            cells = content_table.rows[0].cells
            cells[0].text = "‣ 중점관리 위험요인 및 개선사항\n‣ 보완 후 재점검 필요사항... ‣ 모범사례 등... 작성"
            cells[1].text = "‣ 중점관리 위험요인 및 개선사항\n‣ 보완 후 재점검 필요사항... ‣ 모범사례 등... 작성"

            # 2행: 사진
            cells = content_table.rows[1].cells
            cells[0].text = "현장점검 사진"
            cells[1].text = "현장점검 사진"

        doc.add_paragraph()

        # ===== 종합 조치사항 =====
        doc.add_paragraph("□ 종합 조치사항 : 00건 개선 필요, 모범사례 00건")

        p = doc.add_paragraph("ㅇ 주요 위험요인 개선(물리적 안전)")
        p.paragraph_format.left_indent = Cm(0.5)
        p2 = doc.add_paragraph("난간흔들림, 장비 미작동 등 개선 내용 등")
        p2.paragraph_format.left_indent = Cm(1.0)

        p = doc.add_paragraph("ㅇ 안전의식 개선(심리적 안전)")
        p.paragraph_format.left_indent = Cm(0.5)
        p2 = doc.add_paragraph("안전사고 예방을 위한 사전 TBM 안내, 안전행동 가이드 등")
        p2.paragraph_format.left_indent = Cm(1.0)

        doc.add_paragraph()

        # ===== 현장 점검 확인 =====
        doc.add_paragraph("□ 현장 점검 확인 : 20   .   .   .")

        confirm_table = doc.add_table(rows=4, cols=3)
        confirm_table.style = 'Table Grid'

        # 헤더
        cells = confirm_table.rows[0].cells
        cells[0].text = "소 속"
        cells[1].text = "성 명"
        cells[2].text = "서 명"

        # 점검자 1
        cells = confirm_table.rows[1].cells
        cells[0].text = "점 검 자"
        cells[1].text = "경북 안전보건지킴이"
        cells[2].text = ""

        # 점검자 2
        cells = confirm_table.rows[2].cells
        cells[0].text = "점 검 자"
        cells[1].text = "경북 안전보건지킴이"
        cells[2].text = ""

        # 현장관계자
        cells = confirm_table.rows[3].cells
        cells[0].text = "현장관계자"
        cells[1].text = ""
        cells[2].text = ""

        return doc

    def save_report(self, doc, site_name, inspection_date):
        """보고서 저장"""
        safe_site_name = site_name.replace(" ", "").replace("~", "-")
        filename = f"safety-report-{safe_site_name}-{inspection_date}.docx"
        filepath = self.reports_dir / filename

        doc.save(str(filepath))
        return filepath


def main():
    """테스트 실행"""
    generator = SafetyReportGenerator()

    doc = generator.create_word_report(
        site_name="효자~상원간도로 건설공사",
        inspection_date="2026-09-15",
        site_manager="홍길동((주)두산건설)",
        inspector="경북 안전보건지킴이 5조",
        address="경북 포항시 남구 송도동 253-125번지"
    )

    filepath = generator.save_report(doc, "효자상원간도로", "2026-09-15")
    print(f"✓ 워드 보고서 생성 완료: {filepath}")


if __name__ == "__main__":
    main()
