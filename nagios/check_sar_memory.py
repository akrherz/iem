"""Capture some stats from sar memory"""
import subprocess
import sys


def process(res):
    """Parse and do stuff with the output"""
    lines = res.strip().split("\n")
    if len(lines) < 2 or not lines[-1].startswith("Average:"):
        print('CRITICAL: ERROR %s' % ("|".join(lines),))
        sys.exit(2)
    tokens = lines[-1].strip().split()
    print(('OK: Memory free: %s | KBMEMFREE=%s;;;; '
           'KBMEMUSED=%s;;;; MEMUSED=%s;;;; KBBUFFERS=%s;;;; '
           'KBCACHED=%s;;;; KBCOMMIT=%s;;;; COMMIT=%s;;;; '
           'KBACTIVE=%s;;;; KBBINACT=%s;;;; KBDIRTY=%s;;;; '
           ) % (tokens[1], tokens[1], tokens[2], tokens[3], tokens[4],
                tokens[5], tokens[6], tokens[7], tokens[8], tokens[9],
                tokens[10]))
    if float(tokens[1]) < 500000:
        sys.exit(2)
    elif float(tokens[1]) < 1000000:
        sys.exit(1)
    else:
        sys.exit(0)


def main():
    """Do Something"""
    proc = subprocess.Popen("sar -r 1 5", shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout = proc.stdout.read()
    process(stdout)

if __name__ == '__main__':
    main()
