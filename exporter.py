#!/usr/bin/env python

import dns.resolver
import dns.query
import logging
import time
import http.server
import sys
from urllib.parse import urlparse, parse_qs

def dnsquery(server, domain, qtype, count):
    minRTT = 0
    maxRTT = 0
    avgRTT = 0
    totalRTT = 0
    success = 0
    i = 0
    for i in range(int(count)):
        start = time.time()
        res = dns.resolver.Resolver(configure=False)
        res.nameservers = [server]
        r = res.query(domain, qtype)
        end = time.time()
        diff = (end - start)*1000
        if i == 0:
            minRTT = diff
        if diff > maxRTT:
            maxRTT = diff
        if diff < minRTT:
            minRTT = diff
        totalRTT = totalRTT + diff
        if r.response.rcode() == 0:
            success = success + 1
        i = i + 1
    avgRTT = totalRTT / success
    return minRTT, maxRTT , avgRTT, float(success/float(count))


class myHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path).query
        value = parse_qs(parsed_path)
        minRTT, maxRTT, avgRTT , success = dnsquery(value['target'][0], value['domain'][0], value['type'][0], value['count'][0])
        message = "dns_exporter_min_RTT {}".format(minRTT)
        message = message + "\ndns_exporter_max_RTT {}".format(maxRTT)
        message = message + "\ndns_exporter_avg_RTT {}".format(avgRTT)
        message = message + "\ndns_exporter_success_count {}".format(success)
        self.send_response(200)
        self.end_headers()
        message = str.encode(message)
        self.wfile.write(message)
        return


def export(HandlerClass = http.server.BaseHTTPRequestHandler,
    ServerClass = http.server.HTTPServer):
    http.server.server_address = ('', port)
    httpd = http.server.HTTPServer(http.server.server_address, myHandler)
    logger.debug("Started with port {}".format(port))
    httpd.serve_forever()
 
if __name__ == '__main__':
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    else:
        port = 8088
    logger.debug("Starting with port {}".format(port))
    export(port)
