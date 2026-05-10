# =============================================================================
# 파일명: logger.py
# 목적: 프로그램 실행 로그를 콘솔 및 log.txt 파일에 기록하는 모듈
# 작성일: 2026-05-10
# 버전: 1.0.0
# =============================================================================

"""
로깅 모듈

프로그램 실행 과정, 처리 결과, 오류 내용을 
콘솔과 log.txt 파일에 동시에 기록합니다.
"""

import logging
import os
from datetime import datetime


def setup_logger(log_dir: str) -> logging.Logger:
    """
    로거를 초기화하고 반환합니다.

    콘솔 핸들러와 파일 핸들러를 모두 등록하여
    실행 로그가 콘솔과 log.txt에 동시에 출력됩니다.

    Args:
        log_dir (str): log.txt 파일을 저장할 디렉토리 경로

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger("naver_option")
    logger.setLevel(logging.DEBUG)

    # 이미 핸들러가 등록된 경우 중복 방지
    if logger.handlers:
        logger.handlers.clear()

    # 로그 포맷: [타임스탬프] 레벨 - 메시지
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 핸들러 (INFO 이상 출력)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 파일 핸들러 (DEBUG 이상 저장, log.txt)
    log_path = os.path.join(log_dir, "log.txt")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("=" * 60)
    logger.info("네이버 옵션 조합 생성 프로그램 시작")
    logger.info(f"로그 파일 경로: {log_path}")
    logger.info("=" * 60)

    return logger
