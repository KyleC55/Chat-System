import socket
import time

# Use local loopback address by default
CHAT_IP = '127.0.0.1'
CHAT_PORT = 1112
SERVER = (CHAT_IP, CHAT_PORT)

menu = "\n++++ Choose one of the following commands\n \
        time: calendar time in the system\n \
        who: to find out who else are there\n \
        c _peer_: to connect to the _peer_ and chat\n \
        ? _term_: to search your chat logs where _term_ appears\n \
        p _#_: to get number <#> sonnet\n \
        q: to leave the chat system\n\n"

S_OFFLINE   = 0
S_CONNECTED = 1
S_LOGGEDIN  = 2
S_CHATTING  = 3

SIZE_SPEC = 5

CHAT_WAIT = 0.2

def print_state(state):
    print('**** State *****::::: ')
    if state == S_OFFLINE:
        print('Offline')
    elif state == S_CONNECTED:
        print('Connected')
    elif state == S_LOGGEDIN:
        print('Logged in')
    elif state == S_CHATTING:
        print('Chatting')
    else:
        print('Error: wrong state')

def mysend(s, msg):
    # Append size to message and send it
    msg = ('0' * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg):
        sent = s.send(msg[total_sent:])
        if sent == 0:
            print('Server disconnected')
            break
        total_sent += sent

def myrecv(s):
    # Receive size first
    size = ''
    while len(size) < SIZE_SPEC:
        text = s.recv(SIZE_SPEC - len(size)).decode()
        if not text:
            print('Disconnected')
            return('')
        size += text
    size = int(size)
    # Now receive message
    msg = ''
    while len(msg) < size:
        text = s.recv(size - len(msg)).decode()
        if text == '':
            print('Disconnected')
            break
        msg += text
    return msg

def text_proc(text, user):
    ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
    return '(' + ctime + ') ' + user + ' : ' + text  # Message goes directly to screen
