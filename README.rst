Set Tracker
+++++++++++

This is a simple console-based program for keeping track of sets of
exercises (or sets of any kind of repetitive activity). Sets are stored
in a SQLite database that includes the number of reps and the date/time
for each set.

Every time a new set is added, a report is generated that shows the
number of sets and the total number of reps for each day. A chart is
also displayed to give a visual indication of progress over the past 30
days.

.. note:: The default location of the SQLite database file is ``sets.db`` in
    the current directory. This file will be created automatically if it
    doesn't already exist.

Installation
============

.. note:: Python 3.6+ is *required*.

This package isn't published to PyPI, so it's installed via git::

    git clone https://github.com/wylee/settracker
    cd settracker
    python -m settracker -h

You can also install it with pip from the source directory. This will
install the ``set-tracker`` console script, which is slightly more
convenient than doing ``python -m settracker``. First, clone as above
and ``cd`` into the ``settracker`` directory, then::

    pip install -e .
    set-tracker -h

Adding a Set
============

If you run ``python -m settracker`` or ``set-tracker`` with no options,
it will prompt for the number of reps and use today's date and the
current time::

    > set-tracker
    How many reps did you do? 10
    Add 10 reps for 21 Nov 2017 at 12:00? yes
