#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Problem:
    def __init__(self, eventid, severity, name="Unknown"):
        self.id = 0                # auto_increment
        self.eventid = eventid
        self.name = name
        self.severity = severity
        self.closed = False
        self.startDateTime = None
        self.closedDateTime = None

    def open(self, callback):
        self.closed = False
        self.startDateTime = datetime.datetime.now()
        callback(self)
        print("problem opened: " + self.name + " @ " + self.startDateTime.strftime("%m/%d/%Y, %H:%M:%S"))

    def close(self, callback):
        self.closed = True
        self.closedDateTime = datetime.datetime.now()
        callback(self)
        print("problem closed: " + self.name + " @ " + self.closedDateTime.strftime("%m/%d/%Y, %H:%M:%S"))

def debug():
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)

def changed_problem(p):
    # when closed
    if(p.closed == True):
        print("notify problem closed: phone and text message")
    # when opened
    else:
        print("notify problem opened: phone and text message")

def add_problem(_p):
    # check previous problems
    for p in problems:
        if(p.eventid == _p.eventid):
            return

    # if not exists in previous problems, add new problem
    _p.open(changed_problem)
    problems.append(_p)

def get_next_problems():
    eventids = []

    for h in zapi.host.get(output="extend"):
        hostid = h['hostid']
        for p in zapi.problem.get(output="extend", hostids=[hostid]):
            eventids.append(p['eventid'])
            add_problem(Problem(p['eventid'], p['severity'], p['name']))

    return eventids

def get_previous_problems():
    eventids = []
    for p in problems:
        eventids.append(p.eventid)
    return eventids
    
def work():
    x1 = get_next_problems()
    x2 = get_previous_problems()
    eventids = list(set(x2) - set(x1))

    # remove and close when ended problem
    for eventid in eventids:
        for p in problems:
            if(p.eventid == eventid):
                p.close(changed_problem)
                problems.remove(p)

def main(args):
    while(True):
        work()

        # next step by 2 seconds
        time.sleep(2)

if __name__ == '__main__':
    import sys
    import logging
    import time
    import datetime
    from pyzabbix import ZabbixAPI

    # problem list
    problems = []

    # authenticate to zabbix API
    zapi = ZabbixAPI("http://localhost/zabbix")
    zapi.login("Admin", "zabbix")
    print("Connected to Zabbix API Version %s" % zapi.api_version())

    #debug()
    sys.exit(main(sys.argv))
