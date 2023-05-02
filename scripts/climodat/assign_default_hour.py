"""Sample obs to see what our default times are."""

# Third party
import pandas as pd
from pyiem.util import get_dbconn, get_dbconnstr, logger

LOG = logger()


def main():
    """Go Main Go."""
    df = pd.read_sql(
        "SELECT iemid, id, temp24_hour, precip24_hour from stations WHERE "
        "network ~* 'CLIMATE' ORDER by id ASC",
        get_dbconnstr("mesosite"),
        index_col="id",
    )
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()
    for sid, row in df.iterrows():
        for col in ["temp24_hour", "precip24_hour"]:
            df2 = pd.read_sql(
                f"""SELECT {col.replace('24', '')} as datum, count(*),
                min(day), max(day) from alldata_{sid[:2]} WHERE
                station = %s and day > now() - '3 years'::interval and
                {col.replace('24', '')} is not null and
                {col.replace('24_hour', '')}_estimated = 'f' GROUP by datum
                ORDER by count DESC
                """,
                get_dbconnstr("coop"),
                params=(sid,),
                index_col=None,
            )
            if df2.empty:
                continue
            newval = int(df2.iloc[0]["datum"])
            if pd.isna(row[col]) or newval != row[col]:
                LOG.info("Setting %s[%s] %s->%s", sid, col, row[col], newval)
                mcursor.execute(
                    f"UPDATE stations SET {col} = %s WHERE iemid = %s",
                    (newval, row["iemid"]),
                )
    mcursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
