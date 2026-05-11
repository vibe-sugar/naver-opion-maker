# =============================================================================
# 파일명: excel_writer.py
# 목적: 옵션 조합 결과를 네이버 형식의 엑셀 파일로 저장하는 모듈
# 작성일: 2026-05-10
# 버전: 1.0.0
# =============================================================================

"""
엑셀 출력 모듈

옵션 조합 결과를 네이버 옵션 등록 형식의 엑셀(.xlsx) 파일로 저장합니다.

엑셀 컬럼 구조 (A~G열):
    A: 선택1
    B: 선택2
    C: 선택3
    D: 옵션가
    E: 재고수량
    F: 관리코드
    G: 사용여부
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from combinator import CombinationRow


# 헤더 컬럼 순서 (네이버 형식)
HEADER_COLUMNS = ["선택1", "선택2", "선택3", "옵션가", "재고수량", "관리코드", "사용여부"]


def write_excel(
    rows: List[CombinationRow],
    result_dir: str,
    logger: logging.Logger
) -> str:
    """
    조합 결과를 엑셀 파일로 저장하고 파일 경로를 반환합니다.

    파일명은 'naver_options_YYYYMMDD_HHMMSS.xlsx' 형식으로 생성됩니다.

    Args:
        rows (List[CombinationRow]): 엑셀에 기록할 행 데이터 리스트
        result_dir (str): 결과 파일을 저장할 디렉토리 경로
        logger (logging.Logger): 로거 인스턴스

    Returns:
        str: 저장된 엑셀 파일의 전체 경로

    Raises:
        OSError: 파일 저장 중 오류 발생 시
    """
    logger.info("엑셀 파일 생성 시작")

    # result 디렉토리가 없으면 생성
    os.makedirs(result_dir, exist_ok=True)

    # 타임스탬프 기반 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"naver_options_{timestamp}.xlsx"
    file_path = os.path.join(result_dir, filename)

    # 새 워크북 생성
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "네이버옵션"

    # 헤더 스타일 정의
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(fill_type="solid", fgColor="2E75B6")  # 네이버 파란색 계열
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # ── 1행: 헤더 작성 ──
    for col_idx, col_name in enumerate(HEADER_COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    logger.debug("헤더 행 작성 완료")

    # 데이터 행 스타일
    data_alignment_center = Alignment(horizontal="center", vertical="center")
    data_alignment_left = Alignment(horizontal="left", vertical="center")

    # ── 2행부터: 데이터 작성 ──
    for row_idx, row_data in enumerate(rows, start=2):
        # 교대 행 배경색 (흰색 / 연한 회색)
        if row_idx % 2 == 0:
            row_fill = PatternFill(fill_type="solid", fgColor="F2F2F2")
        else:
            row_fill = PatternFill(fill_type="solid", fgColor="FFFFFF")

        for col_idx, col_name in enumerate(HEADER_COLUMNS, start=1):
            value = row_data.get(col_name, "")

            # None 값은 빈 문자열로 변환 (관리코드 등)
            if value is None:
                value = ""

            # 옵션가, 재고수량은 숫자형 그대로 저장
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border
            cell.fill = row_fill

            # 정렬: 옵션명(선택1~3)은 왼쪽, 나머지는 가운데
            if col_name in ("선택1", "선택2", "선택3"):
                cell.alignment = data_alignment_left
            else:
                cell.alignment = data_alignment_center

    logger.debug(f"데이터 {len(rows)}행 작성 완료")

    # ── 열 너비 자동 조정 ──
    _auto_fit_columns(ws, logger)

    # ── 파일 저장 ──
    wb.save(file_path)
    logger.info(f"엑셀 파일 저장 완료: {file_path}")
    logger.info(f"  - 총 {len(rows)}개 조합 기록")
    logger.info(f"  - 헤더: {HEADER_COLUMNS}")

    return file_path


def _auto_fit_columns(ws, logger: logging.Logger) -> None:
    """
    워크시트의 각 열 너비를 내용에 맞게 자동 조정합니다.

    한글 문자는 영문자보다 넓으므로 추가 여유 너비를 적용합니다.

    Args:
        ws: openpyxl 워크시트 객체
        logger (logging.Logger): 로거 인스턴스
    """
    for col_cells in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col_cells[0].column)

        for cell in col_cells:
            if cell.value is not None:
                cell_str = str(cell.value)
                # 한글은 2바이트 문자이므로 길이 가중치 적용
                length = sum(2 if ord(c) > 127 else 1 for c in cell_str)
                if length > max_length:
                    max_length = length

        # 최소 너비 8, 여유 2 추가
        adjusted_width = max(max_length + 2, 8)
        ws.column_dimensions[col_letter].width = adjusted_width

    logger.debug("열 너비 자동 조정 완료")
