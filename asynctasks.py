from celery import shared_task
import os
import subprocess
import zmq
import utils
import json

IPC_SOCKETNAME = 'ipc://monitor.sock'

@shared_task
def run_comparison(formdata,comparison_id):
    print "running comparison {}".format(comparison_id)
    print "formdata: {}".format(formdata)

    # lhs_container, lhs_command, lhs_

    comparison_home = 'comparisons/{}'.format(comparison_id)
    if not os.path.exists(comparison_home):
        os.makedirs(comparison_home)
    p_lhs = subprocess.Popen(['./runserver.py',IPC_SOCKETNAME,str(comparison_id),'lhs',
                              formdata['dockerImageLHS'],formdata['commandLHS'],
                              '/cutflowcomp/cutflow.yaml','output.yaml'
                              ])
    p_rhs = subprocess.Popen(['./runserver.py',IPC_SOCKETNAME,str(comparison_id),'rhs',
                              formdata['dockerImageRHS'],formdata['commandRHS'],
                              '/cutflowcomp/cutflow.yaml','output.yaml'
                              ])
    p_lhs.wait()
    p_rhs.wait()
    
    print "both processes exited, collecting results"
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(IPC_SOCKETNAME)

    results = utils.collect_results(comparison_id)
    socket.send_json({'compid':str(comparison_id),'to':'comp_results','results':results})
    print "done with task"

    