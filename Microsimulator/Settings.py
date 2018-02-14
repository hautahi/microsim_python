import pathlib
import pandas as pd
import datetime


class Settings:
    INPUT_FOLDER = 'input/'
    OUTPUT_FOLDER = 'output/'
    PARAMS_FOLDER = 'parameters/'
    log = open('output/logtemp.txt', 'w+')

    debug_file = None
    main_file = None
    leaves_file = None
    weekly = None
    states = None
    benefit = None
    employer_pay_file = None
    doctor_file = None
    include_file = None

    partrate = False
    calibrate = False
    clone_factor = 1
    dep_allowance = 0
    level = 8

    fmla_eligr = False
    ma_uib_eligr = False
    earnings_threshold = None
    weeks_threshold = None
    annual_hours_threshold = None
    employer_size_threshold = None
    eligibility_expression = 'All'

    leave_types = ['Own Health', 'Maternity', 'New Child', 'Ill Child', 'Ill Spouse', 'Ill Parent']

    leave_reasons = {'Own Health': 1,
                     'Maternity': 1,
                     'New Child': 1,
                     'Ill Child': 1,
                     'Ill Spouse': 1,
                     'Ill Parent': 1}

    extend_days = leave_reasons.copy()
    extend_proportions = leave_reasons.copy()
    extend_probabilities = leave_reasons.copy()
    extend_leaves = False
    extend_old = False

    fmla_constraint = False
    formula = False
    formula_2 = False
    f_rates = []  # Called '_rates' in original
    f_cutoffs = []  # Called '_brackets' in original

    government = True
    leave_probability_factors = leave_reasons.copy()
    max_weeks = leave_reasons.copy()
    missing_string = '.'
    takeup100 = None
    spin = False
    rep_ratio = 1.0
    seanalysis = False
    selfemployed = False
    stateofwork = None

    take_up_rates = leave_reasons.copy()
    topoffminlength = 0
    topoffrate1 = 0
    waiting_period = leave_reasons.copy()
    cap = None
    n_years = 1.0
    seed = None

    lol_own_health_noprog = None
    lol_own_health_prog = None
    lol_maternity_disability = None
    lol_new_child_men = None
    lol_new_child_women = None
    lol_ill_child_men = None
    lol_ill_child_women = None
    lol_ill_spouse_men = None
    lol_ill_spouse_women = None
    lol_ill_parent_men = None
    lol_ill_parent_women = None
    prdist_u10 = None
    prdist_10_49 = None
    prdist_50_99 = None
    prdist_100_499 = None

    calender_begin = datetime.datetime.strptime('4/16/2011', '%m/%d/%Y').date()
    calender_end = datetime.datetime.strptime('4/15/2012', '%m/%d/%Y').date()

    @classmethod
    def load_distributions(cls, file_location):
        df = pd.read_csv(cls.PARAMS_FOLDER + file_location, sep='\t')
        df.columns = ['num', 'prob']
        return df

    @classmethod
    def load_all_distributions(cls):
        cls.lol_own_health_noprog = cls.load_distributions("length OWN HEALTH 2 noprog.txt")
        cls.lol_own_health_prog = cls.load_distributions("length OWN HEALTH 2 prog.txt")
        cls.lol_maternity_disability = cls.load_distributions("length MATERNITY-DISABILITY 3.txt")
        cls.lol_new_child_men = cls.load_distributions("length NEW CHILD men 2.txt")
        cls.lol_new_child_women = cls.load_distributions("length NEW CHILD women 2.txt")
        cls.lol_ill_child_men = cls.load_distributions("length ILL CHILD men 2.txt")
        cls.lol_ill_child_women = cls.load_distributions("length ILL CHILD women 2.txt")
        cls.lol_ill_spouse_men = cls.load_distributions("length ILL SPOUSE men 2.txt")
        cls.lol_ill_spouse_women = cls.load_distributions("length ILL SPOUSE women 2.txt")
        cls.lol_ill_parent_men = cls.load_distributions("length ILL PARENT men 2.txt")
        cls.lol_ill_parent_women = cls.load_distributions("length ILL PARENT women 2.txt")
        cls.prdist_u10 = cls.load_distributions("Prob Employer Size lt10.txt")
        cls.prdist_10_49 = cls.load_distributions("Prob Employer Size 10-49.txt")
        cls.prdist_50_99 = cls.load_distributions("Prob Employer Size 50-99.txt")
        cls.prdist_100_499 = cls.load_distributions("Prob Employer Size 100-499.txt")

    part_pay = {'Own Health': [[.6329781, .3273122], [.8209731, .3963387], [.9358463, .3633615]],
                'Maternity': [[.4285737, .2745598], [.4975566, .5249832], [.7693701, 1]],
                'New Child': [[.345167, .3324799], [.5689154, .2251773], [.7574125, .8048598]],
                'Ill Child': [[1, .3], [1, .3], [1, .3]],
                'Ill Spouse': [[0, 1], [1, .3], [.6951003, 1]],
                'Ill Parent': [[.513468, .3], [.8721353, 1], [1, .3]]}

    def set_up_directories(self):
        # Create folders for input, output, and parameter files
        pathlib.Path(self.INPUT_FOLDER).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.PARAMS_FOLDER).mkdir(parents=True, exist_ok=True)

        self.log = open(self.OUTPUT_FOLDER + 'log.txt', 'w+')

    @classmethod
    def log_error(cls, message):
        cls.log.write(message)
        cls.log.close()
        exit()

    # def __init__(self):
    #     self.INPUT_FOLDER = 'input/'
    #     self.OUTPUT_FOLDER = 'output/'
    #     self.PARAMS_FOLDER = 'parameters/'
    #     self.log = open('output/logtemp.txt', 'w+')
    #
    #     self.debug_file = None
    #     self.main_file = None
    #     self.leaves_file = None
    #     self.weekly = None
    #     self.states = None
    #     self.benefit = None
    #     self.employer_pay_file = None
    #     self.doctor_file = None
    #     self.include_file = None
    #
    #     self.partrate = False
    #     self.calibrate = False
    #     self.clone_factor = 1
    #     self.dep_allowance = 0
    #     self.level = 8
    #
    #     self.fmla_eligr = False
    #     self.ma_uib_eligr = False
    #     self.earnings_threshold = None
    #     self.weeks_threshold = None
    #     self.annual_hours_threshold = None
    #     self.employer_size_threshold = None
    #     self.eligibility_expression = 'All'
    #
    #     self.leave_types = ['Own Health', 'Maternity', 'New Child', 'Ill Child', 'Ill Spouse', 'Ill Parent']
    #
    #     leave_reasons = {'Own Health': 1,
    #                      'Maternity': 1,
    #                      'New Child': 1,
    #                      'Ill Child': 1,
    #                      'Ill Spouse': 1,
    #                      'Ill Parent': 1}
    #
    #     self.extend_days = leave_reasons.copy()
    #     self.extend_proportions = leave_reasons.copy()
    #     self.extend_probabilities = leave_reasons.copy()
    #     self.extend_leaves = False
    #     self.extend_old = False
    #
    #     self.fmla_constraint = False
    #     self.formula = False
    #     self.f_rates = []  # Called '_rates' in original
    #     self.f_cutoffs = []  # Called '_brackets' in original
    #
    #     self.government = True
    #     self.leave_probability_factors = leave_reasons.copy()
    #     self.max_weeks = leave_reasons.copy()
    #     self.missing_string = '.'
    #     self.takeup100 = None
    #     self.spin = False
    #     self.rep_ratio = 1.0
    #     self.seanalysis = False
    #     self.selfemployed = False
    #     self.stateofwork = None
    #
    #     self.take_up_rates = leave_reasons.copy()
    #     self.topoffminlength = 0
    #     self.topoffrate1 = 0
    #     self.waiting_period = leave_reasons.copy()
    #     self.cap = None
    #     self.n_years = 1.0
    #     self.seed = None
    #
    #     self.lol_own_health_noprog = self.load_distributions("length OWN HEALTH 2 noprog.txt")
    #     self.lol_own_health_prog = self.load_distributions("length OWN HEALTH 2 prog.txt")
    #     self.lol_maternity_disability = self.load_distributions("length MATERNITY-DISABILITY 3.txt")
    #     self.lol_new_child_men = self.load_distributions("length NEW CHILD men 2.txt")
    #     self.lol_new_child_women = self.load_distributions("length NEW CHILD women 2.txt")
    #     self.lol_ill_child_men = self.load_distributions("length ILL CHILD men 2.txt")
    #     self.lol_ill_child_women = self.load_distributions("length ILL CHILD women 2.txt")
    #     self.lol_ill_spouse_men = self.load_distributions("length ILL SPOUSE men 2.txt")
    #     self.lol_ill_spouse_women = self.load_distributions("length ILL SPOUSE women 2.txt")
    #     self.lol_ill_parent_men = self.load_distributions("length ILL PARENT men 2.txt")
    #     self.lol_ill_parent_women = self.load_distributions("length ILL PARENT women 2.txt")
    #     self.prdist_u10 = self.load_distributions("Prob Employer Size lt10.txt")
    #     self.prdist_10_49 = self.load_distributions("Prob Employer Size 10-49.txt")
    #     self.prdist_50_99 = self.load_distributions("Prob Employer Size 50-99.txt")
    #     self.prdist_100_499 = self.load_distributions("Prob Employer Size 100-499.txt")
    #
    #     self.part_pay = {'Own Health': [[.6329781, .3273122], [.8209731, .3963387], [.9358463, .3633615]],
    #                      'Maternity': [[.4285737, .2745598], [.4975566, .5249832], [.7693701, 1]],
    #                      'New Child': [[.345167, .3324799], [.5689154, .2251773], [.7574125, .8048598]],
    #                      'Ill Child': [[1, .3], [1, .3], [1, .3]],
    #                      'Ill Spouse': [[0, 1], [1, .3], [.6951003, 1]],
    #                      'Ill Parent': [[.513468, .3], [.8721353, 1], [1, .3]]}


def log_error(message):
    Settings.log.write(message)
    Settings.log.close()
    exit()


Settings.load_all_distributions()
