from collections import defaultdict
import csv

maps = {
    "shell": "command",
    "uri": "network",
    "package": "package",
    "host": "network",
    "db": "db",
    "cloud": "cloud",
    "port": "network",
    "service connection": "auth",
    "command options": "command",
    "network": "network",
    "URI": "network",
    "glob": "fs",
    "file": "fs",
    "CLI options": "command",
    "auth": "auth",
    "protocol": "network",
    "docker": "docker",
    "ip": "network",
    "firewall rule": "network",
    "locales": "OS general",
    "service  connection": "auth",
    "regex": "regex",
    "ssh key": "auth",
    "OS": "OS general",
    "command": "command",
    "environment variables": "OS general",
    "firewall": "network",
    "NetworkManager": "network",
    "URL": "network",
    "IP": "network",
    "token": "auth",
    "DNS": "network",
    "FQDN": "network",
    "container": "docker",
    "interface": "network",
    "AWS": "cloud",
    "HPE": "cloud",
    "version": "package",
    "mysql": "db",
    "username": "OS general",
    "credentials": "auth",
    "url": "network",
    "fstype": "fs",
    "args": "args"
}

elements = defaultdict(lambda: 0)
with open('../data/bugs.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        col = row[10]
        if col:
            segs = col.replace("; ", ";").split(";")
            freqs = set()
            for elem in segs:
                if elem:
                    flag = False
                    for k, v in maps.items():
                        if k in elem or k == elem:
                            freqs.add(v)
                            flag = True
                    if not flag:
                        print(elem)
            for k in freqs:
                elements[k] += 1
    print (elements)
