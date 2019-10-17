#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Problem:
    def __init__(self, hostid, hostname, eventid, severity, name="Unknown"):
        self.id = 0                # auto_increment
        self.hostid = hostid
        self.hostname = hostname
        self.affiliate = "Unknown"
        self.eventid = eventid
        self.name = name
        self.severity = int(severity)
        self.message = ""
        self.closed = False
        self.changed = False
        self.openedDateTime = None
        self.closedDateTime = None
        self.setAffiliateByCallback(get_affiliate)

    def open(self, callback):
        self.closed = False
        self.openedDateTime = datetime.datetime.now()
        self.message = "문제 발생: " + " / ".join([self.openedDateTime.strftime("%Y-%m-%d %H:%M:%S"), self.affiliate, self.hostname, self.name])
        callback(self)

    def close(self, callback):
        self.closed = True
        self.closedDateTime = datetime.datetime.now()
        self.message = "문제 해결: " + " / ".join([self.closedDateTime.strftime("%Y-%m-%d %H:%M:%S"), self.affiliate, self.hostname, self.name])
        callback(self)

    def setChanged(self, changed):
        self.changed = changed

    def setAffiliateByCallback(self, callback):
        self.affiliate = callback(self)

def debug():
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)

def changed_problem(p):
    # when closed
    if(p.closed == True):
        send_text(p.message, tel_number, tel_country)
        send_voice(p.message, tel_number, tel_country)
        print("problem closed")
    # when opened
    else:
        send_text(p.message, tel_number, tel_country)
        send_voice(p.message, tel_number, tel_country)
        print("problem opened")

    # save problems
    save_problems()

def send_text(message, to, country):
    if(is_allow_text == False):
        print("Prevented to send text message");
        return

    data = {
       "action": "text",
       "message": message,
       "to": to,
       "country": country
    }
    headers = {"Content-Type": "application/json; charset=utf8"}
    res = requests.post("http://gw.local/?route=api.twilio", headers=headers, data=json.dumps(data))
    print(res.content)
    return res

def send_voice(message, to, country):
    if(is_allow_voice == False):
        print("Prevented to send voice message");
        return

    data = {
       "action": "voice",
       "message": message,
       "to": to,
       "country": country
    }
    headers = {"Content-Type": "application/json; charset=utf8"}
    res = requests.post("http://gw.local/?route=api.twilio", headers=headers, data=json.dumps(data))
    print(res.content)
    return res

def get_affiliate(p):
    return "Unknown"

def save_problems():
    try:
        with open("problems.json", "wb") as f:
            pickle.dump(problems, f)
    except:
        print("Could not load current problems")

def load_problems():
    problems = []

    try:
        with open("problems.json", "rb") as f:
            problems = pickle.load(f)
    except:
        print("Colud not load previous problems")

    return problems

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
        hostname = h['host']
        for p in zapi.problem.get(output="extend", hostids=[hostid]):
            eventids.append(p['eventid'])
            add_problem(Problem(hostid, hostname, p['eventid'], p['severity'], p['name']))

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
        time.sleep(5)

if __name__ == '__main__':
    import sys
    import logging
    import time
    import datetime
    from pyzabbix import ZabbixAPI
    import pickle
    import requests
    import json

    # problem list
    problems = load_problems()

    # allow text/voice
    is_allow_text = True
    is_allow_voice = True

    # telephone
    tel_number = "01049157829"
    tel_country = 82

    # authenticate to zabbix API
    zapi = ZabbixAPI("http://zbx.local/zabbix")
    zapi.login("Admin", "zabbix")
    print("Connected to Zabbix API Version %s" % zapi.api_version())

    #debug()
    sys.exit(main(sys.argv))
