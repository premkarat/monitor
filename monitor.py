#!/usr/bin/python
# Author: Prem Karat [prem.karat@gmail.com]
# MIT License


import socket
import sys


def usage():
    print("Usage:")
    print("\t montior.py <host-ip> <interval>\n")
    print("\t <host-ip>: Valid IPv4 address")
    print("\t <interval>: in seconds. Minimum 1 sec")


def parse_args():
    if len(sys.argv) != 3:
        usage()
        raise SystemExit("Invalid Usage")

    ipaddr = sys.argv[1]
    interval = sys.argv[2]

    try:
        socket.inet_pton(socket.AF_INET, ipaddr)
    except socket.error:
        usage()
        raise SystemExit('Invalid IP address')

    try:
        interval = int(interval)
    except ValueError:
        usage()
        raise SystemExit('Invalid interval')
    if not interval:
        usage()
        raise SystemExit('Interval should be miminum 1 second')


def main():
    parse_args()


if __name__ == '__main__':
    main()
