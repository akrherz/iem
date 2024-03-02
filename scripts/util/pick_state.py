"""Pick a state to run."""

import datetime

from pyiem.reference import state_names


def main():
    """Go."""
    states = list(state_names.keys())
    states.sort()
    doy = int(datetime.date.today().strftime("%j"))
    print(states[doy % len(states)])


if __name__ == "__main__":
    main()
