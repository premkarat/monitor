monitor
=======

Basic remote monitoring tool.

monitor daemon connects to a remote host at every interval and collects the following information

* Total number of processes running in the system and the increase/decrease of the process count since the last monitoring.
* Top 5 processes by memory usage (list pid of the process, memory consumed and complete command line for the process). 
* Percentage disk space usage in /var partition and the change since last monitoring round.
* Check the new contents of syslog for the keyword "ERROR" (case insensitive) since the last monitoring round.

Requirements
============

python-pip package should be availble on the target machine.

If not, download get-pip.py from
    https://bootstrap.pypa.io/get-pip.py

Install it by running::

    $ python get-pip.py

This will install pip on the target machine.

Deploy
======

Basic steps::

    1. git clone https://github.com/premkarat/monitor.git 
    2. cd monitor
    3. pip install -r requirements.txt

Running monitor
===============

    monitor <host-ip> <interval>

    host-ip: Valid IPv4 address
    interval: in seconds (greater than 0)

Example::

    monitor.py 192.168.1.1 60

Monitor result log 
==================

monitor log is available under::

    monitor.log

License 
=======

This project is licensed under the MIT License

Authors 
=======

* Prem Karat [prem(dot)karat(at)gmail(dot)com]
