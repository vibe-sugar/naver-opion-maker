# =============================================================================
# 파일명: combinator.py
# 목적: 파싱된 옵션 그룹들의 모든 조합(카테시안 곱)을 생성하는 모듈
# 작성일: 2026-05-10
# 버전: 1.0.0
# =============================================================================

"""
옵션 조합 생성 모듈

파싱된 옵션 그룹 리스트를 받아 모든 가능한 조합(카테시안 곱)을 생성합니다.

예시:
    옵션 그룹 1: [("마이쮸 1개 #099*01", 7000), ("참크래커 1개 #099*01", 7500)]
    옵션 그룹 2: [("오레오 1개 #A01", 5000), ("칙촉 1개 #B02", 6000)]
    옵션 그룹 3: [("포카칩 1개 #C03", 3000)]

    조합 결과 (2 × 2 × 1 = 4가지):
        ("마이쮸...", "오레오...", "포카칩...", 15000)
        ("마이쮸...", "칙촉...",  "포카칩...", 16000)
        ("참크래커...", "오레오...", "포카칩...", 15500)
        ("참크래커...", "칙촉...",  "포카칩...", 16500)
"""

import logging
from itertools import product
from typing import List, Tuple, Dict, Any

from src.parser import OptionGroup


# 조합 결과 행: 선택1, 선택2, 선택3, 옵션가, 재고수량, 관리코드, 사용여부
CombinationRow = Dict[str, Any]

# 고정값
STOCK_QUANTITY = 1000
MANAGEMENT_CODE = ""
USE_YN = "Y"


def generate_combinations(
    option_groups: List[OptionGroup],
    logger: logging.Logger
) -> List[CombinationRow]:
    """
    옵션 그룹들의 모든 조합을 생성하고 결과 행 리스트를 반환합니다.

    옵션가는 각 조합에서 선택된 항목들의 가격 합산입니다.
    선택2, 선택3은 옵션 그룹 수에 따라 빈 문자열로 처리됩니다.

    Args:
        option_groups (List[OptionGroup]): 파싱된 옵션 그룹 리스트 (1~3개)
        logger (logging.Logger): 로거 인스턴스

    Returns:
        List[CombinationRow]: 엑셀에 기록할 행 데이터 리스트
            각 행: {
                "선택1": str,
                "선택2": str,
                "선택3": str,
                "옵션가": int,
                "재고수량": int,
                "관리코드": str,
                "사용여부": str
            }
    """
    logger.info("옵션 조합 생성 시작")
    logger.info(f"옵션 그룹 수: {len(option_groups)}개")

    # 각 그룹의 항목 수 출력
    for i, group in enumerate(option_groups, start=1):
        names = [name for name, _ in group]
        logger.info(f"  선택{i} 항목: {names}")

    # itertools.product로 카테시안 곱 계산
    # 각 그룹의 (옵션명, 가격) 튜플 리스트를 인자로 전달
    all_combinations = list(product(*option_groups))

    logger.info(f"생성된 총 조합 수: {len(all_combinations)}개")

    rows: List[CombinationRow] = []

    for combo in all_combinations:
        # combo 예시 (3그룹): (("마이쮸...", 7000), ("오레오...", 5000), ("포카칩...", 3000))
        # combo 예시 (2그룹): (("마이쮸...", 7000), ("오레오...", 5000))

        # 각 그룹에서 선택된 옵션명과 가격 추출
        names = [item[0] for item in combo]   # 옵션명 리스트
        prices = [item[1] for item in combo]  # 가격 리스트

        # 옵션가: 선택된 항목 가격의 합산
        total_price = sum(prices)

        # 선택1~3을 최대 3개까지 채우고, 부족한 경우 빈 문자열로 패딩
        sel1 = names[0] if len(names) > 0 else ""
        sel2 = names[1] if len(names) > 1 else ""
        sel3 = names[2] if len(names) > 2 else ""

        row: CombinationRow = {
            "선택1": sel1,
            "선택2": sel2,
            "선택3": sel3,
            "옵션가": total_price,
            "재고수량": STOCK_QUANTITY,
            "관리코드": MANAGEMENT_CODE,
            "사용여부": USE_YN,
        }
        rows.append(row)

        logger.debug(
            f"  조합: [{sel1}] / [{sel2}] / [{sel3}] "
            f"→ 옵션가: {total_price:,}원"
        )

    logger.info(f"옵션 조합 생성 완료 - 총 {len(rows)}개 행 생성")
    return rows
