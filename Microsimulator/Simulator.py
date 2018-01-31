from CommandParser import CommandParser
from Wage import Wage
from Account import Account
from Calender import Calender
import random
import datetime
import numpy as np


class Simulator:
    def __init__(self):
        self.settings = None

    def simulate(self):
        command_parser = CommandParser()
        settings = command_parser.execute('commands.txt')
        self.settings = settings

        begin = datetime.datetime.strptime('4/16/2011', '%m/%d/%Y').date()
        end = datetime.datetime.strptime('4/15/2012', '%m/%d/%Y').date()
        calender = Calender(begin, end, 1080)
        households = command_parser.generate_households()

        for hh in households:
            for person in hh.people:
                if self.filter_requirements(person):
                    n_none = 0
                    weight = person.pwgtp * settings.n_years
                    if settings.seanalysis:
                        weight /= settings.clone_factor

                    no_leaves_account = None
                    for i in range(settings.clone_factor):
                        wage = Wage(person, random.random(), random.random(), settings)
                        wage.set_employer_size(random.random(), settings)
                        pr_hourly = wage.pr_hourly(settings)
                        wage.hourly = random.random < pr_hourly

                        account = Account(person, wage, weight, settings)

    def filter_requirements(self, person):
        settings = self.settings
        if not settings.government and 2 < person.cow < 6:
            return False
        if not settings.government and (person.cow == 6 or person.cow == 7):
            return False
        if person.esr == 4 or person.esr == 7:
            return False
        if person.agep >= 15 and person.wkw >= 1 and 1 <= person.cow <= 7:
            if not settings.stateofwork:
                return True
            elif (person.st == settings.stateofwork and person.powsp05 <= 0 and person.powsp12 <= 0) or \
                    person.powsp05 == settings.stateofwork or person.powsp12 == settings.stateofwork:
                return True
            else:
                return False
        else:
            return False

    def process_person(self, account, calender):
        settings = self.settings
        self.set_leaves(account, calender)

    def set_leaves(self, account, calender):
        settings = self.settings

        uniform_draw = random.random()
        cum_prob_of_leave = 0
        most_recent_leave_type = 'Own Health'
        any_leave = False

        for leave_type in settings.leavetype:
            pr_leave = self.pr_take(leave_type, account)

    def pr_take(self, leave_type, account):
        settings = self.settings
        person = account.person
        wage = account.wage

        num_children = wage.num_dep_child_u18

        bx = 0
        if leave_type == 'Own Health':
            delta = .119783 if settings.calibrate else 0
            bx = delta - 3.664033 + .0149854 * person.agep + .4782719 * wage.hourly + .3684891 * person.divorced \
                 + .7569287 * account.employerWorkerEligFMLA
            prob = np.exp(bx) / (1 + np.exp(bx))
            bx = prob * settings.leave_probability_factors[leave_type]

        elif leave_type == 'Maternity':
            if person.female == 0 or num_children == 0:
                return 0
            else:
                delta = .004768 if settings.calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) * self.pr_take_given_leave(leave_type, account)

        elif leave_type == 'New Child':
            if num_children == 0:
                return 0
            else:
                delta = .012459 if settings.calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) + self.pr_take_given_leave(leave_type, account)

        elif leave_type == 'Ill Child':
            delta = .142228 if settings.calibrate else 0
            bx = delta - 3.960923 - 1.701863 * person.nochildren + .1395203 * person.separated \
                 + .6759066 * person.divorced
            prob = np.exp(bx) / (1 + np.exp(bx))
            bx = prob * settings.leave_probability_factors[leave_type]

        elif leave_type == 'Ill Spouse':
            if person.nevermarried or person.divorced:
                return 0
            else:
                delta = -.001269 if settings.calibrate else 0
                bx = delta + self.pr_leave(leave_type, account) + self.pr_take_given_leave(leave_type, account)

        elif leave_type == 'Ill Parent':
            delta = .142228 if settings.calibrate else 0
            bx = delta - 11.92293 + .3218775 * person.agep - .0030002 * person.agep ** 2 - .9691048 * person.male \
                 + 1.198466 * person.nevermarried - .5518191 * person.colgrad
            prob = np.exp(bx) / (1 + np.exp(bx))
            bx = prob * settings.leave_probability_factors[leave_type]

        return bx * .74085585

    def pr_leave(self, leave_type, account):
        person = account.person
        wage = account.wage

        bx = 0
        if leave_type == 'Own Health':
            bx = -2.525684 + .0142925 * person.agep - .2065864 * wage.lnfamic + .4498745 * wage.hourly \
                 + .3152762 * person.divorced + .7395613 * account.employerWorkerEligFMLA

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

        prob = np.exp(bx) / (1 + np.exp(bx)) * self.settings.leave_probability_factors[leave_type]
        return prob

    def pr_take_given_leave(self, leave_type, account):
        person = account.person

        if leave_type == 'Own Health':
            bx = - 1.365028 + .0218084 * person.agep + .4299428 * person.male + .4799236 * person.lnfaminc \
                 - .7657413 * person.blachnh - .7673626 * person.hispanic + .5116349 * account.employerWorkerEligFMLA

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
