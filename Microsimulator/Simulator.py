from CommandParser import CommandParser
from Wage import Wage
from Account import Account
import random


class Simulator:
    def __init__(self):
        self.settings = None

    def simulate(self):
        command_parser = CommandParser()
        settings = command_parser.execute('commands.txt')
        self.settings = settings
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
