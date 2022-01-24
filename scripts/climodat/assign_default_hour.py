"""Sample obs to see what our default times are."""

# Third party
import pandas as pd
from pyiem.util import get_dbconn, get_dbconnstr, logger

LOG = logger()


def main():
    """Go Main Go."""
    df = pd.read_sql(
        "SELECT iemid, id, temp24_hour, precip24_hour from stations WHERE "
        "network ~* 'CLIMATE' and (temp24_hour is null or "
        "precip24_hour is null) ORDER by id ASC",
        get_dbconnstr("mesosite"),
        index_col="id",
    )
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()
    for col in ["temp24_hour", "precip24_hour"]:
        for sid, row in df[pd.isna(df[col])].iterrows():
            df2 = pd.read_sql(
                f"SELECT {col.replace('24', '')} as datum, count(*), "
                f"min(day), max(day) from alldata_{sid[:2]} WHERE "
                f"{col.replace('24', '')} is not null and "
                f"{col.replace('24_hour', '')}_estimated = 'f' GROUP by datum "
                "ORDER by count DESC",
                get_dbconnstr("coop"),
                index_col=None,
            )
            if df2.empty:
                continue
            newval = int(df2.iloc[0]["datum"])
            LOG.info("Setting %s for %s to %s", col, sid, newval)
            mcursor.execute(
                f"UPDATE stations SET {col} = %s WHERE iemid = %s",
                (newval, row["iemid"]),
            )
    mcursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
