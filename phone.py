#!/usr/bin/env python

from __future__ import print_function

import sys
import time
import yaml
import json
import random
import requests

class Phone(object):
    def __init__(self, config_file, trace_file):
        with open(config_file) as f:
            self.config = yaml.load(f)

        self.imsi = self._get_fake_imsi()
        with open(trace_file) as f:
            self.trace = self.load_trace(f)

    def _get_fake_imsi(self):
        """
        An IMSI is a unique subscriber identifier.
        """
        return "IMSI999990091%.6d" % random.randint(0,999999)

    def load_trace(self, trace):
        res = []
        for line in trace:
            if line.startswith("#"):
                continue

            try:
                fields = [int(_) for _ in line.split(",")]
            except ValueError:
                print("Invalid trace line: '%s'" % line, file=sys.stderr)
                raise

            res.append({"imsi": self.imsi, "time": fields[0], "pos_x": fields[1], "pos_y": fields[2], "rssi": fields[3]})
        return res

    def report(self, entry):
        if self.config['output'] == "STDOUT":
            print(entry)
        elif self.config['output'] == "JSON":
            url = self.config['report_url']
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=json.dumps(entry), headers=headers) # XXX No error checking!
        else:
            raise ValueError("Invalid output format.")

    def run(self):
        speedup = float(self.config['speedup'])
        for item in self.trace:
            time.sleep(item['time'] / speedup)
            self.report(item)

if __name__ == "__main__":
    p = Phone("config.yaml", sys.argv[1])
    p.run()
