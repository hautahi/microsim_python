from Leave import Leave

class Account:
    def __init__(self, person, wage, weight, settings):
        self.person = person
        self.wage = wage
        self.weight = weight

        self.dependent_allowance = wage.num_dep_child_u18 * settings.dep_allowance
        self.wage_replacement = self.get_wage_replacement(settings)
        self.weekly_benefit = self.wage_replacement + self.dependent_allowance
        self.daily_benefit = self.weekly_benefit / 5

        self.leaves = []
        self.dates_ok = False
        self.n_leaves = 0
        self.n_need_wo_prog = 0
        self.n_need = 0
        self.employerWorkerEligFMLA = False
        self.workerEligFMLA = False
        self.employerWorkerElig = False

    def get_wage_replacement(self, settings):
        wage = self.wage
        wage_part = 0
        weekly_wage = wage.weekly_wage
        if settings.formula:
            avg_wage = 1256.47  # 2015 average weekly wage
            ratio = weekly_wage / avg_wage

            if ratio <= .3:
                wage_part = .95 * weekly_wage
            elif ratio <= .5:
                wage_part = .9 * weekly_wage
            elif ratio <= .8:
                wage_part = .8 * weekly_wage
            else:
                wage_part = .66 * weekly_wage

        elif settings.formula2:
            base = 0
            for i in range(len(settings.f_cutoffs)):
                top = settings.f_cutoffs[i]
                rate = settings.f_rates[i]
                if weekly_wage > top:
                    wage_part += rate * (top - base)
                else:
                    wage_part += rate * (weekly_wage - base) + settings.rate[i + 1] * (weekly_wage - top)
                    break
                base = top

        else:
            wage_part = weekly_wage * settings.rep_ratio

        return min(wage_part, settings.cap)

        # Log to debug here

    def new_leave(self, leave_type, length):
        leave = Leave(leave_type, length)
        self.leaves.append(leave)
        return leave
