"""Opinionated script to combine apache access logs into a single file.

1. It takes a list of log files as input.
2. One of the click based arguments is --output or -o which is the output file.
3. The script will combine the logs into a single file.
4. It simultaneously iterates over all files and takes entries are found and
   to keep the result in order.
5. If a timestamp is found in the "past", it is updated to use the current
   time being interated on.
6. The script then reports the results of how many lines were found in each
   file and how many had their timestamps updated.
"""

import os
from datetime import datetime

import click
from tqdm import tqdm


def replace_timestamp(log_line: str, dt: datetime) -> str:
    """Replace the timestamp in the log line with the given datetime."""
    timestamp_str = log_line.split("[")[1].split("]")[0]
    new_timestamp = dt.strftime("%d/%b/%Y:%H:%M:%S %z")
    return log_line.replace(timestamp_str, new_timestamp)


def extract_timestamp(log_line) -> datetime:
    """Extract timestamp from a log line. Assumes Apache log format."""
    try:
        # Example  [10/Oct/2000:13:55:36 -0700]
        timestamp_str = log_line.split("[")[1].split("]")[0]
        return datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
    except (IndexError, ValueError) as exp:
        msg = f"Could not extract timestamp from log line: {log_line}"
        raise ValueError(msg) from exp


def processor(progress, outfp, log_iters):
    """Do the work."""
    counters = {
        "hardcoded_timestamps": 0,
    }
    # First line of each log file
    first_lines = []
    for logi in log_iters:
        line = logi.readline()
        first_lines.append((extract_timestamp(line), line))
    current_time = min(x[0] for x in first_lines)
    deffered = []
    for dt, line in first_lines:
        if dt == current_time:
            outfp.write(line)
        else:
            deffered.append((dt, line))

    # Iterate over all log files
    while True:
        for logi in log_iters:
            while True:
                line = logi.readline()
                if not line:
                    break
                try:
                    dt = extract_timestamp(line)
                except ValueError:
                    # Skip lines that do not have a valid timestamp
                    continue
                if dt == current_time:
                    progress.update(1)
                    outfp.write(line)
                elif dt < current_time:
                    # Replace timestamp with current time
                    counters["hardcoded_timestamps"] += 1
                    progress.update(1)
                    outfp.write(replace_timestamp(line, current_time))
                else:
                    # Defer this line for later
                    deffered.append((dt, line))
                    break
        # Find the new minimum timestamp within the deferred lines
        if not deffered:
            break
        deffered.sort(key=lambda x: x[0])
        current_time = deffered[0][0]
        # Write and remove all lines with the current time
        for dt, line in deffered:
            if dt == current_time:
                progress.update(1)
                outfp.write(line)
                deffered.remove((dt, line))

    # Print the counters
    print(f"Lines with hardcoded time: {counters['hardcoded_timestamps']}")


@click.command()
@click.argument("log_files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Output file to write combined logs.",
)
def combine_logs(log_files, output):
    """Combine Apache access logs into a single file."""
    log_iters = []

    # Open all log files and create iterators
    for log_file in log_files:
        log_iters.append(open(log_file))  # noqa

    progress = tqdm(disable=not os.isatty(0))

    with open(output, "w") as outfp:  # skipcq
        processor(progress, outfp, log_iters)

    # Close all log files
    for log_iter in log_iters:
        log_iter.close()


if __name__ == "__main__":
    combine_logs()
