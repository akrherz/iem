"""Pick a state to run."""

from datetime import date

from pyiem.reference import state_names


def main():
    """Go."""
    states = list(state_names.keys())
    states.sort()
    doy = date.today().timetuple().tm_yday
    print(states[doy % len(states)])


if __name__ == "__main__":
    main()
