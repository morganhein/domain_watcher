#!/bin/python

import json
import requests
import time
import re

from os.path import join, dirname
from os import getenv
from dotenv import load_dotenv
from datetime import datetime
from dateutil import parser


reg = 

class Tester():

    def __init__(self):
        self.expReg = re.compile("(?:expiration|expiry|expires?)[^:]*:\s+(.*)\n", re.IGNORECASE)


    def checkIfAvailable(domain):
        print "Checking domain:", domain
        KEY = getenv("whoapi")
        payload = {'apikey': KEY, 'r': 'whois', 'domain': domain}
        # todo, error checking here that it actually responded with what we need
        whois = requests.get('http://api.whoapi.com', params=payload).json()

        if (whois['status'] == 18):
            print 'Request happened too quickly. Waiting a minute to try again.'
            time.sleep(60)
            return checkIfAvailable(domain)

        if (whois['status'] == 12):
            print "API credentials for the WhoAPI are wrong. Please fix and try again."
            quit()

        if ('date_expires' not in whois):
            print "date_expires not found:", whois
            return False

        if (len(whois['date_expires']) == 0):
            print domain, "has no expiration date."
            return False

        expires = parser.parse(whois['date_expires'])
        if ((expires - datetime.now()).days < 15):
            whois['domain'] = domain
            whois['expires_in'] = (expires - datetime.now()).days
            print domain, "expires in", whois['expires_in']
            return whois

    def sms(whois):
        username = getenv("smsusername")
        password = getenv("smspassword")
        target = getenv("smstarget")
        r = requests.post("http://api.infobip.com/sms/1/text/single", 
            auth=(username, password),
            json=   {
                "from": "InfoSMS",
                "to": target,
                "text":"The domain http://" + whois['domain'] + " expires in " + str(whois['expires_in']) + " days."
            })
        print "SMS response", r.text

    def detectExpiration(data):
        results = reg.search(data)
        if (results == None):
            return False
        if (len(results.group(1)) > 0):
            return results.group(1)
        else:
            return False


def NICTest():
    import NICClient
    nic = NICClient.NICClient()
    # print nic.whois_lookup(None, "resu.me", False)
    # time.sleep(5)
    # print nic.whois_lookup(None, "adon.is", False)
    # time.sleep(5)
    # print nic.whois_lookup(None, "hein.com", False)
    # time.sleep(5)
    # print nic.whois_lookup(None, "braincage.com", False)
    # time.sleep(5)
    # print nic.whois_lookup(None, "ingaming.org", False)
    # time.sleep(5)
    print detectExpiration(nic.whois_lookup(None, "resu.me", False))



def main():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    with open('domains.json') as domains_file:    
        domains = json.load(domains_file)['domains']

    for domain in domains:
        whois = checkIfAvailable(domain)
        if (whois): 
            # sms(whois)
            print "Would be sending SMS, but i'm not."
        else:
            print "Domain unavailable or no expiration date was found."
        print "Sleeping for 60 seconds.\n"
        time.sleep(60)

if __name__ == '__main__':
    # main
    # WhoisTest()
    NICTest()