# Set Tracker

This is a simple console-based program for keeping track of sets of
exercises (or sets of any kind of repetitive activity). Sets are stored
in a SQLite database that includes the number of reps and the date/time
for each set.

Every time a new set is added, a report is generated that shows the
number of sets and the total number of reps for each day. A chart is
also displayed to give a visual indication of progress over the past 30
days.

The default location of the SQLite database file is `sets.db` in the
current directory. This file will be created automatically if it doesn't
already exist.

The default location can be overridden using the command line option
`--file-name` or by setting the `SET_TRACKER_BASE_DIR` and
`SET_TRACKER_DEFAULT_FILE` environment variables:

    export SET_TRACKER_BASE_DIR=/some/path   # bash
    set -Ux SET_TRACKER_BASE_DIR /some/path  # fish

With this configuration, `settracker` will look for `sets.db` in
`/some/path`.

If `SET_TRACKER_DEFAULT_FILE` is set to an absolute path, that path will
be used as is and `SET_TRACKER_BASE_DIR` will be ignored. If it's set to
a relative path, it will be considered relative to the specified base
directory or to `PWD` if no base directory is set.

## Installation

> NOTE Python 3.11+ is the miminum supported version.

Clone the repo and use either `pip` or [pipx] to install the package:

    git clone https://github.com/wylee/settracker
    cd settracker

    # Install using pip
    pip install --user .

    # Or install using pipx
    pipx install .

If you want to hack on this project, use `poetry` to install it:

    git clone https://github.com/wylee/settracker
    cd settracker
    poetry install
    poetry run settracker

[pipx]: https://pypa.github.io/pipx/
[poetry]: https://python-poetry.org

## Adding a Set

If you run `settracker` with no options, it will prompt for the number
of reps and use today's date and the current time:

    > settracker
    How many reps did you do? 10
    Add 10 reps for 21 Nov 2017 at 12:00? yes
