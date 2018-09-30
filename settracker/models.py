from collections import namedtuple, OrderedDict
from datetime import date, datetime, timedelta
from functools import lru_cache
from itertools import groupby

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from .util import confirm, expand_file_name


DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = f'{DATE_FORMAT}@{TIME_FORMAT}'
DATE_DISPLAY_FORMAT = '%d %b %Y'
DATETIME_DISPLAY_FORMAT = f'{DATE_DISPLAY_FORMAT} at {TIME_FORMAT}'
ONE_DAY = timedelta(days=1)


Base = declarative_base()
Session = sessionmaker()


@lru_cache()
def get_engine(file_name):
    file_name = expand_file_name(file_name)
    url = f'sqlite:///{file_name}'
    return create_engine(url)


def get_session(file_name):
    engine = get_engine(file_name)
    return Session(bind=engine)


def create_tables(file_name):
    engine = get_engine(file_name)
    Base.metadata.create_all(engine)


class SetGroup(Base):

    __tablename__ = 'set_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sets = relationship('Set', back_populates='group')


class Set(Base):

    __tablename__ = 'sets'

    """A set of repetitions done at a specified date/time."""

    def __init__(self, **kwargs):
        date_time = kwargs.get('date_time')
        if date_time is None:
            kwargs['date_time'] = datetime.now()
        super().__init__(**kwargs)

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    date_time = Column(DateTime, nullable=False)
    group_id = Column(Integer, ForeignKey('set_groups.id'), nullable=False)
    group = relationship('SetGroup', back_populates='sets')

    @property
    def date(self):
        return self.date_time.date()

    @property
    def time(self):
        return self.date_time.time()

    @property
    def date_string(self):
        return self.date_time.strftime(DATE_FORMAT)

    @property
    def time_string(self):
        return self.date_time.strftime(TIME_FORMAT)

    @property
    def date_time_string(self):
        return self.date_time.strftime(DATETIME_FORMAT)

    @property
    def date_display_string(self):
        return self.date_time.strftime(DATE_DISPLAY_FORMAT)

    @property
    def time_display_string(self):
        return self.time_string

    @property
    def date_time_display_string(self):
        return self.date_time.strftime(DATETIME_DISPLAY_FORMAT)


def get_or_add_set_group(session, name):
    try:
        group = session.query(SetGroup).filter_by(name=name).one()
    except NoResultFound:
        confirmed = confirm(f'Set group "{name}" does not exist. Create?')
        if confirmed:
            group = SetGroup(name=name)
            session.add(group)
            session.commit()
        else:
            group = None
    return group


def add_set(session, group, quantity, date_time):
    new_set = Set(group=group, quantity=quantity, date_time=date_time)
    confirmed = confirm(
        f'Add set of {new_set.quantity} reps '
        f'for {new_set.date_time_display_string}?'
    )
    if not confirmed:
        session.expunge_all()
        return None
    session.add(new_set)
    session.commit()
    return new_set


DayInfo = namedtuple(
    'DayInfo', 'date date_string sets num_sets num_reps target to_go extra behind')


def get_day_info(session, group, days=30, target_reps=100, skip_leading=True):
    """Get info for the specified number of days."""
    q = session.query(Set)
    q = q.filter_by(group=group)

    delta = timedelta(days=(days - 1))
    start_date = date.today() - delta
    end_date = start_date + timedelta(days=days)
    q = q.filter(Set.date_time >= start_date)
    q = q.filter(Set.date_time <= end_date)
    q = q.order_by('date_time', 'id')
    records = q.all()

    sets = OrderedDict()

    current_date = start_date
    while current_date < end_date:
        sets[current_date] = []
        current_date += ONE_DAY

    for record in records:
        sets[record.date].append(record)

    sets = tuple(sets.items())

    if skip_leading:
        skip = 0
        for (group_date, day_sets) in sets:
            if not day_sets:
                skip += 1
            else:
                break
        if skip:
            sets = sets[skip:]

    prev_behind = 0
    last = len(sets) - 1

    for i, (group_date, day_sets) in enumerate(sets):
        date_string = group_date.strftime(DATE_DISPLAY_FORMAT)
        num_sets = len(day_sets)
        num_reps = sum(s.quantity for s in day_sets)
        to_go = target_reps - num_reps

        if to_go < 0:
            extra = -to_go
            to_go = 0
            behind = 0
        elif to_go > 0:
            extra = 0
            behind = 0 if i == last else to_go
        else:
            extra = 0
            behind = 0

        behind = behind + prev_behind - extra
        behind = 0 if behind < 0 else behind

        info = DayInfo(
            group_date, date_string, day_sets, num_sets, num_reps, target_reps, to_go, extra,
            behind)

        prev_behind = behind

        yield info
