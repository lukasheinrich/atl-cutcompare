from celery import shared_task
import os
import subprocess

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
                              formdata['outputLHS'],'output.root'
                              ])
    p_rhs = subprocess.Popen(['./runserver.py',IPC_SOCKETNAME,str(comparison_id),'rhs',
                              formdata['dockerImageRHS'],formdata['commandRHS'],
                              formdata['outputRHS'],'output.root'
                              ])
    p_lhs.wait()
    p_rhs.wait()
    print "done.."
    