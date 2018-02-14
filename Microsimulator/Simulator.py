from CommandParser import CommandParser
from Wage import Wage
from Account import Account
import Calender
import Param
from Settings import Settings
import random
import datetime
import numpy as np
import math


class Simulator:
    def __init__(self):
        pass

    def simulate(self):
        command_parser = CommandParser()
        command_parser.execute('commands.txt')

        calender = Calender.Calender(Settings.calender_begin, Settings.calender_end, 1080)
        households = command_parser.generate_households()

        for hh in households:
            for person in hh.people:
                if self.filter_requirements(person):
                    n_none = 0
                    weight = person.pwgtp * Settings.n_years
                    if Settings.seanalysis:
                        weight /= Settings.clone_factor

                    no_leaves_account = None
                    for i in range(Settings.clone_factor):
                        wage = Wage(person, random.random(), random.random())
                        wage.set_employer_size(random.random(), random.random(), random.random())
                        pr_hourly = wage.pr_hourly()
                        wage.hourly = random.random < pr_hourly

                        account = Account(person, wage, weight)

    def filter_requirements(self, person):
        if not Settings.government and 2 < person.cow < 6:
            return False
        if not Settings.government and (person.cow == 6 or person.cow == 7):
            return False
        if person.esr == 4 or person.esr == 7:
            return False
        if person.agep >= 15 and person.wkw >= 1 and 1 <= person.cow <= 7:
            if not Settings.stateofwork:
                return True
            elif (person.st == Settings.stateofwork and person.powsp05 <= 0 and person.powsp12 <= 0) or \
                    person.powsp05 == Settings.stateofwork or person.powsp12 == Settings.stateofwork:
                return True
            else:
                return False
        else:
            return False

    def process_person(self, account, calender):
        any_leaves = self.set_leaves(account, calender)

        benefit = 0
        leaves = account.leaves
        for leave in leaves:
            if leave.length > 0:
                paid = False
                if leave.length_no_prog > 0:
                    pr_paid = self.pr_paid_leave(leave, account)
                    paid = random.random() < pr_paid
                leave.paid = paid

                this_benefit = bene

    def set_leaves(self, account, calender):

        leaves = []
        leave_num = []
        need_num = []
        l_len = []
        l_len_noprog = []
        l_len_prog = []
        uni_draw = []
        doctor = []
        hospital = []
        eligible = []
        take = []
        reason_taken_back = []

        leave_number = 0
        need_number = 0

        most_recent_leave_type, any_leave = self.any_leave_taken(account)

        if any_leave:
            maternity = True if most_recent_leave_type == 'Maternity' or most_recent_leave_type == 'New Child' \
                else False

            this_leaves = [most_recent_leave_type]

            num_leaves = 1
            pr_multiple = self.pr_multiple_leaves(most_recent_leave_type, account)
            if random.random() < pr_multiple:
                num_leaves = Param.ran_discrete(self.pr_dist_multiple_leaves(most_recent_leave_type))

            if num_leaves > 1:
                prior_type = most_recent_leave_type
                take_dist_uncond = {lt: 0 for lt in Settings.leave_types}

                for leave_type in take_dist_uncond:
                    take_dist_uncond[leave_type] = self.pr_take(leave_type, account)

                for i in range(num_leaves):
                    pr_take_this = {lt: 0 for lt in Settings.leave_types}
                    mask = []
                    remain_prob = 1
                    prob_unmasked = 0

                    for leave_type in pr_take_this:
                        if leave_type == 'Own Health' and prior_type == 'Own Health':
                            pr_take_this[leave_type] = .6576
                            mask.append(False)
                            remain_prob -= .6576

                        elif (leave_type == 'Maternity' or leave_type == 'New Child') and maternity:
                            pr_take_this[leave_type] = 0
                            mask.append(False)

                        elif leave_type == prior_type == 'Ill Parent':
                            pr_take_this[leave_type] = .6095
                            mask.append(False)
                            remain_prob -= .6095

                        else:
                            prob_unmasked += take_dist_uncond[leave_type]
                            mask.append(True)

                    factor = remain_prob / prob_unmasked if prob_unmasked > 0 else 1
                    for idx, leave_type in enumerate(Settings.leave_types):
                        if mask[idx]:
                            pr_take_this[leave_type] = take_dist_uncond[leave_type] * factor

                    uniform = random.random()
                    found = False
                    cum_prob = 0

                    for leave_type in pr_take_this:
                        cum_prob += pr_take_this[leave_type]
                        if cum_prob >= uniform:
                            prior_type = leave_type
                            found = True
                            break

                    if not found:
                        prior_type = 'Ill Parent'

                    if prior_type == 'Maternity' or prior_type == 'New Child':
                        maternity = True

                    this_leaves.append(prior_type)

            for leave_type in this_leaves:
                leave_number += 1

                pr_doctor = self.pr_doctor(leave_type, account)
                if random.random() < pr_doctor:
                    doc = True
                    pr_hospital = self.pr_hospital(leave_type, account)
                    hos = random.random() < pr_hospital
                else:
                    doc, hos = False

                doctor.append(doc)
                hospital.append(hos)

                elig = self.eligible_doctor_hospital(leave_type, account, doc, hos) and account.employerWorkerElig
                len_uniform = random.random()
                len_leave = self.length_of_leave(leave_type, account)
                length = Param.ran_discrete_cum(len_leave, uniform=len_uniform)
                if length <= 0:
                    Settings.log_error('Error: Length of leave is not positive.')

                leaves.append(leave_type)
                leave_num.append(leave_number)
                need_num.append(need_number)
                take.append(True)
                l_len_noprog.append(length)
                uni_draw.append(len_uniform)
                eligible.append(elig)
                reason_taken_back.append(0)
                l_len_prog.append(0)

        most_recent_leave_type, any_leave = self.any_leave_needed(account)

        if any_leave:
            maternity = True if most_recent_leave_type == 'Maternity' or most_recent_leave_type == 'New Child' \
                else False

            num_leaves = 1
            pr_multiple = self.pr_multiple_needs(most_recent_leave_type)
            if random.random() < pr_multiple:
                num_leaves = Param.ran_discrete(self.pr_dist_multiple_needs(most_recent_leave_type))

            this_leaves = [most_recent_leave_type]

            if num_leaves > 1:
                prior_type = most_recent_leave_type
                need_dist_uncond = {lt: 0 for lt in Settings.leave_types}

                for leave_type in need_dist_uncond:
                    need_dist_uncond[leave_type] = self.pr_need(leave_type, account)

                for i in range(num_leaves):
                    pr_take_this = {lt: 0 for lt in Settings.leave_types}
                    mask = []
                    remain_prob = 1
                    prob_unmasked = 0

                    for leave_type in pr_take_this:
                        if (leave_type == 'Maternity' or leave_type == 'New Child') and maternity:
                            pr_take_this[leave_type] = 0
                            mask.append(False)
                        else:
                            prob_unmasked += need_dist_uncond[leave_type]
                            mask.append(True)

                    factor = remain_prob / prob_unmasked if prob_unmasked > 0 else 1
                    for idx, leave_type in enumerate(Settings.leave_types):
                        if mask[idx]:
                            pr_take_this[leave_type] = need_dist_uncond[leave_type] * factor

                    uniform = random.random()
                    found = False
                    cum_prob = 0

                    for leave_type in pr_take_this:
                        cum_prob += pr_take_this[leave_type]
                        if cum_prob >= uniform:
                            prior_type = leave_type
                            found = True
                            break

                    if not found:
                        prior_type = 'Ill Parent'

                    if prior_type == 'Maternity' or prior_type == 'New Child':
                        maternity = True

                    this_leaves.append(prior_type)

                for leave_type in this_leaves:
                    leave_number += 1
                    need_number += 1

                    pr_doctor = self.pr_doctor_need(leave_type)
                    if random.random() < pr_doctor:
                        doc = True
                        pr_hospital = self.pr_hospital_need(leave_type)
                        hos = random.random() < pr_hospital
                    else:
                        doc, hos = False

                    elig = self.eligible_doctor_hospital(leave_type, account, doc, hos) and account.employerWorkerElig
                    pr_take_given_prog = self.pr_take_given_prog(leave_type, account)

                    if random.random() < pr_take_given_prog and Settings.cap:
                        if elig:
                            len_uniform = random.random()
                            len_leave = self.length_of_leave(leave_type, account)
                            length = Param.ran_discrete_cum(len_leave, uniform=len_uniform)
                            prog_max = Settings.max_weeks[leave_type] * 5
                            if length <= 0:
                                Settings.log_error('Error: Length of leave is not positive.')
                            elif length > prog_max:
                                length = prog_max

                            l_len_noprog.append(length)
                            uni_draw.append(len_uniform)

                            if length > Settings.waiting_period[leave_type] * 5:
                                take.append(True)
                                l_len_prog.append(length)
                                reason_taken_back.append(0)
                            else:
                                take.append(False)
                                l_len_prog.append(0)
                                reason_taken_back.append(1)
                        else:
                            take.append(False)
                            l_len_prog.append(0)
                            l_len_noprog.append(0)
                            uni_draw.append(0)
                            reason_taken_back.append(0)
                    else:
                        take.append(False)
                        l_len_prog.append(0)
                        l_len_noprog.append(0)
                        uni_draw.append(0)
                        reason_taken_back.append(0)

                    leave_num.append(leave_number)
                    need_num.append(need_number)
                    doctor.append(doc)
                    hospital.append(hos)
                    leaves.append(leave_type)
                    eligible.append(elig)

        max_length = 0
        n_leaves = 0
        n_need_wo_prog = 0
        n_need = 0

        for i in range(len(take)):
            length = l_len_noprog[i] + l_len_prog[i]
            l_len.append(length)
            if length > max_length:
                max_length = length
            if take[i]:
                if length <= 0:
                    Settings.log_error('Error: Leave length for taker is not positive')
                n_leaves += 1
                if l_len_noprog[i] == 0:
                    n_need_wo_prog += 1
            else:
                if length != 0:
                    Settings.log_error('Error: Leave length for non-taker is not 0')
                n_need += 1
                n_need_wo_prog += 1

        account.n_leaves = n_leaves
        account.n_need_wo_prog = n_need_wo_prog
        account.n_need = n_need

        if n_leaves > 0:
            leaves_info = [[0] for _ in range(5)] * n_leaves
            j = 0
            for i, length in enumerate(l_len):
                if length > 0:
                    leaves_info[j][5] = i
                    leaves_info[j][1] = length
                    j += 1

            no_overlap = self.assign_leaves(leaves_info, account, calender)
            account.dates_ok = no_overlap

            for row in leaves_info:
                pos = row[4]
                leave = account.new_leave(leaves[pos], row[0])
                leave.leave_num = leave_num[pos]
                leave.need_num = need_num[pos]
                leave.begin = row[1]
                leave.end = row[2]
                if row[3] == 1:
                    leave.truncated = True
                length = l_len_noprog[pos]
                leave.length_no_prog = length
                leave.unifrom_draw_leave_length = uni_draw[pos]
                leave.end_no_prog = calender.weekdays_after(leave.begin, length - 1)
                leave.need = False
                leave.doctor = doctor[pos]
                leave.hospital = hospital[pos]
                leave.eligible = eligible[pos]
                leave.reason_taken_back = 0

        for i in range(len(take)):
            if not take[i]:
                leave = account.new_leave(leaves[i], 0)
                leave.leave_num = leave_num[i]
                leave.need_num = need_num[i]
                leave.begin = 0
                leave.end = 0
                leave.truncated = False
                leave.doctor = doctor[i]
                leave.hospital = hospital[i]
                leave.eligible = eligible[i]
                leave.need = True
                leave.length_no_prog = 0
                leave.end_no_prog = 0
                leave.reason_taken_back = reason_taken_back[i]

        return len(leaves) > 0

    def pr_take(self, leave_type, account):
        person = account.person
        wage = account.wage

        num_children = wage.num_dep_child_u18

        bx = 0
        if leave_type == 'Own Health':
            delta = .119783 if Settings.calibrate else 0
            bx = delta - 3.664033 + .0149854 * person.agep + .4782719 * wage.hourly + .3684891 * person.divorced \
                 + .7569287 * account.employer_worker_elig_fmla
            prob = np.exp(bx) / (1 + np.exp(bx))
            bx = prob * Settings.leave_probability_factors[leave_type]

        elif leave_type == 'Maternity':
            if person.female == 0 or num_children == 0:
                return 0
            else:
                delta = .004768 if Settings.calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) * self.pr_take_given_leave(leave_type, account)

        elif leave_type == 'New Child':
            if num_children == 0:
                return 0
            else:
                delta = .012459 if Settings.calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) + self.pr_take_given_leave(leave_type, account)

        elif leave_type == 'Ill Child':
            delta = .142228 if Settings.calibrate else 0
            bx = delta - 3.960923 - 1.701863 * person.nochildren + .1395203 * person.separated \
                 + .6759066 * person.divorced
            prob = np.exp(bx) / (1 + np.exp(bx))
            bx = prob * Settings.leave_probability_factors[leave_type]

        elif leave_type == 'Ill Spouse':
            if person.nevermarried or person.divorced:
                return 0
            else:
                delta = -.001269 if Settings.calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) + self.pr_take_given_leave(leave_type, account)

        elif leave_type == 'Ill Parent':
            delta = .142228 if Settings.calibrate else 0
            bx = delta - 11.92293 + .3218775 * person.agep - .0030002 * person.agep ** 2 - .9691048 * person.male \
                 + 1.198466 * person.nevermarried - .5518191 * person.colgrad
            prob = np.exp(bx) / (1 + np.exp(bx))
            bx = prob * Settings.leave_probability_factors[leave_type]

        else:
            Settings.log_error('Invalid leave type')

        return bx * .74085585

    def pr_leave(self, leave_type, account):
        person = account.person
        wage = account.wage

        bx = 0
        if leave_type == 'Own Health':
            bx = -2.525684 + .0142925 * person.agep - .2065864 * wage.lnfamic + .4498745 * wage.hourly \
                 + .3152762 * person.divorced + .7395613 * account.employer_worker_elig_fmla

        elif leave_type == 'New Child':
            if person.nochildren:
                return 0
            else:
                bx = -1.167947 - .0947342 * person.agep + .8728679 * person.male + .2990525 * wage.family_income \
                     - .8850203 * person.nevermarried

        elif leave_type == 'Ill Child':
            bx = - 3.598767 - 1.763005 * person.nochildren + .924801 * person.separated + .6579277 * person.divorced

        elif leave_type == 'Ill Spouse':
            if person.nevermarried or person.divorced:
                return 0
            else:
                bx = -7.741155 + .1478521 * person.agep - .001273 * person.agep ** 2 + .799002 * person.widowed

        elif leave_type == 'Ill Parent':
            bx = -9.826241 + .2675669 * person.agep - .0025905 * person.agep ** 2 - 1.096209 * person.male \
                 + 1.096173 * person.nevermarried - .5798151 * person.colgrad

        else:
            Settings.log_error('Invalid leave type')

        prob = np.exp(bx) / (1 + np.exp(bx)) * Settings.leave_probability_factors[leave_type]
        return prob

    def pr_take_given_leave(self, leave_type, account):
        person = account.person

        if leave_type == 'Own Health':
            bx = - 1.365028 + .0218084 * person.agep + .4299428 * person.male + .4799236 * person.lnfaminc \
                 - .7657413 * person.blachnh - .7673626 * person.hispanic + .5116349 * account.employer_worker_elig_fmla

            prob = np.exp(bx) / (1 + np.exp(bx))
            return prob

        elif leave_type == 'Maternity':
            return .9677755

        elif leave_type == 'New Child':
            return .8306387

        elif leave_type == 'Ill Child':
            return .6435354

        elif leave_type == 'Ill Spouse':
            return .771771

        elif leave_type == 'Ill Parent':
            return .6706344

        else:
            Settings.log_error('Invalid leave type')

    def pr_multiple_leaves(self, leave_type, account):
        if leave_type == 'Own Health':
            return .2354

        elif leave_type == 'Maternity':
            return .2378

        elif leave_type == 'New Child':
            return .1237

        elif leave_type == 'Ill Child':
            return .2582

        elif leave_type == 'Ill Spouse':
            return .2216

        elif leave_type == 'Ill Parent':
            return .3207

        else:
            Settings.log_error('Invalid leave type')

    def pr_dist_multiple_leaves(self, leave_type):
        # prob = {lt: 0 for lt in self.settings.leave_types}
        prob = []
        if leave_type == 'Own Health':
            prob = [0] * 5
            q = [16.58, 3.73, 0.80, 0.55, 1.87]
            q_sum = sum(q)
            for i in range(len(prob)):
                prob[i] = q[i] / q_sum

        elif leave_type == 'Maternity':
            prob = [0] * 3
            prob[0] = 1

        elif leave_type == 'New Child':
            prob = [0] * 3
            q = [8.25, 4.13]
            q_sum = sum(q)
            for i in range(len(prob) - 1):
                prob[i] = q[i] / q_sum

        elif leave_type == 'Ill Child':
            prob = [0] * 5
            q = [8.47, 10.62, 3.74, 2.00, .99]
            q_sum = sum(q)
            for i in range(len(prob)):
                prob[i] = q[i] / q_sum

        elif leave_type == 'Ill Spouse':
            prob = [0] * 5
            q = [15.37, 3.30, 0.81, 0.45, 2.23]
            q_sum = sum(q)
            for i in range(len(prob)):
                prob[i] = q[i] / q_sum

        elif leave_type == 'Ill Parent':
            prob = [0] * 5
            q = [16.94, 3.88, 9.91, 0.0, 1.33]
            q_sum = sum(q)
            for i in range(len(prob)):
                prob[i] = q[i] / q_sum

        else:
            Settings.log_error('Invalid leave type')

        return prob

    def pr_doctor(self, leave_type, account):
        person = account.person

        bx = 0
        if leave_type == 'Own Health':
            bx = 1.744011 + .0296154 * person.agep - .7265564 * person.male - 2.069772 * person.lths

        elif leave_type == 'Maternity':
            return .9105083

        elif leave_type == 'New Child':
            return .44395

        elif leave_type == 'Ill Child':
            bx = .851705

        elif leave_type == 'Ill Spouse':
            bx = .9769981

        elif leave_type == 'Ill Parent':
            bx = .90958

        else:
            Settings.log_error('Invalid leave type')

        prob = np.exp(bx) / (1 + np.exp(bx))
        return prob

    def pr_hospital(self, leave_type, account):
        person = account.person
        wage = account.wage

        bx = 0
        if leave_type == 'Own Health':
            bx = - .394659 + .0121001 * person.agep - .4958134 * wage.hourly

        elif leave_type == 'Maternity':
            return .7441218

        elif leave_type == 'New Child':
            return .7380709

        elif leave_type == 'Ill Child':
            bx = .5120788

        elif leave_type == 'Ill Spouse':
            bx = .7773943

        elif leave_type == 'Ill Parent':
            bx = .7791853

        else:
            Settings.log_error('Invalid leave type')

        prob = np.exp(bx) / (1 + np.exp(bx))
        return prob

    def eligible_doctor_hospital(self, leave_type, account, doc, hos):
        if leave_type == 'Own Health':
            return doc

        elif leave_type == 'Maternity':
            return doc

        elif leave_type == 'New Child':
            return True

        elif leave_type == 'Ill Child':
            return doc or hos

        elif leave_type == 'Ill Spouse':
            return doc or hos

        elif leave_type == 'Ill Parent':
            return doc or hos

        else:
            Settings.log_error('Invalid leave type')

    def length_of_leave(self, leave_type, account):
        person = account.person

        if leave_type == 'Own Health':
            return Settings.lol_own_health_noprog

        elif leave_type == 'Maternity':
            return Settings.lol_maternity_disability

        elif leave_type == 'New Child':
            return Settings.lol_new_child_women if person.female else Settings.lol_new_child_men

        elif leave_type == 'Ill Child':
            return Settings.lol_ill_child_women if person.female else Settings.lol_ill_child_men

        elif leave_type == 'Ill Spouse':
            return Settings.lol_ill_spouse_women if person.female else Settings.lol_ill_spouse_men

        elif leave_type == 'Ill Parent':
            return Settings.lol_ill_parent_women if person.female else Settings.lol_ill_parent_men

        else:
            Settings.log_error('Invalid leave type')

    def any_leave_taken(self, account):
        uniform_draw = random.random()
        cum_prob_of_leave = 0

        for leave_type in Settings.leave_types:
            pr_leave = self.pr_take(leave_type, account)
            cum_prob_of_leave += pr_leave

            if cum_prob_of_leave > uniform_draw:
                return leave_type, True

        return None, False

    def any_leave_needed(self, account):
        uniform = random.random()
        cum_prob_of_leave = 0

        for leave_type in Settings.leave_types:
            pr_leave = self.pr_need(leave_type, account)
            cum_prob_of_leave += pr_leave

            if cum_prob_of_leave >= uniform:
                return leave_type, True

        return None, False

    def pr_need(self, leave_type, account):
        person = account.person
        calibrate = Settings.calibrate

        bx = 0
        if leave_type == 'Own Health':
            delta = -.096994 if calibrate else 0
            bx = delta - 1.101205 - .6832573 * person.lnfaminc + .5309711 * account.employer_worker_elig_fmla

        elif leave_type == 'Maternity':
            if not person.female or person.nochildren:
                return 0
            else:
                delta = .001472 if calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) * self.pr_need_given_leave(leave_type, account)
                return bx * .76075913

        elif leave_type == 'New Child':
            if person.nochildren:
                return 0
            else:
                delta = .003179 if calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) * self.pr_need_given_leave(leave_type, account)
                return bx * .76075913

        elif leave_type == 'Ill Child':
            delta = .335255 if calibrate else 0
            bx = delta - 4.600122 - 2.018847 * person.nochildren + 1.537669 * person.separated \
                 + .95226 * person.divorced

        elif leave_type == 'Ill Spouse':
            if person.nevermarried or person.divorced:
                return 0
            else:
                delta = -.000444 if calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) * self.pr_need_given_leave(leave_type, account)
                return bx * .76075913

        elif leave_type == 'Ill Parent':
            delta = -.167921 if calibrate else 0
            bx = delta - 3.605241 + .0148474 * person.age - 1.243705 * person.male + .8036237 * person.nevermarried \
                 - .3333713 * person.lnfaminc

        else:
            Settings.log_error('Invalid leave type')

        prob = np.exp(bx) / (1 + np.exp(bx))
        return prob * .76075913

    def pr_need_given_leave(self, leave_type, account):
        person = account.person

        if leave_type == 'Own Health':
            return 0

        elif leave_type == 'Maternity':
            bx = 1.258345 - .9339265 * person.lnfaminc
            return np.exp(bx) / (1 + np.exp(bx))

        elif leave_type == 'New Child':
            return .205026

        elif leave_type == 'Ill Child':
            return .4371967

        elif leave_type == 'Ill Spouse':
            return .2741959

        elif leave_type == 'Ill Parent':
            return .4451086

        else:
            Settings.log_error('Invalid leave type')

    def pr_multiple_needs(self, leave_type):
        if leave_type == 'Own Health':
            return .161244001

        elif leave_type == 'Maternity':
            return .198823

        elif leave_type == 'New Child':
            return .042329

        elif leave_type == 'Ill Child':
            return .195478287

        elif leave_type == 'Ill Spouse':
            return .123355934

        elif leave_type == 'Ill Parent':
            return .087347709

        else:
            Settings.log_error('Invalid leave type')

    def pr_dist_multiple_needs(self, leave_type):
        if leave_type == 'Own Health':
            return [0.668133073, 0.255659655, 0.076207272]

        elif leave_type == 'Maternity':
            return [1, 0, 0]

        elif leave_type == 'New Child':
            return [0.77453356, 0.22546644, 0]

        elif leave_type == 'Ill Child':
            return [0.562208829, 0.22933475, 0.208457696]

        elif leave_type == 'Ill Spouse':
            return [0.154727589, 0.705612393, 0.139660018]

        elif leave_type == 'Ill Parent':
            return [0.897980908, 0, 0.102019092]

        else:
            Settings.log_error('Invalid leave type')

    def pr_doctor_need(self, leave_type):
        if leave_type == 'Own Health':
            return .8808665

        elif leave_type == 'Maternity':
            return .9561921

        elif leave_type == 'New Child':
            return .3346132

        elif leave_type == 'Ill Child':
            return .9716478

        elif leave_type == 'Ill Spouse':
            return .9663462

        elif leave_type == 'Ill Parent':
            return .9902155

        else:
            Settings.log_error('Invalid leave type')

    def pr_hospital_need(self, leave_type):
        if leave_type == 'Own Health':
            return .1679876

        elif leave_type == 'Maternity':
            return .3536807

        elif leave_type == 'New Child':
            return .4767099

        elif leave_type == 'Ill Child':
            return .570265

        elif leave_type == 'Ill Spouse':
            return .5660124

        elif leave_type == 'Ill Parent':
            return .8519646

        else:
            Settings.log_error('Invalid leave type')

    def pr_take_given_prog(self, leave_type, account):
        person = account.person

        bx = 0
        if leave_type == 'Own Health':
            bx = 2.987098 - .8360153 * person.lnfaminc

        elif leave_type == 'Maternity':
            return .4236814

        elif leave_type == 'New Child':
            return .2997617

        elif leave_type == 'Ill Child':
            bx = 4.124997 - 1.272222 * person.lnfaminc

        elif leave_type == 'Ill Spouse':
            return .361724

        elif leave_type == 'Ill Parent':
            bx = 4.14044 - 1.207769 * person.lnfaminc

        else:
            Settings.log_error('Invalid leave type')

        prob = np.exp(bx) / (1 + np.exp(bx))
        return prob

    def pr_unfinished(self, length):
        ln_len = math.log(length)
        ln_len_sq = ln_len ** 2
        bx = -2.010323 - .2502718 * ln_len + .0939005 * ln_len_sq

        prob = math.exp(bx) / (1 - math.exp(bx))
        num_leaves = 1.842856 - .2728155 * ln_len + .0309899 * ln_len_sq

        return prob / num_leaves

    def assign_leaves(self, leaves_info, account, calender):
        no_overlap = True
        mask_beg = []
        mask_end = []

        unfinished_inventory = calender.unfinished_inventory
        n_days = calender.n_days
        end_day_dist = calender.end_day_dist

        any_unfinished = False
        row_unfinished = None

        for row in leaves_info:
            length = row[0]
            if not any_unfinished and unfinished_inventory[length - 1] > 0:
                unfinished_inventory[length - 1] -= 1
                any_unfinished = True
                row_unfinished = row
                row[3] = 1
            pr_unfinished = self.pr_unfinished(length)
            if random.random() < pr_unfinished:
                if not any_unfinished:
                    any_unfinished = True
                    row_unfinished = row
                else:
                    unfinished_inventory[length - 1] += 1

        if any_unfinished:
            end_day = n_days
            beg_day = n_days - row_unfinished[0] + 1
            mask_beg.append(beg_day)
            mask_end.append(end_day)
            date_beg = Calender.weekdays_after(calender.first_date, beg_day - 1)
            date_end = Calender.weekdays_after(date_beg, end_day - 1)
            calender.first_date = date_end
            row_unfinished[1] = date_beg  # TODO: Convert this from date to number of days since 01/01/1960
            row_unfinished[2] = date_end

            if len(leaves_info) == 1:
                return True

        ev = sum(end_day_dist) / n_days
        p_weight = [0] * n_days

        for i in range(len(n_days)):
            w = ev / end_day_dist[i]
            p_weight[i] = 2 * w if w >= 1 else w / 2

        for row in leaves_info:
            if row[3] == 0:
                length = row[0]
                for i in range(len(mask_beg)):
                    extend_end = mask_end[i] + length - 1
                    for j in range(mask_beg[i], extend_end + 1):
                        if 0 <= j <= n_days:
                            p_weight[j] = 1

                    denom = sum(p_weight)
                    end_day = 1

                    if denom > 0:
                        p_weight[:] = [w / denom for w in p_weight]
                        end_day = Param.ran_discrete(p_weight)
                    else:
                        uniform = random.random()
                        end_day = int(uniform * n_days) + 1
                        if end_day > n_days:
                            end_day = n_days
                            no_overlap = False
                    beg_day = end_day - length + 1
                    mask_beg.append(beg_day)
                    mask_end.append(end_day)
                    date_beg = calender.weekdays_after(calender.first_date, beg_day - 1)
                    date_end = calender.weekdays_after(date_beg, end_day - 1)
                    calender.first_date = date_end
                    row_unfinished[1] = date_beg
                    row_unfinished[2] = date_end
                    end_day_dist[end_day - 1] += account.weight

        return no_overlap

    def pr_paid_leave(self, leave, account):
        person = account.person
        wage = account.wage
        leave_type = leave.leave_type

        bx = 0
        if leave_type == 'Own Health':
            bx = - 6.429768 + 1.112856 * account.employer_worker_elig_fmla - .8137799 * wage.hourly \
                 + .1506044 * person.age - .0014772 * person.agesq + .9326934 * person.lnfaminc

        elif leave_type == 'Maternity':
            bx = - 6.061317 + 1.657273 * person.lnfaminc

        elif leave_type == 'New Child':
            bx = - 4.408498 + 2.269567 * account.employer_worker_elig_fmla + 1.080977 * person.lnfaminc

        elif leave_type == 'Ill Child':
            bx = 2.833213 - 2.484907 * wage.hourly

        elif leave_type == 'Ill Spouse':
            bx = 2.685577 - 2.084803 * wage.hourly

        elif leave_type == 'Ill Parent':
            bx = - .8967988 + .779754 * person.lnfaminc - 1.993381 * wage.hourly

        else:
            Settings.log_error('Invalid leave type')

        prob = np.exp(bx) / (1 + np.exp(bx))
        return prob

    def benefits(self, leave, account):
        person = account.person
        wage = account.wage

        weekly_wage = wage.weekly_wage
        leave.weekly_wage = weekly_wage
        weeks_on_leave = leave.length_no_prog / 5

        n_weeks = math.ceil(weeks_on_leave)
        full_weeks = math.floor(weeks_on_leave)
        fraction = weeks_on_leave - n_weeks
        fraction_days = leave.length_no_prog % 5

        w_pay = [0]
        days_pay = [0]

        if n_weeks > 0:
            w_pay = [0] * int(n_weeks)
            days_pay = [0] * int(n_weeks)

            if leave.paid:
                pay_group = self.pay_group(leave, account)
                pay_stats = Settings.part_pay[leave.leave_type]

                if pay_group == 6:
                    self.partial_pay_every_week(w_pay, days_pay, full_weeks, weekly_wage, 1, fraction_days, fraction)
                elif pay_group == 1 or pay_group == 2:
                    frac_pay = 0.125 if pay_group == 1 else .375
                    self.weeks_paid(w_pay, days_pay, pay_stats, 0, weeks_on_leave, full_weeks,
                                    weekly_wage, frac_pay, fraction_days, fraction)
                elif pay_group == 3:
                    frac_pay = .5
                    self.weeks_paid(w_pay, days_pay, pay_stats, 1, weeks_on_leave, full_weeks,
                                    weekly_wage, frac_pay, fraction_days, fraction)
                elif pay_group == 4 or pay_group == 5:
                    frac_pay = 0.625 if pay_group == 5 else .875
                    self.weeks_paid(w_pay, days_pay, pay_stats, 0, weeks_on_leave, full_weeks,
                                    weekly_wage, frac_pay, fraction_days, fraction)
                else:
                    Settings.log_error('Error: Pay Group out of bound')

        leave.pay_amt_no_prog = sum(w_pay)
        leave.w_pay_no_prog = w_pay
        leave.days_pay_no_prog = sum(days_pay)

    def pay_group(self, leave, account):
        pr_full_pay = self.pr_full_pay(leave, account)
        if random.random() < pr_full_pay:
            return 6
        else:
            prob = self.o_prob_pay_group(leave)
            uniform = random.random()

            for i, p in enumerate(prob):
                if uniform < p:
                    return i
            return 5

    def pr_full_pay(self, leave, account):
        person = account.person
        wage = account.wage
        leave_type = leave.leave_type
        ln_length = math.log(leave.length)

        bx = 0
        if leave_type == 'Own Health':
            bx = 1.292053 - 1.210179 * wage.hourly + .0271334 * person.age + .4222762 * person.lnfaminc \
                 - .9217541 * ln_length

        elif leave_type == 'Maternity':
            bx = 5.07015 - 1.296848 * wage.hourly - 1.051936 * ln_length

        elif leave_type == 'New Child':
            bx = 5.701751 - 1.460606 * ln_length

        elif leave_type == 'Ill Child':
            return .938284

        elif leave_type == 'Ill Spouse':
            bx = 1.214342 + .7277014 * person.lnfaminc

        elif leave_type == 'Ill Parent':
            bx = - 3.955898 + 1.495486 * person.lnfaminc

        else:
            Settings.log_error('Invalid leave type')

        prob = np.exp(bx) / (1 + np.exp(bx))
        return prob

    def o_prob_pay_group(self, leave):
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

    def weeks_paid(self, w_pay, days_pay, pay_stats, index, weeks_on_leave, full_weeks, weekly_wage, frac_pay, fraction_days, fraction):
        if random.random() < pay_stats[index][0]:
            self.partial_pay_every_week(w_pay, days_pay, full_weeks, weekly_wage, frac_pay, fraction_days, fraction)
        elif random.random() < pay_stats[index][1]:
            self.full_pay_some_weeks(w_pay, days_pay, weeks_on_leave, weekly_wage, frac_pay)
        else:
            self.partial_pay_some_weeks(w_pay, days_pay, weeks_on_leave, weekly_wage, frac_pay)

    def partial_pay_every_week(self, w_pay, days_pay, full_weeks, weekly_wage, frac_pay, fraction_days, fraction):
        for i in range(full_weeks):
            w_pay[i] = frac_pay * weekly_wage
            days_pay[i] = 5
        if fraction_days > 0:
            w_pay[full_weeks] = fraction * frac_pay * weekly_wage
            days_pay[full_weeks] = fraction_days

    def full_pay_some_weeks(self, w_pay, days_pay, weeks_on_leave, weekly_wage, frac_pay):
        weeks_paid = frac_pay * weeks_on_leave
        full_weeks = int(math.floor(weeks_paid))
        fraction_last_week = weeks_paid - full_weeks

        for i in range(full_weeks):
            w_pay[i] = weekly_wage
            days_pay[i] = 5
        if fraction_last_week > 0:
            w_pay[full_weeks] = fraction_last_week * weekly_wage
            days_pay[full_weeks] = round(fraction_last_week * 5)

    def partial_pay_some_weeks(self, w_pay, days_pay, weeks_on_leave, weekly_wage, frac_pay):
        p = math.sqrt(frac_pay)

        weeks_paid = p * weeks_on_leave
        full_weeks = int(math.floor(weeks_paid))
        fraction_last_week = weeks_paid - full_weeks

        for i in range(full_weeks):
            w_pay[i] = p * weekly_wage
            days_pay[i] = 5
        if fraction_last_week > 0:
            w_pay[full_weeks] = fraction_last_week * p * weekly_wage
            days_pay[full_weeks] = round(fraction_last_week * 5)
