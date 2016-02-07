#!/usr/bin/env python
import select
import sys
import zmq


def client(host,readfrom, socketio):
    sio,sid = socketio['sio'],socketio['sid']
    def writer(x):
        sio.emit('luke',x,room = sid)
    writer('hello!!')

    context = zmq.Context()
    
    print('starting remote docker session')

    #incoming messages
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://{0}:{1}".format(host,readfrom))

    poller = zmq.Poller()
    poller.register(socket,zmq.POLLIN)
    sockets = [socket]

    socket.send_json({'ctrl':'start'})
    ack = socket.recv()
    
    
    outfile = sys.stdout
    
    while True:
        s = read_write_nontty(socket,writer,outfile)
        if s > 0: break

    print('Bye.')
    return

def read_write_nontty(socket,writer,outfile):
    try:
        r, w, x  = select.select([], [outfile], [], 0.0)
    except select.error:
        pass
    zr,zw,zx = zmq.select([socket],[socket],[], timeout = 0.0)

    if (socket in zr) and (outfile in w):
        x = socket.recv_json()
        result = handle_message(x,socket,writer,outfile)
        if result == 1: return 1

    return 0

def handle_message(x,socket,writer,outfile):
    print "handle {}".format(x)
    try:
        plain = x['p']
        outfile.write(plain)
        writer(plain)
        while True:
            r, w, x  = select.select([], [outfile], [], 0.0)
            if outfile in w:
                outfile.flush()
                break
    except KeyError:
        if 'ctrl' in x:
            ctrlmsg = x['ctrl']
            if 'terminated' in ctrlmsg:
                socket.send_json({'ctrl':'terminated'})
                return 1

if __name__ == '__main__':
    client('0.0.0.0',5556,None)