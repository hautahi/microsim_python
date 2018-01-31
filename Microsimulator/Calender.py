import datetime


class Calender:
    def __init__(self, begin, end, max_length):
        self.first_date = self.advance_to_weekday(begin)
        self.last_date = self.retreat_to_weekday(end)
        self.n_days = (self.last_date - self.first_date).days + 1
        self.end_day_dist = [1] * self.n_days
        self.unfinished_inventory = [0] * max_length

    @staticmethod
    def advance_to_weekday(date):
        # If the day is Saturday, move forward two days
        if date.weekday == 5:
            date += datetime.timedelta(days=2)
        # If the day is Sunday, move forward one day
        elif date.weekday == 6:
            date += datetime.timedelta(days=1)
        return date

    @staticmethod
    def retreat_to_weekday(date):
        # If the day is Saturday, move back one day
        if date.weekday == 5:
            date -= datetime.timedelta(days=1)
        # If the day is Sunday, move back two days
        elif date.weekday == 6:
            date -= datetime.timedelta(days=2)
        return date
