#!/usr/bin/env python3
import subprocess
from .printops import cprint
import os

def run_command(command, verbose=False):
    if verbose:
        cprint("command:", command)
    try:
        #output = subprocess.getoutput(command)
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        if verbose:
            cprint("output:", output)
        if b'error' in output.lower():
            cprint("error in output.lower():", output.lower())
            os._exit(1)
        if b'warning' in output.lower():
            cprint("warning in output.lower():", output.lower())
            #os._exit(1)
    except subprocess.CalledProcessError as error:
        cprint("exit code:", error.returncode, error.output)
        os._exit(1)

    return output

