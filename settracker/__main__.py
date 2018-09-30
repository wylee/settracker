import argparse
import os
import signal
import sys
import textwrap
from datetime import datetime

from .models import DATE_FORMAT, TIME_FORMAT
from .models import create_tables, get_session
from .models import SetGroup
from .models import add_set, get_or_add_set_group
from .reporting import print_chart, print_report
from .util import confirm, expand_file_name, prompt


def main(argv=None):
    """Keep track of sets of rep(etition)s.

    This can be used for tracking sets of exercises or sets of any other
    repetitive activity. Sets are grouped together by day.

    To add a set::

        python -m settracker 10

    When a set is added, a progress report will be shown (of the last 30
    days by default). To show the progress report without adding a set::

        python -m settracker -r

    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    description = textwrap.dedent(f'    {main.__doc__.strip()}')

    default_file_name = expand_file_name(None)
    default_group = os.getenv('SET_TRACKER_DEFAULT_GROUP')
    default_target_reps = os.getenv('SET_TRACKER_DEFAULT_TARGET_REPS')
    default_date_time = datetime.now()
    default_date = default_date_time.strftime(DATE_FORMAT)
    default_time = default_date_time.strftime(TIME_FORMAT)

    parser = argparse.ArgumentParser(
        prog='set-tracker',
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-f', '--file-name', default=None,
        help='SQLite database file; '
             'defaults to sets.db (change via SET_TRACKER_DEFAULT_FILE); '
             'can be specified with or without .db suffix; '
             'relative file paths are searched for in the current directory '
             '(set SET_TRACKER_BASE_DIR to search in a different directory) '
             f'[{default_file_name}]')

    parser.add_argument(
        'quantity', nargs='?', type=positive_int_type, default=None,
        help='Number of reps done in set; if not specified, will be prompted for')

    group_help = f'[{default_group}]' if default_group else ''
    parser.add_argument('group', nargs='?', default=default_group, help=group_help)

    parser.add_argument(
        '-d', '--date', type=date_type, default=default_date,
        help='Date set was done in YYYY-MM-DD format '
             f'[today: {default_date}]')

    parser.add_argument(
        '-t', '--time', type=time_type, default=default_time,
        help='Time set was done in HH:MM format (24-hour clock) '
             f'[now: {default_time}]')

    parser.add_argument(
        '-T', '--target-reps', type=int, default=default_target_reps,
        help='Daily target repetitions [100]')

    parser.add_argument(
        '-r', '--report-only', action='store_true', default=False,
        help='Only show report (skip adding a set) [False]')

    parser.add_argument(
        '-c', '--chart-only', action='store_true', default=False,
        help='Only show chart in report (implies -r) [False]')

    parser.add_argument(
        '-C', '--no-chart', dest='chart', action='store_false', default=True,
        help='Don\'t show chart when reporting (implies -r) [True]')

    parser.add_argument(
        '-D', '--days', type=int, default=30,
        help='Number of days to include in report [30]')

    args = parser.parse_args(argv)
    file_path = expand_file_name(args.file_name)
    report_only = args.report_only or args.chart_only or not args.chart
    group = args.group
    quantity = args.quantity
    date_time = datetime.combine(args.date, args.time)
    days = args.days
    target_reps = args.target_reps

    print(f'Database file: {file_path}')

    if not os.path.exists(file_path):
        confirmed = confirm('Database file does not exist. Create?')
        if confirmed:
            create_tables(file_path)

    session = get_session(file_path)

    if group:
        # If a group was specified, look it up. If it doesn't exist,
        # create it.
        group = get_or_add_set_group(session, group)
        if group is None:
            return abort()
    else:
        # If a group was not specified, ask the user to select a group
        # or specify the name of a new group.
        groups = list(session.query(SetGroup).order_by('name').all())
        if groups:
            print('Available set groups:')
            for i, g in enumerate(groups, 1):
                print(f'    {i}) {g.name}')
        else:
            print('No set groups')
        group = prompt('Select a group or enter a new group name:')
        if group.isdigit():
            group = groups[int(group) - 1]
        else:
            group = get_or_add_set_group(session, group)
            if group is None:
                return abort()

    print(f'Set group: {group.name}')

    if not report_only:
        if quantity is None:
            quantity = prompt('How many reps did you do?', converter=int)
        new_set = add_set(session, group, quantity, date_time)
        if new_set is not None:
            print(f'Added {new_set.quantity} reps')
        else:
            return abort()

    print()
    if args.chart_only:
        print_chart(session, group, days, target_reps)
    else:
        print_report(session, group, days, target_reps, chart=args.chart)

    return 0


def abort(message='Aborted', code=0):
    print(message)
    return code


def date_type(value):
    return datetime.strptime(value, DATE_FORMAT).date()


def time_type(value):
    return datetime.strptime(value, TIME_FORMAT).time()


def positive_int_type(value):
    value = int(value)
    if value < 1:
        raise ValueError('Expected a positive number')
    return value


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
