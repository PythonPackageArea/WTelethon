import logging
import sys


def setup_service_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("service.log", encoding="utf-8"),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
