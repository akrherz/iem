"""iemweb utility functions."""

from datetime import datetime


def month2months(month: str) -> list[int]:
    """
    Convert a month string to a list of months.

    Args:
        month (str): A month string commonly used by IEM apps

    Returns:
        list: A list of ints (months)
    """
    if month in ["all", "water_year"]:
        months = list(range(1, 13))
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "octmar":
        months = [10, 11, 12, 1, 2, 3]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "spring2":
        months = [4, 5, 6]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "gs":
        months = [5, 6, 7, 8, 9]
    elif month == "mjj":
        months = [5, 6, 7]
    else:
        fmt = "%b" if len(month) == 3 else "%m"
        months = [datetime.strptime(f"2000-{month}-01", f"%Y-{fmt}-%d").month]
    return months
