"""Do some self diagnostics on NWSLI / DCP metadata"""
from __future__ import print_function
from pyiem.reference import nwsli2country, nwsli2state
from pyiem.util import get_dbconn


def main():
    """Go Main"""
    dbconn = get_dbconn("mesosite", user="nobody")
    cursor = dbconn.cursor()

    cursor.execute(
        """
        SELECT id, state, country, network from stations
        WHERE network ~* 'DCP' and length(id) = 5"""
    )

    for row in cursor:
        nwsli = row[0]
        state = row[1]
        country = row[2]
        network = row[3]
        code = nwsli[-2:]

        country2 = nwsli2country.get(code)
        if country != country2:
            print(
                ("ID:%s ST:%s C:%s NET:%s L_C:%s")
                % (nwsli, state, country, network, country2)
            )
        network2 = "%s_DCP" % (state,)
        if country in ["MX", "CA"]:
            network2 = "%s_%s_DCP" % (country, state)
        elif country not in ["MX", "CA", "US"]:
            network2 = "%s__DCP" % (country,)
        if network != network2:
            print(
                ("ID:%s ST:%s C:%s NET:%s L_N:%s")
                % (nwsli, state, country, network, network2)
            )

        state2 = nwsli2state.get(code)
        if state is not None and state != state2:
            print(
                ("ID:%s ST:%s C:%s NET:%s L_S:%s")
                % (nwsli, state, country, network, state2)
            )


if __name__ == "__main__":
    main()
