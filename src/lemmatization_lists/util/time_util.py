
import time
import datetime

DEFAULT_DATE_FORMAT = "%Y%m%d%H%M%S"


def str_date_to_milliseconds(s_datetime, time_zone=1, date_time_format=DEFAULT_DATE_FORMAT):
    """
    Transform a string representation of a date to a UNIX format timestamp (referred to GMT+0).
    :param s_datetime: String containing the date time inofrmation.
    :param time_zone: Time zone in hours with respect to UTC. Default values is 1 (Madrid/Paris/Berlin timezone)
    :param date_time_format: String containing the format of the date to be processed. Default value is
    DEFAULT_DATE_FORMAT.
    :return:
    """
    t = datetime.datetime.strptime(s_datetime, date_time_format)
    res = long(time.mktime((t.year, t.month, t.day, t.hour, t.minute, t.second, 0, 0, 0))) - time_zone * 3600
    return res * 1000


def timestamp_to_str(timestamp, millis=True, format=DEFAULT_DATE_FORMAT):
    """
    Get the normalized string representation of the time corresponding to a timestamp.
    :param timestamp: Time in UNIX format.
    :param millis: True if timestamp is represented using milliseconds. False if a second based representation is used.
    :param format: Format to be used to convert timestamp to string. Default value: DEFAULT_DATE_FORMAT (%Y%m%d%H%M%S)
    :return:
    """
    t = timestamp
    if millis:
        t = timestamp / 1000
    res = datetime.datetime.fromtimestamp(t).strftime(format)
    return res


def parse_datetime(s_date):
    """
    Parse a date string in the format yyyy/mm/dd[/hh/mm/ss]
    :param s_date:
    :return:
    """
    _toks = s_date.split("/")
    if len(_toks) < 3:
        raise Exception("The format of the date " + s_date + " is wrong. Expected yyyy/mm/dd[hh/mm/ss]")
    year = int(_toks[0])
    month = int(_toks[1])
    day = int(_toks[2])
    hour = 0
    minute = 0
    second = 0
    if len(_toks) >= 4:
        hour = int(_toks[3])
    if len(_toks) >= 5:
        minute = int(_toks[4])
    if len(_toks) >= 6:
        second = int(_toks[5])
    return datetime.datetime(year, month, day, hour, minute, second)


def total_seconds(timedelta):
    """Convert timedeltas to seconds
    In Python, time differences can take many formats. This function can take
    timedeltas in any format and return the corresponding number of seconds, as
    a float.
    Beware! Representing timedeltas as floats is not as precise as representing
    them as a timedelta object in datetime, numpy, or pandas.
    Parameters
    ----------
    timedelta : various
        Time delta from python's datetime library or from numpy or pandas. If
        it is from numpy, it can be an ndarray with dtype datetime64. If it is
        from pandas, it can also be a Series of datetimes. However, this
        function cannot operate on entire pandas DataFrames. To convert a
        DataFrame, do df.apply(to_seconds)
    Returns
    -------
    seconds : various
        Returns the total seconds in the input timedelta object(s) as float.
        If the input is a numpy ndarray or pandas Series, the output is the
        same, but with a float datatype.
    """
    try:
        seconds = timedelta.total_seconds()
    except AttributeError:  # no method total_seconds
        one_second = np.timedelta64(1000000000, 'ns')
        # use nanoseconds to get highest possible precision in output
        seconds = timedelta / one_second
    return seconds







