from Settings import Settings
import Calender
import random
import datetime
import math
import Param
from enum import Enum
import numpy as np


class BenefitCalc:
    def __init__(self, account, leave):
        self.account = account
        self.leave = leave
        self.program_begin_date = Calender.weekdays_after(leave.begin, Settings.waiting_period[leave.leave_type] * 5)
        self.fmla_date = Calender.weekdays_after(leave.begin, 12 * 5)
        self.was_a_needer = False
        self.path = 0
        self.state = []
        self.begin_date = []
        self.end_date = []
        self.weekly_wage = []
        self.week_num_p = []
        self.days_p = []
        self.state_num_p = []
        self.fraction_p = []
        self.date_pay = []
        self.daily_pay = []
        self.week_num_of_day_p = []
        self.date_ben = []
        self.daily_ben = []
        self.week_num_of_day_b = []
        self.weekly_ben = []
        self.week_num_b = []
        self.state_num_b = []
        self.fraction_b = []
        self.days_b = []
        self.days = []
        self.topoff1 = False

        if leave.length_no_prog == 0:
            self.was_a_needer = True
            leave.length_no_prog = leave.length
            leave.end_no_prog = leave.end

        participate = False

        if leave.eligible:
            tur = Settings.take_up_rates[leave.leave_type]
            if random.random() <= tur or (self.was_a_needer and Settings.takeup100):
                participate = True

        if participate:
            if leave.paid:
                if leave.full_paid and Settings.topoffrate1 > 0:
                    if random.random() <= Settings.topoffrate1 and leave.length_no_prog >= Settings.topoffminlength:
                        self.topoff1 = True

                self.begin_paid_leave_elig()
            else:
                self.begin_unpaid_leave_elig()

    def begin_paid_leave_elig(self):
        leave = self.leave
        date_begin = leave.begin
        self.state.append(State.begin_paid_leave_elig)
        self.begin_date.append(date_begin)

        wait_weeks = Settings.waiting_period[leave.leave_type]

        if self.program_begin_date > leave.end_no_prog:
            self.end_date.append(leave.end_no_prog)
            self.bple_pay_during()
            self.extend_5()
        elif self.program_begin_date <= leave.end_no_prog and leave.w_pay_no_prog[wait_weeks]:
            self.end_date.append(Calender.weekdays_before(self.program_begin_date, 1))
            if self.end_date[-1] >= self.begin_date[-1]:
                self.bple_pay_during()
            self.participate_1()
            # TODO

    def participate_1(self):
        decision_date = self.end_date[-1]
        self.state.append(State.participate_1)
        self.begin_date.append(decision_date)

        pr_part = Param.pr_participate(self, 1)
        if random.random() < pr_part or (self.was_a_needer and Settings.takeup100):
            self.end_date.append(decision_date)
        elif self.was_a_needer and not Settings.takeup100:
            self.return_as_leave_needer(3)
        else:
            self.end_date.append(decision_date)
            self.continue_paid_leave()

    def participate_2(self):
        decision_date = self.end_date[-1]
        self.state.append(State.participate_2)
        self.begin_date.append(decision_date)

        pr_part = Param.pr_participate(self, 2)

        if random.random() < pr_part or (self.was_a_needer and Settings.takeup100):
            self.end_date.append(decision_date)
            self.begin_program()
        elif self.was_a_needer and not Settings.takeup100:
            self.return_as_leave_needer(3)
        else:
            self.end_date.append(decision_date)
            self.unpaid_leave_to_ol()

    def begin_program(self):
        leave = self.leave
        max_days_on_program = (Settings.max_weeks[leave.leave_type] - Settings.waiting_period[leave.leave_type]) * 5
        date_end_max = Calender.weekdays_after(self.end_date[-1], max_days_on_program)
        days_left_after_program_ends = Calender.weekdays_between(date_end_max, leave.end_no_prog)

        if days_left_after_program_ends < 0:
            self.end_date.append(leave.end_no_prog)
            self.benefits_during()
            if self.topoff1:
                self.pay_during()
            self.extend_1()
        else:
            self.end_date.append(date_end_max)
            self.benefits_during()
            if self.topoff1:
                self.pay_during()
            days_of_pay_left = self.num_days_of_original_pay() - sum(self.days_p)

            if days_of_pay_left > 0:
                if days_left_after_program_ends > 0:
                    self.receive_pay_after_program()
                else:
                    self.extend_2()
            else:
                if days_left_after_program_ends > 0:
                    self.unpaid_leave_to_ol()
                else:
                    self.end_leave()

    def continue_paid_leave(self):
        leave = self.leave

        n_days_paid_no_prog = sum(leave.days_pay_no_prog)
        if n_days_paid_no_prog == leave.length_no_prog:
            self.end_date.append(leave.end_no_prog)
            self.cpl_pay_during()
            self.extend_3()
        else:
            self.end_date.append(Calender.weekdays_after(leave.begin, n_days_paid_no_prog - 1))
            self.cpl_pay_during()
            self.participate_2()

    def pay_during(self):
        leave = self.leave
        state_num = len(self.state)

        bow = self.begin_date[-1]
        eow = self.end_date[-1]

        week_num_beg = int(math.ceil((Calender.weekdays_between(leave.begin, bow) + 1) / 5))
        week_num_end = int(math.ceil((Calender.weekdays_between(leave.begin, eow) + 1) / 5))

        if len(self.week_num_b) != week_num_end - week_num_beg + 1:
            Settings.log_error('week_num_b is wrong size')
        if self.week_num_b[0] != week_num_beg:
            Settings.log_error('week_num_b[0] is wrong')

        for i in range(week_num_end - week_num_beg + 1):
            weekly_wage = leave.w_pay_no_prog[i]
            weekly_ben = self.weekly_ben[i]
            top_off = weekly_wage - weekly_ben
            if (Settings.rep_ratio > 1 or Settings.dep_allowance > 0) and top_off < 0:
                top_off = 0
            if -0.5 < top_off < 0.5:
                top_off = 0
            if top_off < 0:
                Settings.log_error('top_off negative in pay_during')

            days_this_week = self.days_b[i]
            if days_this_week <= 0:
                Settings.log_error('days_this_week is not positive in pay_during')
            eow = Calender.weekdays_between(bow, days_this_week - 1)
            daily_top_off = top_off / days_this_week

            pointer = bow
            while pointer <= eow:
                if daily_top_off > 0:
                    self.date_pay.append(pointer)
                    self.daily_pay.append(daily_top_off)
                    self.week_num_of_day_p.append(week_num_beg + i)
                pointer += datetime.timedelta(days=1)
                pointer = Calender.advance_to_weekday(pointer)

            self.weekly_wage.append(top_off)
            self.week_num_p.append(week_num_beg + i)
            self.days_p.append(self.days_b[i])
            self.fraction_p.append(self.fraction_b[i])
            self.state_num_p.append(state_num)
            bow += datetime.timedelta(weeks=1)

        if eow != self.end_date[-1]:
            Settings.log_error("Error: End of week doesn't match in pay_during")

    def bple_pay_during(self):
        date_begin = self.begin_date[-1]
        date_end = self.end_date[-1]
        leave = self.leave
        state_num = len(self.state)

        bow = date_begin
        eow = date_end

        length = Calender.weekdays_between(date_begin, date_end) + 1
        n_weeks = length // 5
        remainder = length % 5
        fraction = True if remainder else False

        for i in range(n_weeks):
            wages = leave.w_pay_no_prog[i]
            daily_wage = wages / 5
            self.weekly_wage.append(wages)
            self.week_num_p.append(i + 1)
            self.fraction_p.append(False)
            self.days_p.append(5)
            self.state_num_p.append(state_num)

            eow = Calender.weekdays_after(bow, 4)
            pointer = bow
            while pointer <= eow:
                self.date_pay.append(pointer)
                self.daily_pay.append(daily_wage)
                self.week_num_of_day_p.append(i + 1)
                pointer += datetime.timedelta(days=1)
                pointer = Calender.advance_to_weekday(pointer)

            bow += datetime.timedelta(weeks=1)

        if fraction:
            wages = leave.w_pay_no_prog(n_weeks)
            self.weekly_wage.append(wages)
            self.week_num_p.append(n_weeks + 1)
            self.fraction_p.append(remainder)
            self.state_num_p.append(state_num)

            eow = Calender.weekdays_after(bow, remainder - 1)
            daily_wage = wages / remainder
            pointer = bow
            while pointer <= eow:
                self.date_pay.append(pointer)
                self.daily_pay.append(daily_wage)
                self.week_num_of_day_p.append(n_weeks + 1)
                pointer = Calender.weekdays_after(pointer, 1)

        if eow != date_end:
            Settings.log_error("Error: End of week is not equal to date_end at end of bple_pay_during")

    def cpl_pay_during(self):
        leave = self.leave

        bow = self.begin_date[-1]
        eow = self.end_date[-1]

        first_week = self.week_num_p[-1] if len(self.week_num_p) else 0
        for i in range(first_week, int(math.ceil(leave.length_no_prog / 5))):
            wages = leave.w_pay_no_prog[i]
            self.weekly_wage.append(wages)
            self.week_num_p.append(i)
            days = leave.days_pay_no_prog[i]
            self.days_p.append(days)
            if days == 5:
                self.fraction_p.append(False)
            else:
                self.fraction_p.append(True)
            self.state_num_p.append(len(self.state))

            daily_wage = wages / days
            eow = Calender.weekdays_after(bow, days - 1)
            pointer = bow

            while pointer <= eow:
                self.date_pay.append(pointer)
                self.daily_pay.append(daily_wage)
                self.week_num_of_day_p.append(i)

                pointer += datetime.timedelta(days=1)
                pointer = Calender.advance_to_weekday(pointer)
            bow += datetime.timedelta(weeks=1)

        if eow != self.end_date[-1]:
            Settings.log_error("Error: End of week is not equal to date_end at end of cpl_pay_during")

    def return_as_leave_needer(self, reason):
        leave = self.leave
        account = self.account

        leave.length_no_prog = None
        leave.length = 0
        leave.end_no_prog = None
        leave.begin = None
        leave.end = None
        leave.truncated = False
        leave.need = True
        leave.leave_taken_back = True
        leave.reason_taken_back = reason

        account.n_leaves -= 1
        account.n_need += 1

        self.state = []
        self.begin_date = []
        self.end_date = []
        self.days = []
        self.weekly_ben = []
        self.week_num_b = []
        self.state_num_b = []
        self.weekly_wage = []
        self.week_num_p = []
        self.fraction_p = []
        self.days_p = []
        self.state_num_p = []

    def extend_1(self):
        leave = self.leave
        leave_type = leave.leave_type
        decision_date = self.end_date[-1]

        self.state.append(State.extend_3)
        self.begin_date.append(decision_date)

        pr_extend = Param.pr_extend_1(leave_type) if Settings.extend_old else Param.pr_extend_1_new(leave_type)
        if random.random() < pr_extend:
            days_extend = Param.days_extend(self) if Settings.extend_old else Param.days_extend_new(self)
            prog_max = Settings.max_weeks[leave.leave_type] * 5 - Settings.waiting_period[leave.leave_type] * 5
            if days_extend > prog_max:
                days_extend = prog_max

            end = Calender.weekdays_after(decision_date, days_extend)
            date_prog_end = Calender.weekdays_between(self.begin_date[-1], (Settings.max_weeks[leave_type] - Settings.waiting_period[leave_type]) * 5)
            if end > date_prog_end:
                end = date_prog_end

            if decision_date < self.fmla_date < end and Settings.fmla_constraint:
                end = self.fmla_date
            leave.end = end

            self.end_date.append(decision_date)
            self.continue_program()
        else:
            self.end_date.append(decision_date)
            self.end_leave()

    def extend_3(self):
        leave = self.leave
        decision_date = self.end_date[-1]

        self.state.append(State.extend_3)
        self.begin_date.append(decision_date)

        pr_extend = Param.pr_extend_3(leave.leave_type) if Settings.extend_old else Param.pr_extend_3_new(leave.leave_type)

        if random.random() < pr_extend:
            days_extend = Param.days_extend(self) if Settings.extend_old else Param.days_extend_new(self)
            prog_max = Settings.max_weeks[leave.leave_type] * 5 - Settings.waiting_period[leave.leave_type] * 5
            if days_extend > prog_max:
                days_extend = prog_max

            end = Calender.weekdays_after(decision_date, days_extend)

            if decision_date < self.fmla_date < end and Settings.fmla_constraint:
                end = self.fmla_date
            leave.end = end

            self.end_date.append(decision_date)
            self.continue_program()
        else:
            self.end_date.append(decision_date)
            self.end_leave()

    def extend_4(self):
        leave = self.leave
        decision_date = self.end_date[-1]

        self.state.append(State.extend_4)
        self.begin_date.append(Calender.weekdays_after(decision_date, 1))

        pr_extend = Param.pr_extend(leave.leave_type, self.account)

        if random.random() < pr_extend:
            wait_days = Settings.waiting_period[leave.leave_type] * 5
            end_old = Calender.weekdays_after(leave.begin, wait_days + 4)

            if Settings.extend_old:
                leave.end(end_old)
            else:
                days_extend = Param.days_extend_new(self)
                max_weeks = Settings.max_weeks[leave.leave_type] * 5 - Settings.waiting_period[leave.leave_type] * 5
                if days_extend > max_weeks:
                    days_extend = max_weeks
                end = Calender.weekdays_after(decision_date, days_extend)
                if end < end_old:
                    end = end_old
                if decision_date < self.fmla_date and end > self.fmla_date and Settings.fmla_constraint:
                    end = self.fmla_date
                leave.end = end

            self.end_date.append(Calender.weekdays_before(self.begin_date, 1))
            self.continue_program()
        else:
            self.end_date.append(decision_date)
            self.end_leave()

    def extend_5(self):
        leave = self.leave
        leave_type = leave.leave_type
        decision_date = self.end_date[-1]

        self.state.append(State.extend_5)
        self.begin_date.append(Calender.weekdays_after(decision_date, 1))

        pr_extend = Param.pr_extend(leave_type, self.account)
        if random.random() < pr_extend:
            wait_days = Settings.waiting_period[leave_type] * 5
            end_old = Calender.weekdays_after(leave.begin, wait_days + 4)

            if Settings.extend_old:
                leave.end = end_old
            else:
                days_extend = Param.days_extend_new(self)
                program_length = Settings.max_weeks[leave_type] * 5 - Settings.waiting_period[leave_type] * 5

                if days_extend > program_length:
                    days_extend = program_length

                end = Calender.weekdays_after(decision_date, days_extend)
                if end < end_old:
                    end = end_old

                if (decision_date < self.fmla_date < end) and Settings.fmla_constraint:
                    end = self.fmla_date
                leave.end(end)

            self.end_date.append(Calender.weekdays_before(self.program_begin_date, 1))
            self.continue_program()
        else:
            self.end_date.append(decision_date)
            self.end_leave()

        pass

    def continue_program(self):
        self.state.append(State.continue_program)
        date_begin = Calender.weekdays_after(self.end_date[-1], 1)
        self.begin_date.append(date_begin)

        date_end = self.leave.end
        self.end_date.append(date_end)
        self.benefits_during()
        self.end_leave()

    def benefits_during(self):
        date_begin = self.begin_date[-1]
        date_end = self.end_date[-1]
        state_num = len(self.state)

        week_num = self.week_number(date_begin)
        daily_ben = self.account.daily_benefit

        n_days = 0
        week_ben = 0

        pointer = date_begin
        while pointer <= date_end:
            self.date_ben.append(pointer)
            self.daily_ben.append(daily_ben)
            self.week_num_of_day_b.append(week_num)

            week_ben += daily_ben
            n_days += 1

            pointer += datetime.timedelta(days=1)
            if pointer.day > 4:
                self.weekly_ben.append(week_ben)
                self.week_num_b.append(week_num)
                self.state_num_b.append(state_num)

                if n_days == 5:
                    self.fraction_b.append(False)
                else:
                    self.fraction_b.append(True)
                self.days_b.append(n_days)
                n_days = 0
                week_ben = 0
                week_num += 1

            pointer = Calender.advance_to_weekday(pointer)

        if pointer.day != 0:
            self.weekly_ben.append(week_ben)
            self.week_num_b.append(week_num)
            self.state_num_b.append(state_num)
            self.fraction_b.append(True)
            self.days_b.append(n_days)

    def end_leave(self):
        self.state.append(State.end_leave)
        self.begin_date.append(self.end_date[-1])
        self.end_date.append(self.end_date[-1])

        self.clean_up()

    def week_number(self, date):
        date_begin = self.leave.begin
        n_days = Calender.weekdays_between(date_begin, date)
        return n_days // 5 + 1 if n_days % 5 else n_days // 5

    def clean_up(self):
        leave = self.leave
        date_end = self.end_date[-1]

        if self.was_a_needer:
            leave.length_no_prog = 0
            leave.end_no_prog = Calender.weekdays_before(leave.begin, 1)

        length = Calender.weekdays_between(self.begin_date[0], date_end) + 1
        original_length = leave.length_no_prog

        n_weeks = length // 5
        if length % 5 > 0:
            n_weeks += 1

        w_pay = [0] * n_weeks
        days_pay = [0] * n_weeks
        w_ben = [0] * n_weeks
        days_ben = [0] * n_weeks

        for i in range(len(self.week_num_p)):
            w_pay[self.week_num_p[i]] += self.weekly_wage[i]
            days_pay[self.week_num_p[i]] += self.days_p[i]
        total_pay = sum(w_pay)

        for i in range(len(self.week_num_b)):
            w_ben[self.week_num_b[i]] += self.weekly_ben[i]
            days_ben[self.week_num_b[i]] += self.days_b[i]
        total_ben = sum(w_ben)

        leave.length = length
        leave.end = date_end
        leave.paid = True if total_pay > 0 else False
        leave.benefits = True if total_ben > 0 else False

        x_weeks = length / 5
        leave.leave_weeks = x_weeks
        leave.pay_amt = total_pay
        leave.benefits_amt = total_ben

        lost_product = leave.weekly_wage * x_weeks
        leave.lost_product = lost_product

        leave.uncompensated_amt = lost_product - total_pay - total_ben
        leave.w_pay = w_pay
        leave.days_pay = days_pay
        leave.w_benefits = w_ben
        leave.days_ben = days_ben

        w_pay_no_prog = leave.w_pay_no_prog
        days_pay_no_prog = leave.days_pay_no_prog
        if len(w_pay_no_prog) != len(days_pay_no_prog):
            Settings.log_error("Error: Size of days_pay_no_prog not equal to size of w_pay_no_prog")

        for i in range(len(w_pay) - len(w_pay_no_prog)):
            w_pay_no_prog.append(0)
            days_pay_no_prog.append(0)
        leave.w_pay_no_prog = w_pay_no_prog
        leave.days_pay_no_prog = days_pay_no_prog

        leave.w_pay_induced = [w_pay[i] - w_pay_no_prog[i] for i in range(len(w_pay))]

        days_benefit = 0
        days_paid = 0
        days_unpaid = 0

        self.path = 0
        state = self.state
        paid_states = {State.begin_paid_leave_elig, State.begin_paid_leave_inelig, State.continue_paid_leave,
                       State.continue_paid_leave_2, State.receive_pay_after_program}
        unpaid_states = {State.begin_unpaid_leave_elig, State.begin_unpaid_leave_inelig, State.extend_4,
                         State.extend_5, State.unpaid_leave_to_ol, State.wait}
        benefit_states = {State.begin_program, State.continue_program}
        for i in range(len(state)):
            days = Calender.weekdays_between(self.begin_date[i], self.end_date[i]) + 1

            if state[i] != State.end_leave:
                self.path += 2 ** state[i].value

            if state[i] in paid_states:
                days_paid += days
            elif state[i] in unpaid_states:
                days_unpaid += days
            elif state[i] in benefit_states:
                days_benefit += days
            else:
                days = 0

            self.days.append(days)

        leave.days_benefits = sum(days_benefit)
        leave.days_paid = sum(days_pay)

        first_date = Calender.advance_to_weekday(Settings.calender_begin)
        last_date = Calender.retreat_to_weekday(Settings.calender_end)

        leave.begin_prog_year = first_date if leave.begin < first_date else leave.begin
        leave.end_no_prog_prog_year = last_date if leave.end_no_prog > last_date else leave.end_no_prog
        leave.end_no_prog = last_date if leave.end > last_date else leave.end
        leave.length_prog_year = Calender.weekdays_between(leave.begin_prog_year, leave.end_no_prog)
        leave.length_no_prog_prog_year = 0 if leave.length_prog_year == 0 else \
            Calender.weekdays_between(leave.begin_prog_year, leave.end_no_prog_prog_year) + 1
        leave.lost_product_prog_year = leave.weekly_wage * leave.length_prog_year / 5

        w_pay_no_prog_prog_year = w_pay_no_prog.copy()
        days_pay_no_prog_prog_year = days_pay_no_prog.copy()

        if leave.pay_amt_no_prog > 0 and (leave.begin_prog_year > leave.begin or leave.end_no_prog_prog_year < leave.end_no_prog):
            self.intersect_program_year(w_pay_no_prog_prog_year, days_pay_no_prog_prog_year, leave.begin_prog_year, leave.end_no_prog_prog_year)

        leave.w_pay_no_prog_prog_year = w_pay_no_prog_prog_year
        leave.days_pay_no_prog_prog_year = days_pay_no_prog_prog_year
        leave.pay_amt_no_prog_prog_year = sum(w_pay_no_prog_prog_year)

        w_pay_prog_year = w_pay.copy()
        days_pay_prog_year = days_pay.copy()

        if leave.pay_amt > 0 and (leave.begin_prog_year > leave.begin or leave.end_prog_year < leave.end):
            self.intersect_program_year_2(w_pay_prog_year, days_pay_prog_year, leave.begin_prog_year, leave.end_prog_year, self.date_pay, self.daily_pay, self.week_num_of_day_p)

        leave.w_pay_prog_year = w_pay_prog_year
        leave.days_pay_prog_year = days_pay_prog_year
        leave.w_pay_induced_prog_year = [w_pay_prog_year[i] - w_pay_no_prog_prog_year[i] for i in range(len(w_pay_prog_year))]
        leave.pay_amt_prog_year = sum(w_pay_prog_year)

        w_ben_prog_year = w_ben.copy()
        days_ben_prog_year = days_pay.copy()

        if leave.benefits_amt > 0 and (leave.begin_prog_year > leave.begin or leave.end_prog_year < leave.end):
            self.intersect_program_year_2(w_ben_prog_year, days_ben_prog_year, leave.begin_prog_year, leave.end_prog_year, self.date_ben, self.daily_ben, self.week_num_of_day_b)

        leave.w_benefits_prog_year = w_ben_prog_year
        leave.days_benefits_prog_year = days_ben_prog_year
        leave.benefits_amt_prog_year = sum(w_ben_prog_year)
        leave.uncompensated_amt_prog_year = leave.lost_product_prog_year - leave.pay_amt_prog_year - leave.benefits_amt_prog_year

        leave.days_benefits_prog_year = sum(days_ben_prog_year)  # TODO: This gets set twice? Which one is correct?
        leave.days_paid_prog_year = days_pay_prog_year

        self.create_day_matrix()
        leave.days_unpaid = self.count_unpaid()
        leave.days_unpaid_prog_year = self.count_unpaid_prog_year()

    def begin_unpaid_leave_elig(self):
        leave = self.leave

        self.state.append(State.begin_unpaid_leave_elig)
        self.begin_date.append(leave.begin)
        wait_weeks = Settings.waiting_period[leave.leave_type]

        if self.program_begin_date > leave.end_no_prog:
            self.end_date.append(leave.end_no_prog)

    def intersect_program_year(self, amount, days, begin_year, end_year):
        bow = self.leave.begin

        for i in range(len(amount)):
            eow = Calender.weekdays_after(bow, 4)
            if eow < begin_year or bow > end_year:
                amount[i] = 0
                days[i] = 0
            elif bow < begin_year:
                n_days_overlap = Calender.weekdays_between(begin_year, eow) + 1
                n_days = days[i]
                days_rec = max(n_days_overlap - 5 + n_days, 0)
                if days_rec > 0:
                    amt_per_day = amount[i] / days[i]
                    amount[i] = amt_per_day * days_rec
                    days[i] = days_rec
                else:
                    amount[i] = 0
                    days[i] = 0
            elif eow > end_year:
                n_days_overlap = Calender.weekdays_between(bow, end_year) + 1
                n_days = days[i]
                if n_days_overlap < n_days:
                    amt_per_day = amount[i] / days[i]
                    amount[i] = amt_per_day * n_days_overlap
                    days[i] = n_days_overlap
        bow += datetime.timedelta(weeks=1)

    def intersect_program_year_2(self, amount, days, begin_year, end_year, date, daily, week_num_of_day):
        bow = self.leave.begin
        for i in range(len(amount)):
            eow = Calender.weekdays_after(bow, 4)
            if eow < begin_year or bow > end_year:
                amount[i] = 0
                days[i] = 0
            elif bow < begin_year:
                if len(date) != len(daily) or len(date) != len(week_num_of_day):
                    Settings.log_error("Error: Size of date, week_num_of_day_p, and daily_pay lists are not equal in intersect_program_year_2")

                amount[i] = 0
                days[i] = 0

                try:
                    pos = week_num_of_day.index(i)
                    for j in range(pos, len(week_num_of_day)):
                        if week_num_of_day[j] != i:
                            break
                        if date[j] <= end_year:
                            amount[i] += daily[j]
                            days[i] += 1
                except ValueError:
                    pass
            bow += datetime.timedelta(weeks=1)

    def create_day_matrix(self):
        self.day_matrix = np.asmatrix([self.daily_ben, self.daily_pay]).T

    def count_unpaid(self):
        unpaid_days = 0
        for row in self.day_matrix:
            if row.item(0) <= 0 and row.item(1) <= 0:
                unpaid_days += 1
        return unpaid_days

    def count_unpaid_prog_year(self):
        leave = self.leave
        day_matrix = self.day_matrix
        unpaid_days_prog_year = leave.days_unpaid
        if leave.begin_prog_year == leave.begin and leave.end_prog_year == leave.end:
            return unpaid_days_prog_year

        begin_difference = (leave.begin_prog_year - leave.begin).day
        for i in range(begin_difference):
            if day_matrix.item(i, 0) <= day_matrix(i, 1) <= 0:
                unpaid_days_prog_year -= 1

        end_difference = (leave.end_prog_year - leave.end).day
        for i in range(end_difference):
            if day_matrix.item(-i, 0) <= day_matrix(-i, 1) <= 0:
                unpaid_days_prog_year -= 1

        return unpaid_days_prog_year

class State(Enum):
    begin_paid_leave_elig = 0
    begin_paid_leave_inelig = 1
    begin_program = 2
    begin_unpaid_leave_elig = 3
    begin_unpaid_leave_inelig = 4
    continue_paid_leave = 5
    continue_paid_leave_2 = 6
    continue_program = 7
    participate_1 = 8
    participate_2 = 9
    participate_3 = 10
    participate_4 = 11
    extend_1 = 12
    extend_2 = 13
    extend_3 = 14
    extend_4 = 15
    extend_5 = 16
    receive_pay_after_program = 17
    unpaid_leave_to_ol = 18
    wait = 19
    end_leave = 20
