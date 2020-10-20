import timeit


def _time_string(time_value):
    """hrs:mins:secs"""
    minutes, seconds = divmod(time_value, 60)
    hours, minutes = divmod(minutes, 60)
    return '%d:%02d:%02d' % (hours, minutes, seconds)


class Timer(object):
    """Measures execution time of code.
    For an executable script, only one instance of Timer should suffice.
    If different parts of the script need to be timed individually, use laps.
    """

    def __init__(self):
        self.__start_time = timeit.default_timer()
        self.__laps = [0.0]

    def _new_lap(self):
        lap_time = timeit.default_timer() - self.__start_time
        self.__laps.append(lap_time)
        self.__start_time = timeit.default_timer()
        return lap_time

    @property
    def lap_time(self):
        return _time_string(self._new_lap())

    @property
    def total_time(self):
        self._new_lap()
        return _time_string(sum(self.__laps))
