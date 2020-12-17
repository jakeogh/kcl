#!/usr/bin/env python3

import glob
from pathlib import Path

from icecream import ic

from kcl.mathops import sort_versions


def get_latest_postgresql_version(verbose=False):
    glob_pattern = "/etc/init.d/postgresql-*"
    if verbose:
        ic(glob_pattern)
    results = glob.glob(glob_pattern)
    if verbose:
        ic(results)
    if len(results) == 0:
        raise FileNotFoundError(glob_pattern)
    versions = [init.split('-')[-1] for init in results]
    if verbose:
        ic(versions)
    versions = sort_versions(versions, verbose=verbose)
    if verbose:
        ic(versions)

    return versions[0]



## from kerframil@#gentoo
#
#shopt -s nullglob
#
#get_postgresql_version() {
#        declare -a files
#        files=(/etc/init.d/postgresql-*)
#        if (( ! ${#files[@]} )); then
#            return 1
#        fi
#        # without -V, 9.x would be considered to be newer than 10.x, for instance
#        mapfile -t files < <(printf '%s\n' "${files[@]##*/}" | sort -V)
#        echo "${files[-1]#*-}"
#}
#
#echo "$(get_postgresql_version)"

