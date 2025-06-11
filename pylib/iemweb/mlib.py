"""Comparables to include/mlib.php"""


def rectify_wfo(wfo: str):
    """Convert three char to four char WFO."""
    if len(wfo) == 4:
        return wfo
    if wfo in ["GUM", "HFO", "AFG", "AJK", "AFC"]:
        return f"P{wfo}"
    if wfo in ["JSJ", "SJU"]:
        return "TJSJ"
    return f"K{wfo}"


def unrectify_wfo(wfo: str):
    """Convert four char to three char WFO."""
    if len(wfo) == 3:
        return wfo
    if wfo in ["PGUM", "PHFO", "PAFG", "PAJK", "PAFC"]:
        return wfo[1:]
    if wfo in ["TJSJ", "TSJU"]:
        return "JSJ"
    return wfo[1:]
