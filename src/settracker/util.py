import os
import sys


def confirm(message, yes_answers=("y", "yes")):
    answer = prompt(
        f"{message} [{yes_answers[0]}/N]",
        lambda result: result.lower(),
        "no",
    )
    return answer in yes_answers


def prompt(message, converter=None, default=None):
    if not message.endswith(" "):
        message = f"{message} "
    result = None
    while not result:
        result = input(message)
        result = result.strip()
        if result:
            if converter is not None:
                try:
                    result = converter(result)
                except (TypeError, ValueError):
                    print(
                        f'Could not convert "{result}" to {converter.__name__}',
                        file=sys.stderr,
                    )
                    result = None
        elif default is not None:
            return default
    return result


def expand_file_name(file_name):
    if file_name is None:
        file_name = os.getenv("SET_TRACKER_DEFAULT_FILE") or "sets.db"
    if os.path.isabs(file_name):
        return file_name
    base_dir = os.getenv("SET_TRACKER_BASE_DIR") or os.getcwd()
    base_dir = os.path.expanduser(base_dir)
    base_dir = os.path.expandvars(base_dir)
    base_dir = os.path.abspath(base_dir)
    base_dir = os.path.normpath(base_dir)
    path = os.path.join(base_dir, file_name)
    if not os.path.isfile(path):
        name, ext = os.path.splitext(path)
        if not ext:
            path = f"{path}.db"
    return path
