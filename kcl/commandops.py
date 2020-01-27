#!/usr/bin/env python3
import subprocess
import os
from icecream import ic
from kcl.printops import ceprint


def run_command(command, verbose=False, shell=True, expected_exit_code=0, stdin=None, stderr=subprocess.STDOUT, popen=False):
    if isinstance(command, str):
        command = os.fsencode(command)  # hm.
    if isinstance(command, list):
        command = b' '.join(command)
    output = ''
    if verbose:
        ic(command)
        ic(shell)
    if popen:
        if isinstance(command, bytes):
            command = command.decode('utf8')
        popen_instance = os.popen(command, stderr=stderr)
        output = popen_instance.read()
        if verbose:
            ic(output)
        exit_code = popen_instance.returncode
        if exit_code == expected_exit_code:
            return output
        else:
            ic(command)
            ceprint("exit code:", exit_code, output)

    else:
        try:
            output = subprocess.check_output(command, stderr=stderr, shell=shell, stdin=stdin)
            if verbose:
                ic(output)
        except subprocess.CalledProcessError as error:
            if error.returncode == expected_exit_code:
                return output
            ic(command)
            ceprint("exit code:", error.returncode, error.output)
            raise error

    return output
