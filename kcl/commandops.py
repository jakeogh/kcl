#!/usr/bin/env python3
import subprocess
import os
from kcl.printops import ceprint


def run_command(command, verbose=False, shell=True, expected_exit_code=0, stdin=None, stderr=subprocess.STDOUT, popen=False):
    if isinstance(command, str):
        command = os.fsencode(command)  # hm.
    if isinstance(command, list):
        command = b' '.join(command)
    output = ''
    if verbose:
        ceprint(b"command: `" + command + b"`")
        ceprint("shell:", shell)
    if popen:
        if isinstance(command, bytes):
            command = command.decode('utf8')
        output = os.popen(command).read()
        if verbose:
            ceprint("output:", output)

    else:
        try:
            output = subprocess.check_output(command, stderr=stderr, shell=shell, stdin=stdin)
            if verbose:
                ceprint(b"output:", output)
        except subprocess.CalledProcessError as error:
            if error.returncode == expected_exit_code:
                return output
            ceprint(b"command: `" + command + b"`")
            ceprint("exit code:", error.returncode, error.output)
            raise error

    return output
