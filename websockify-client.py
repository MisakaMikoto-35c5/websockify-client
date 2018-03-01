#!/usr/bin/python3

from base64 import b64encode, b64decode
from socket import socket, AF_INET, SOCK_STREAM
from websocket import create_connection, WebSocket

import sys, os, argparse

try:
    import _thread
    import socketserver
except ImportError:
    import thread as _thread
    import SocketServer as socketserver

REMOTE = None

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print("Passing data from: {}".format(self.client_address[0]))
        ws = create_connection(REMOTE, header=["Sec-WebSocket-Protocol: base64"])
        
        def __inner_packet_sender():
            # Send data to the server
            while True:
                try:
                    data = self.request.recv(1024)
                except OSError:
                    return
                if data != b'':
                    try:
                        ws.send(b64encode(data).decode('utf-8'))
                    except BrokenPipeError:
                        return
        _thread.start_new_thread(__inner_packet_sender, (),)
        
        try:
            # Receive data from the server
            while True:
                try:
                    result = ws.recv()
                except websocket._exceptions.WebSocketConnectionClosedException:
                    break
                if result == b'\x03\xe8Target closed':
                    print('Receive: Remote closed')
                    ws.close()
                    break
                try:
                    self.request.send(b64decode(result))
                except OSError:
                    break
        except KeyboardInterrupt:
            return
        finally:
            ws.close()
            return

def http_test(remote_addr):
    print('Testing ' + remote_addr)
    ws = create_connection(remote_addr, header=["Sec-WebSocket-Protocol: base64"])
    print('Sending HTTP request to ' + remote_addr)
    ws.send(b64encode('GET / HTTP/1.1\r\nConnection: close\r\nAccept: */*\r\nHost: example.com\r\n\r\n'.encode('utf-8')).decode('utf-8'))
    print('Send finish, receiveing HTTP request to ' + remote_addr)
    while True:
        result = ws.recv()
        if result == b'\x03\xe8Target closed':
            print('Receive: Remote closed')
            ws.close()
            return
        print('Receive from remote: ' + remote_addr)
        print(b64decode(result))
    ws.close()

def check_list(keys, result_list):
    for i in keys:
        try:
            now_value = result_list[i]
            if now_value == None or now_value == '':
                return False
        except KeyError:
            return False
    return True

def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--remote-address', action='store', dest='remote_address', required=True,
                        help='Remote address, like "ws://your.site.example.org/some/path"')
    parser.add_argument('-l', '--listen-address', action='store', dest='bind_address', default='127.0.0.1',
                        help='Listen address, default value is "127.0.0.1"')
    parser.add_argument('-p', '--bind-port', action='store', dest='bind_port', default='3124',
                        help='Bind port, default value is "3124"')
    return parser.parse_args()

if __name__ == '__main__':
    config = get_config()
    server = ThreadedTCPServer((config.bind_address, int(config.bind_port)), ThreadedTCPRequestHandler)
    REMOTE = config.remote_address
    print('Started websockify client at tcp://{}:{}, remote server is {}'.format(
        config.bind_address,
        config.bind_port,
        config.remote_address
        ))
    server.serve_forever()