"""
process the output of ldmadmin printmetrics

getTime(), getLoad(), getPortCount(), getPq(), getCpu()

20121019.190728   date -u +%Y%m%d.%H%M%S
1.35 2.01 2.24    last three vals of `uptime`
49 8              downstream hosts, upstream hosts
3699 230388 7999874360  queue age, product count, byte count
21 2 77 0           $userTime, $sysTime, $idleTime, $waitTime,
49104080e3 305612e3 438048e3 $memUsed, $memFree, $swapUsed,
24137944e3 21514 $swapFree, $contextSwitches

"""
import subprocess
import sys


def main():
    proc = subprocess.Popen("/home/ldm/bin/ldmadmin printmetrics", shell=True,
                            stdout=subprocess.PIPE)
    data = proc.stdout.read()
    tokens = data.split()
    if len(tokens) != 18:
        print 'CRITICAL - can not parse output %s ' % (data,)
        sys.exit(2)

    downstream = tokens[4]
    upstream = int(tokens[5])
    queue_age = tokens[6]
    product_count = tokens[7]
    byte_count = tokens[8]

    msg = 'OK'
    estatus = 0
    if upstream < 0:
        msg = 'CRITICAL'
        estatus = 2
    print(("%s - Down:%s Up:%s Raw:%s| downstream=%s;; upstream=%s;; "
           "queue_age=%s;; product_count=%s;; byte_count=%s"
           ) % (msg, downstream, upstream, data,
                downstream, upstream, queue_age,
                product_count, byte_count))
    sys.exit(estatus)

if __name__ == '__main__':
    main()
