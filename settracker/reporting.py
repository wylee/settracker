from shutil import get_terminal_size

from .models import get_day_info


def print_report(session, group, days=30, target_reps=100, *, chart=True):
    day_info = list(get_day_info(session, group, days, target_reps))

    if not day_info:
        print('Nothing to report (no sets recorded)')
        return

    date_width = len(day_info[0].date_string)
    total_sets = sum(info.num_sets for info in day_info)
    total_reps = sum(info.num_reps for info in day_info)
    sets_width = len(str(total_sets)) + 2
    reps_width = len(str(total_reps)) + 2

    for info in day_info:
        message = f'{info.to_go} to go' if info.to_go > 0 else 'Done!'
        print(
            f'{info.date_string}'
            f'{info.num_sets: >{sets_width}} sets'
            f'{info.num_reps: >{reps_width}} reps'
            f'  {message}'
        )

    print(
        f'{"Total": <{date_width}}'
        f'{total_sets: >{sets_width}} sets'
        f'{total_reps: >{reps_width}} reps'
    )

    if chart:
        print()
        print_chart(session, group, days, target_reps, day_info=day_info)


def print_chart(session, group, days=30, target_reps=100, *,
                day_info=None, column_width=3, column_height=25):
    if day_info is None:
        day_info = list(get_day_info(session, group, days, target_reps))

    num_columns = max(days, len(day_info)) + 1
    term_width, term_height = get_terminal_size()

    while (num_columns * column_width > term_width) and column_width > 1:
        column_width -= 1

    chart_width = num_columns * column_width

    if target_reps <= column_height:
        column_height = target_reps

    columns = []
    reps_per_row = target_reps // column_height

    label = ' Reps '
    label_len = len(label)
    label_column = ['>'] + (['|'] * (column_height - 1))
    label_pos = column_height // 2 - label_len // 2
    label_column[label_pos:label_pos + label_len] = label
    columns.append(label_column)

    blocks = ['▁', '▂', '▃', '▅', '▆', '▇', '█', '█']
    empty_block = ' '
    num_blocks = len(blocks)
    full_block = blocks[-1]

    for info in day_info:
        reps = min(info.num_reps, target_reps)
        cutoff, remainder = divmod(reps, reps_per_row)
        column = [empty_block] * column_height
        if cutoff:
            column[-cutoff:] = [full_block] * cutoff
        if remainder:
            block_index = int(round(remainder / reps_per_row * num_blocks))
            partial_index = -1 if cutoff == 0 else -(cutoff + 1)
            column[partial_index] = blocks[block_index]
        columns.append(column)

    empty_column = [empty_block] * column_height
    for _ in range(days - len(day_info)):
        columns.append(empty_column)

    for i in range(column_height):
        for column in columns:
            print(f'{column[i]: <{column_width}}', end='')
        print()

    label = f' Last {len(day_info)} days '
    print(f'{label:-^{chart_width}}')

    if column_width >= 3:
        # Only print days if there's enough space
        for i in range(num_columns):
            i = '' if i == 0 else i
            print(f'{i: <{column_width}}', end='')
        print()
