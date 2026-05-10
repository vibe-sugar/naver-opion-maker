# =============================================================================
# 파일명: parser.py
# 목적: data 디렉토리의 텍스트 파일을 읽어 옵션 데이터를 파싱하는 모듈
# 작성일: 2026-05-10
# 버전: 1.0.0
# =============================================================================

"""
데이터 파싱 모듈

data/input.txt 파일을 읽어 옵션 그룹과 각 옵션 항목(이름, 가격)을 파싱합니다.

input.txt 형식:
    - 각 줄 = 하나의 옵션 그룹 (선택1, 선택2, 선택3 순서)
    - 한 줄 안에서 여러 항목은 쉼표(,)로 구분
    - 각 항목 형식: 옵션명$가격
    - 옵션 그룹은 최소 1개, 최대 3개 (빈 줄 무시)

예시:
    마이쮸 1개 #099*01$7000, 참크래커 1개 #099*01$7500
    오레오 1개 #A01$5000, 칙촉 1개 #B02$6000
"""

import os
import logging
from typing import List, Tuple


# 각 옵션 항목: (옵션명, 가격)
OptionItem = Tuple[str, int]
# 옵션 그룹: 여러 항목의 리스트
OptionGroup = List[OptionItem]


def parse_data_file(data_path: str, logger: logging.Logger) -> List[OptionGroup]:
    """
    data.txt 파일을 읽어 옵션 그룹 리스트를 반환합니다.

    Args:
        data_path (str): data.txt 파일의 전체 경로
        logger (logging.Logger): 로거 인스턴스

    Returns:
        List[OptionGroup]: 옵션 그룹 리스트
            예) [
                  [("마이쮸 1개 #099*01", 7000), ("참크래커 1개 #099*01", 7500)],
                  [("오레오 1개 #A01", 5000)],
                ]

    Raises:
        FileNotFoundError: data.txt 파일이 존재하지 않을 때
        ValueError: 형식 오류 또는 옵션 그룹이 4개 이상일 때
    """
    logger.info(f"데이터 파일 읽기 시작: {data_path}")

    # 파일 존재 여부 확인
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"data.txt 파일을 찾을 수 없습니다: {data_path}\n"
            "data 폴더 안에 data.txt 파일을 생성해주세요."
        )

    with open(data_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    logger.debug(f"파일 읽기 완료 - 전체 줄 수: {len(raw_lines)}")

    # 빈 줄 제거 후 유효 줄만 추출
    lines = [line.strip() for line in raw_lines if line.strip()]
    logger.info(f"유효 옵션 그룹 수: {len(lines)}")

    # 옵션 그룹 개수 검증 (1~3개)
    if len(lines) == 0:
        raise ValueError("input.txt 파일에 유효한 데이터가 없습니다. 최소 1개의 옵션 그룹을 작성해주세요.")
    if len(lines) > 3:
        raise ValueError(
            f"옵션 그룹은 최대 3개까지 등록 가능합니다. (현재: {len(lines)}개)\n"
            "input.txt에서 4번째 줄 이후를 제거해주세요."
        )

    option_groups: List[OptionGroup] = []

    for group_idx, line in enumerate(lines, start=1):
        logger.debug(f"옵션 그룹 {group_idx} 파싱 중: {line}")
        group = _parse_option_group(line, group_idx, logger)
        option_groups.append(group)
        logger.info(f"옵션 그룹 {group_idx} 파싱 완료 - 항목 수: {len(group)}개")
        for item_name, item_price in group:
            logger.debug(f"  항목: '{item_name}' / 가격: {item_price:,}원")

    return option_groups


def _parse_option_group(line: str, group_idx: int, logger: logging.Logger) -> OptionGroup:
    """
    한 줄의 텍스트를 파싱하여 옵션 항목 리스트를 반환합니다.

    Args:
        line (str): 파싱할 줄 문자열
        group_idx (int): 옵션 그룹 번호 (오류 메시지용)
        logger (logging.Logger): 로거 인스턴스

    Returns:
        OptionGroup: [(옵션명, 가격), ...] 리스트

    Raises:
        ValueError: '$' 구분자가 없거나 가격이 숫자가 아닐 때
    """
    group: OptionGroup = []

    # 쉼표로 여러 항목 분리
    raw_items = line.split(",")

    for raw_item in raw_items:
        item = raw_item.strip()
        if not item:
            continue  # 공백 항목 무시

        # '$'를 기준으로 옵션명과 가격 분리
        if "$" not in item:
            raise ValueError(
                f"옵션 그룹 {group_idx}에서 형식 오류: '{item}'\n"
                "형식은 '옵션명$가격' 이어야 합니다. (예: 마이쮸 1개 #099*01$7000)"
            )

        # 마지막 '$' 기준으로 분리 (옵션명에 '$'가 포함될 경우 대비)
        last_dollar = item.rfind("$")
        option_name = item[:last_dollar].strip()
        price_str = item[last_dollar + 1:].strip()

        # 옵션명 유효성 검사
        if not option_name:
            raise ValueError(
                f"옵션 그룹 {group_idx}에서 옵션명이 비어있습니다: '{item}'"
            )

        # 가격 숫자 변환
        try:
            # 쉼표가 포함된 가격 처리 (예: 7,000 → 7000)
            price = int(price_str.replace(",", ""))
        except ValueError:
            raise ValueError(
                f"옵션 그룹 {group_idx}에서 가격 형식 오류: '{price_str}'\n"
                "가격은 숫자여야 합니다. (예: 7000)"
            )

        group.append((option_name, price))

    if not group:
        raise ValueError(f"옵션 그룹 {group_idx}에 유효한 항목이 없습니다.")

    return group
