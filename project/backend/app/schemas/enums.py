from enum import Enum

class DealStatus(str, Enum):
    NEW = "new"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
