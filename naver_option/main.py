# =============================================================================
# 파일명: main.py
# 목적: 네이버 옵션 조합 생성 프로그램의 메인 실행 파일
# 작성일: 2026-05-10
# 버전: 1.0.0
# =============================================================================

"""
네이버 옵션 조합 생성 프로그램 메인 모듈

실행 흐름:
    1. 로거 초기화
    2. data/data.txt 파일 파싱
    3. 옵션 조합 생성
    4. result/ 디렉토리에 엑셀 파일 저장
    5. 실행 결과 출력
"""

import os
import sys

# PyInstaller --onefile 빌드 및 일반 실행 모두 대응
# 실행 파일(EXE) 기준 경로와 스크립트 기준 경로를 모두 sys.path에 추가
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 EXE 실행 시
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 일반 python 실행 시
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 루트 디렉토리를 sys.path 최우선으로 추가
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from logger import setup_logger
from parser import parse_data_file
from combinator import generate_combinations
from excel_writer import write_excel


# ── 경로 상수 ──
DATA_PATH = os.path.join(BASE_DIR, "data", "data.txt")
RESULT_DIR = os.path.join(BASE_DIR, "result")
LOG_DIR = BASE_DIR  # log.txt는 프로그램 루트에 저장


def main() -> None:
    """
    프로그램 메인 진입점.

    data/data.txt를 읽어 옵션 조합을 생성하고
    result/ 폴더에 엑셀 파일로 저장합니다.
    오류 발생 시 로그에 기록하고 프로그램을 종료합니다.
    """
    # ── Step 1: 로거 초기화 ──
    logger = setup_logger(LOG_DIR)

    try:
        # ── Step 2: 데이터 파일 파싱 ──
        logger.info(f"데이터 파일 경로: {DATA_PATH}")
        option_groups = parse_data_file(DATA_PATH, logger)

        logger.info(f"파싱 완료 - 옵션 그룹 수: {len(option_groups)}개")
        for i, group in enumerate(option_groups, start=1):
            logger.info(f"  [선택{i}] {len(group)}개 항목")
            for name, price in group:
                logger.info(f"    - {name} / {price:,}원")

        # ── Step 3: 옵션 조합 생성 ──
        rows = generate_combinations(option_groups, logger)

        # ── Step 4: 엑셀 파일 저장 ──
        output_path = write_excel(rows, RESULT_DIR, logger)

        # ── Step 5: 최종 결과 출력 ──
        logger.info("=" * 60)
        logger.info("✔ 프로그램 실행 완료")
        logger.info(f"  옵션 그룹 수  : {len(option_groups)}개")
        logger.info(f"  총 조합 수    : {len(rows)}개")
        logger.info(f"  저장 파일     : {output_path}")
        logger.info("=" * 60)

        print("\n" + "=" * 60)
        print("  네이버 옵션 조합 생성 완료!")
        print(f"  옵션 그룹 수 : {len(option_groups)}개")
        print(f"  총 조합 수   : {len(rows)}개")
        print(f"  저장 위치    : {output_path}")
        print("=" * 60 + "\n")

    except FileNotFoundError as e:
        # 데이터 파일 없음
        logger.error(f"파일 없음 오류: {e}")
        print(f"\n[오류] 파일을 찾을 수 없습니다:\n{e}\n")
        sys.exit(1)

    except ValueError as e:
        # 데이터 형식 오류
        logger.error(f"데이터 형식 오류: {e}")
        print(f"\n[오류] 데이터 형식이 올바르지 않습니다:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        # 그 외 예상치 못한 오류
        logger.exception(f"예상치 못한 오류 발생: {e}")
        print(f"\n[오류] 예상치 못한 오류가 발생했습니다:\n{e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
