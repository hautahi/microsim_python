from Settings import Settings
import math
import random
import Calender


def o_prob_pay_group(leave):
    leave_type = leave.leave_type

    prob = []
    if leave_type == 'Own Health':
        prob = [0.161849711, 0.283236994, 0.473988439, 0.791907514]

    elif leave_type == 'Maternity':
        cut = [4.4297677, 5.139921, 6.694829, 7.870817]
        bx = 1.507677 * math.log(leave.length)
        prob = [1 / (1 + math.exp(bx - c)) for c in cut]

    elif leave_type == 'New Child':
        prob = [0.222222222, 0.333333333, 0.5, 0.77777778]

    elif leave_type == 'Ill Child':
        prob = [0.083333333, 0.083333333, 0.5, 0.666666667]

    elif leave_type == 'Ill Spouse':
        prob = [0.083333333, 0.083333333, 0.5, 0.666666667]

    elif leave_type == 'Ill Parent':
        prob = [0.083333333, 0.083333333, 0.5, 0.666666667]

    else:
        Settings.log_error('Invalid leave type')

    return prob


def pr_extend(leave_type, account):
    if not Settings.extend_leaves:
        return 0

    person = account.person
    bx = 0

    if leave_type == 'Own Health':
        bx = - 1.849637 + .082769 * person.age - .001249 * person.agesq + .431599 * person.female

    elif leave_type == 'Maternity':
        return .6154

    elif leave_type == 'New Child':
        return .5686

    elif leave_type == 'Ill Child':
        return .4

    elif leave_type == 'Ill Spouse':
        bx = + 6.358431 - .095628 * person.age - 2.290875 * account.employer_worker_elig_fmla

    elif leave_type == 'Ill Parent':
        return .5435

    else:
        Settings.log_error('Invalid leave type')

    prob = math.exp(bx) / (1 + math.exp(bx))
    return prob


def pr_extend_3(leave_type):
    if not Settings.extend_leaves:
        return 0
    if leave_type == 'Own Health':
        return 1
    return 0.25


def pr_extend_3_new(leave_type):
    if not Settings.extend_leaves:
        return 0
    return Settings.extend_probabilities[leave_type]


def ran_discrete(lst):
        cur_val = 0
        for i in range(len(lst)):
            cur_val += lst[i]
            lst[i] = cur_val
        return ran_discrete_cum(lst)


def ran_discrete_cum(lst, uniform=random.random()):
        highest = 0
        for i, prob in enumerate(lst):
            if uniform > prob:
                highest = i
            else:
                break
        return highest + 1


def days_extend(benefit_calc):
    leave = benefit_calc.leave
    uniform = leave.unifrom_draw_leave_length
    length = leave.length_no_prog

    if leave.leave_type == 'Own Health':
        original_length = ran_discrete_cum(Settings.lol_own_health_noprog, uniform=uniform)
        new_length = ran_discrete_cum(Settings.lol_own_health_prog, uniform=uniform)
        extra = new_length - original_length
        return extra if extra >= 0 else 0
    else:
        if length == 0:
            return 1
        return length * 0.25


def days_extend_new(benefit_calc):
    leave = benefit_calc.leave
    leave_type = leave.leave_type
    account = benefit_calc.account
    length = leave.length_no_prog
    uniform = leave.unifrom_draw_leave_length
    person = account.person
    original_length = 0
    new_length = 0
    extra_own_health = 0

    extend_days = Settings.extend_days[leave_type]
    extend_proportion = Settings.extend_proportions[leave_type]
    extra = extend_days + extend_proportion * length

    if leave_type == 'Own Health':
        original_length = ran_discrete_cum(Settings.lol_own_health_noprog, uniform)
        new_length = ran_discrete_cum(Settings.lol_own_health_prog, uniform)
        extra_own_health = new_length - original_length
        if extra_own_health > extra:
            extra = extra_own_health

    if extra == 0:
        extra = 1

    return extra


def pr_participate(benefit_calc, p):
    account = benefit_calc.account
    leave = benefit_calc.leave

    faminc = account.wage.family_income
    if faminc < 0:
        faminc = 1

    if p == 1:
        pay_date = Calender.weekdays_after(benefit_calc.end_date[-1], 1)
        week_num = Calender.weekdays_between(leave.begin, pay_date) // 5
        wage = 0 if len(leave.w_pay_no_prog) <= week_num else leave.w_pay_no_prog[week_num]
        diff = account.weekly_benefit if benefit_calc.topoff1 else account.weekly_benefit - wage
    else:
        diff = account.weekly_benefit

    if Settings.partrate:
        bx = -4 + 0.9531 * diff - .0000421442 * faminc
        return math.exp(bx) / (1 + math.exp(bx))
    else:
        if diff > 0:
            return 1
        return 0
