#!/usr/bin/env python
import termios
import struct
import fcntl
import sys
import time
import zmq
import subprocess
import sys
import os
import select
import zmq
import time
import signal
import click
import shlex
import tempfile

def docker_command(container,command):
    f = tempfile.NamedTemporaryFile()
    f.close()
    cidfile = f.name
    cmd = 'docker pull {} && docker run -it --cidfile {}'.format(container,cidfile)
    cmd += ' {} {}'.format(container,command)    
    print 'command is {}'.format(cmd)
    return cmd, cidfile

@click.command()
@click.argument('socketname')
@click.argument('compid')
@click.argument('side')
@click.argument('container')
@click.argument('command')
@click.argument('copyfrom')
@click.argument('copyto')
def start_server(socketname, compid, side, container, command, copyfrom, copyto):
    comparison_home = 'comparisons/{}'.format(compid)
    donefile = '{}/{}.done'.format(comparison_home,side)
    if os.path.exists(donefile):
        return
    
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(socketname)
    
    cmd, cidfile = docker_command(container,command)
    time.sleep(2)
    
    logfile  = '{}/{}.log'.format(comparison_home,side)
    msgstub  = {'to':'update_logs','compid':compid, 'side':side}
    start_docker(cmd, cidfile,socket, logfile = logfile, msgstub = msgstub)
    open(donefile, 'a').close()
    
    print 'docker done... copying result'
    container_id = open(cidfile).read()
    cmd = 'docker cp {}:{} {}/{}.{}'.format(container_id,copyfrom,comparison_home,side,copyto)
    subprocess.call(shlex.split(cmd))


    cmd = 'docker rm {}'.format(container_id)
    subprocess.call(shlex.split(cmd))
    print 'exit, runserver'
    
def start_docker(cmd,cid,socket,logfile,msgstub):
    cmd = cmd + '| cat' #make sure there is not interactive updating
    writelog = open(logfile,'w')
    readlog  = open(logfile,'r')
    p = subprocess.Popen(cmd, shell = True, stdout = writelog, stderr = writelog)
    while True:
        r, w, x = select.select([readlog],[],[], 0.0)
        zr,zw,zx = zmq.select([socket], [socket],[socket], timeout = 0.0)
        procpoll = p.poll()
        if (procpoll is not None):
            print "ending session because process ended"
            break
        if (readlog in r) and (socket in zw):
            fromprocess = os.read(readlog.fileno(),1024)
            if fromprocess:
                socket.send_json(dict(p = fromprocess, **msgstub))

if __name__ == '__main__':
    start_server()
