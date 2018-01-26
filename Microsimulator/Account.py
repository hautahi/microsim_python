class Account:
    def __init__(self, person, wage, weight):
        self.person = person
        self.wage = wage
        self.leaves = []
        self.dates_ok = False
        self.n_leaves = 0
        self.n_need_wo_prog = 0
        self.n_need = 0
        self.employerWorkerEligFMLA = False
        self.workerEligFMLA = False
        self.employerWorkerElig = False
        self.weekly_benefit = 0
        self.dependent_allowance = 0
        self.wage_replacement = 0
        self.daily_benefit = 0
        self.weight = weight
