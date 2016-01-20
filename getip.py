#! /usr/bin/env python

from __future__ import print_function

import re
import requests

def get_external_ip():
    site = requests.get("http://checkip.dyndns.org/").text
    grab = re.findall('\d{2,3}.\d{2,3}.\d{2,3}.\d{2,3}', site)
    address = grab[0]
    return address

def main():
    print(get_external_ip())

if __name__ == "__main__":
        main()
