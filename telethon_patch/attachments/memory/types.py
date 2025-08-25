from enum import StrEnum


class SpamblockType(StrEnum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    FREE = "free"


class Types:
    spamblock_type = SpamblockType
