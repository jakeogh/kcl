#!/usr/bin/env python3

# https://github.com/mitsuhiko/click/issues/441
CONTEXT_SETTINGS = \
    dict(help_option_names=['--help'], terminal_width=shutil.get_terminal_size((80, 20)).columns)
