import socket
import sys
import argparse
from chat_utils import *
import client_state_machine as csm
from GUI import *

class Client:
    def __init__(self, args):
        self.args = args
        self.socket = None
        self.sm = None
        self.gui = None

    def quit(self):
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        svr = SERVER if self.args.d is None else (self.args.d, CHAT_PORT)
        try:
            self.socket.connect(svr)
            print(f"Connected to server at {svr[0]}:{svr[1]}")
        except ConnectionRefusedError:
            print(f"Failed to connect to the server at {svr[0]}:{svr[1]}. Ensure the server is running.")
            sys.exit()

        self.sm = csm.ClientSM(self.socket)
        self.gui = GUI(send=self.send, recv=self.recv, sm=self.sm, s=self.socket)

    def shutdown_chat(self):
        # Implement any shutdown procedures if needed
        pass

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def run_chat(self):
        self.init_chat()
        self.gui.run()
        print("GUI has been closed.")
        self.quit()

def main():
    parser = argparse.ArgumentParser(description='Chat Client')
    parser.add_argument('-d', type=str, help='Server IP address', default=None)
    args = parser.parse_args()
    client = Client(args)
    client.run_chat()

if __name__ == "__main__":
    main()
