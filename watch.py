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
from socket import error
import NICClient

class Tester():

    def __init__(self):
        self.expReg = re.compile("(?:expiration|expiry|expires?)[^:]*:\s?(.*)\n", re.IGNORECASE)
        self.whois = NICClient.NICClient()

    def runCheck(self, domain):
        availability = self.checkIfAvailable(domain)
        if (availability):
            self.sms(availability)

    def checkIfAvailable(self, domain):
        print "Checking domain:", domain
        try:
            expires = self.detectExpiration(self.whois.whois_lookup(None, domain, False))
        except socket.error:
            print "Socket error retrieving information for domain", domain
            return False

        if (expires == False):
            print "No information on", domain
            return False

        expires = parser.parse(expires, None, ignoretz=True)

        expires_in  = (expires - datetime.now(None)).days
        print domain, "expires in", expires_in, "days"
        
        if (expires_in < 15):
            return {"domain": domain, "expires_in": expires_in}

    def sms(self, data):
        username = getenv("smsusername")
        password = getenv("smspassword")
        target = getenv("smstarget")
        r = requests.post("http://api.infobip.com/sms/1/text/single", 
            auth=(username, password),
            json=   {
                "from": "InfoSMS",
                "to": target,
                "text":"The domain http://" + data['domain'] + " expires in " + str(data['expires_in']) + " days."
            })
        print "SMS response", r.text

    def detectExpiration(self, data):
        results = self.expReg.search(data)
        if (results == None):
            return False
        if (len(results.group(1)) > 0):
            return results.group(1)
        else:
            return False

def main():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    with open('domains.json') as domains_file:    
        domains = json.load(domains_file)['domains']

    tester = Tester()

    for domain in domains:
        tester.runCheck(domain)
        print "Sleeping for 10 seconds.\n"
        time.sleep(10)

if __name__ == '__main__':
    main()