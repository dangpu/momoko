#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2013-11-20
    @author: devin
    @desc:
        http server
'''
import sys
import socket
import SocketServer
import SimpleHTTPServer
import urlparse

class URLParams:
    def __init__(self, params, path):
        self.params = params
        self.path = path
    
    def get(self, key):
        if key in self.params:
            return self.params[key][0]
        return None

    def get_array(self, key):
        if key in self.params:
            return self.params[key]
        return []
    
    def get_json_obj(self, key):
        import jsonlib
        print self.params[key][0]
        if key in self.params:
            return jsonlib.read(self.params[key][0])
        return None

class ThreadedHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    dispatchers = {}
    
    @classmethod 
    def register(self, path, fun):    
        self.dispatchers[path] = fun 

    def do_GET(self):
        o = urlparse.urlparse(self.path)
        params = urlparse.parse_qs(o.query)

        response = ''
        if o.path in self.dispatchers:
            fun = self.dispatchers[o.path]
            response = fun(URLParams(params, o.query))
        #send data
        self.send_response(200)
        self.end_headers()
        self.wfile.write(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class HttpServer:
    def __init__(self, host, port):
        self.server = ThreadedTCPServer((host, port), ThreadedHTTPRequestHandler)

    def register(self, path, fun):
        ThreadedHTTPRequestHandler.register(path, fun)

    def run(self):
        self.server.serve_forever()

def Test(params):
    return "Test:" + str(params)

if __name__ == "__main__":
    HOST, PORT = "115.29.161.44", 8089
    server = HttpServer(HOST, PORT)
    server.register("/test", Test)
    server.run()

