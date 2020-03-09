import sys
import subprocess
import socketserver
import time

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.request.sendall(b'XtraLib.Stream.0\nTacview.RealTimeTelemetry.0\nI AM THE SERVER\n\x00')
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

        FO=open('DATE(2020-03-07)_UTC(15.58.26)_LOC(07.58.26)_diVine@DESKTOP-ON3TOE9.acmi', 'r')
        while True:
            loglines=FO.readline()
            print(loglines)
            self.request.sendall(bytes(loglines, encoding='utf8'))





if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    subprocess.call( ['D:\\Tacview\\tacview.exe', '/ConnectRealTimeTelemetry'] )
    server.serve_forever()
