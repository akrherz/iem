"""Update The Test Database.

The test database instance for CI has static data for testing.  This is static
from the time of the docker image build.  This script runs from GHA and does
some mucking with the database to improve coverage.

"""

from pyiem.database import sql_helper, with_sqlalchemy_conn
from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("id3b")
def ldm_product_log(conn: Connection = None) -> None:
    """Update these to the future."""
    conn.execute(
        sql_helper("""
    update ldm_product_log SET
    entered_at = now() - ('2024-12-03 19:30+00'::timestamptz - entered_at),
    valid_at = now() - ('2024-12-03 19:30+00'::timestamptz - valid_at),
    wmo_valid_at = now() -
    ('2024-12-03 19:30+00'::timestamptz - wmo_valid_at)
    where entered_at between '2024-12-03 16:00+00'
    and '2024-12-03 20:00+00'
""")
    )
    conn.commit()


def main():
    """Go Main."""
    ldm_product_log()


if __name__ == "__main__":
    main()
