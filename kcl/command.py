#!/usr/bin/env python3
import subprocess
from kcl.printops import ceprint
#import os

def run_command(command, verbose=False):
    if verbose:
        ceprint("command:", command)
    try:
        #output = subprocess.getoutput(command)
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        #if verbose:
        #    eprint("output:", output)
        #if b'error' in output.lower():
        #    eprint("error in output.lower():", output.lower())
        #    os._exit(1)
        #if b'warning' in output.lower():
        #    eprint("warning in output.lower():", output.lower())
        #    #os._exit(1)
    except subprocess.CalledProcessError as error:
        ceprint("exit code:", error.returncode, error.output)
        output = False
        #os._exit(1)

    return output
