"""Comparables to include/imagemaps.php"""


def rectify_wfo(wfo3):
    """Convert three char to four char WFO."""
    if wfo3 in ["GUM", "HFO", "AFG", "AJK", "AFC"]:
        return f"P{wfo3}"
    if wfo3 in ["JSJ", "SJU"]:
        return "TJSJ"
    return f"K{wfo3}"


def unrectify_wfo(wfo4):
    """Convert four char to three char WFO."""
    if wfo4 in ["PGUM", "PHFO", "PAFG", "PAJK", "PAFC"]:
        return wfo4[1:]
    if wfo4 in ["TJSJ", "TSJU"]:
        return "JSJ"
    return wfo4[1:]
