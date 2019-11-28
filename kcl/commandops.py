#!/usr/bin/env python3
import subprocess
from kcl.printops import ceprint
#import os


def run_command(command, verbose=False, shell=True, expected_exit_code=0, stdin=None, stderr=subprocess.STDOUT):
    if isinstance(command, list):
        command = ' '.join(command)
    output = ''
    if verbose:
        ceprint("command:", '`' + command + '`')
        ceprint("shell:", shell)
    try:
        output = subprocess.check_output(command, stderr=stderr, shell=shell, stdin=stdin)
        if verbose:
            ceprint("output:", output.decode('utf8'))  # bug
    except subprocess.CalledProcessError as error:
        if error.returncode == expected_exit_code:
            return output
        ceprint("command:", command)
        ceprint("exit code:", error.returncode, error.output)
        raise error

    return output
