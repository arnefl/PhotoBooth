import time

from os import popen, system

def CheckIfProcessExists(process):
    SystemProcesses = popen('ps aux')
    return(any([process in p for p in SystemProcesses]))

def ProcessKillAndWait(process):
    ProcessExists = CheckIfProcessExists(process)

    if ProcessExists:
        system('pkill -9 {}'.format(process))

    while ProcessExists:
        ProcessExists = CheckIfProcessExists(process)
        time.sleep(1)

    return(True)
