import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for
import socketio
import time
import uuid
import zmq
import os
import yaml
import json
import subprocess
import runserver
import client
import utils
import asynctasks
from celeryapp import app as celeryapp

app = Flask('dockercutflow')
app.debug = True
IPC_SOCKETNAME = 'ipc://monitor.sock'
sio = socketio.Server()

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/results/<compid>')
def results(compid):
    return render_template('results.html', compid = compid)
    
@app.route('/submit', methods = ['POST'])
def submit():
    compid = uuid.uuid4()
    asynctasks.run_comparison.delay(request.form,compid)

    return redirect(url_for('results', compid = compid))

@sio.on('connect')
def connect(sid, environ):
    print "connected with sid: {}".format(sid)

@sio.on('please_join')
def join(sid,data):
    print "got data {}".format(data)
    sio.enter_room(sid,data)
    sio.emit('luke','to_room',room = data)
    #we joined the room and if a existing logile exits, we're sending it now
    for side in ['lhs','rhs']:
        logname = 'comparisons/{}/{}.log'.format(data,side)
        if os.path.exists(logname):
            sio.emit('update_logs',json.dumps({'side':side,'compid':data,'p':open(logname).read()}),room = sid)

    results = {'results':utils.collect_results(data)}
    if results['results']:
        sio.emit('comp_results',json.dumps(results),room = sid)

@sio.on('luke')
def connect(sid, data):
    print "got event with sid: {} and data: {}".format(sid,data)
    sio.emit('luke','there {}'.format(sid), room = sid)

@sio.on('disconnect')
def disconnect(sid):
    print "disconnected from sid: {}".format(sid)

def zmq_monitor(sio,socketname):
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(socketname)

    while True:
        zr,zw,zx = zmq.select([socket], [socket],[socket], timeout = 0.0)
        if socket in zr:
            jsondata = socket.recv_json()
            senddata = json.dumps(jsondata)
            sio.emit(jsondata['to'],senddata,room = jsondata['compid'])
        time.sleep(0.01)

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.spawn(zmq_monitor,sio,IPC_SOCKETNAME)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)