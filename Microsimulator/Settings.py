import pathlib
import pandas as pd


class Settings:
    def __init__(self):
        self.INPUT_FOLDER = 'input/'
        self.OUTPUT_FOLDER = 'output/'
        self.PARAMS_FOLDER = 'parameters/'
        self.log = open('output/logtemp.txt', 'w+')

        self.debug_file = None
        self.main_file = None
        self.leaves_file = None
        self.weekly = None
        self.states = None
        self.benefit = None
        self.employer_pay_file = None
        self.doctor_file = None
        self.include_file = None

        self.partrate = False
        self.calibrate = False
        self.clone_factor = 1
        self.dep_allowance = 0
        self.level = 8

        self.fmla_eligr = False
        self.ma_uib_eligr = False
        self.earnings_threshold = None
        self.weeks_threshold = None
        self.annual_hours_threshold = None
        self.employer_size_threshold = None
        self.eligibility_expression = 'All'

        self.leave_types = ['Own Health', 'Maternity', 'New Child', 'Ill Child', 'Ill Spouse', 'Ill Parent']

        leave_reasons = {'Own Health': 1,
                         'Maternity': 1,
                         'New Child': 1,
                         'Ill Child': 1,
                         'Ill Spouse': 1,
                         'Ill Parent': 1}

        self.extend_days = leave_reasons.copy()
        self.extend_proportions = leave_reasons.copy()
        self.extend_probabilities = leave_reasons.copy()
        self.extend_leaves = False
        self.extend_old = False

        self.fmla_constraint = False
        self.formula = False
        self.f_rates = []  # Called '_rates' in original
        self.f_cutoffs = []  # Called '_brackets' in original

        self.government = True
        self.leave_probability_factors = leave_reasons.copy()
        self.max_weeks = leave_reasons.copy()
        self.missing_string = '.'
        self.takeup100 = None
        self.spin = False
        self.rep_ratio = 1.0
        self.seanalysis = False
        self.selfemployed = False
        self.stateofwork = None

        self.take_up_rates = leave_reasons.copy()
        self.topoffminlength = 0
        self.topoffrate1 = 0
        self.waiting_period = leave_reasons.copy()
        self.cap = None
        self.n_years = 1.0
        self.seed = None

        self.lol_own_health_noprog = self.load_distributions("length OWN HEALTH 2 noprog.txt")
        self.lol_own_health_prog = self.load_distributions("length OWN HEALTH 2 prog.txt")
        self.lol_maternity_disability = self.load_distributions("length MATERNITY-DISABILITY 3.txt")
        self.lol_new_child_men = self.load_distributions("length NEW CHILD men 2.txt")
        self.lol_new_child_women = self.load_distributions("length NEW CHILD women 2.txt")
        self.lol_ill_child_men = self.load_distributions("length ILL CHILD men 2.txt")
        self.lol_ill_child_women = self.load_distributions("length ILL CHILD women 2.txt")
        self.lol_ill_spouse_men = self.load_distributions("length ILL SPOUSE men 2.txt")
        self.lol_ill_spouse_women = self.load_distributions("length ILL SPOUSE women 2.txt")
        self.lol_ill_parent_men = self.load_distributions("length ILL PARENT men 2.txt")
        self.lol_ill_parent_women = self.load_distributions("length ILL PARENT women 2.txt")
        self.prdist_u10 = self.load_distributions("Prob Employer Size lt10.txt")
        self.prdist_10_49 = self.load_distributions("Prob Employer Size 10-49.txt")
        self.prdist_50_99 = self.load_distributions("Prob Employer Size 50-99.txt")
        self.prdist_100_499 = self.load_distributions("Prob Employer Size 100-499.txt")

    def set_up_directories(self):
        # Create folders for input, output, and parameter files
        pathlib.Path(self.INPUT_FOLDER).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.PARAMS_FOLDER).mkdir(parents=True, exist_ok=True)

        self.log = open(self.OUTPUT_FOLDER + 'log.txt', 'w+')

    def log_error(self, message):
        self.log.write(message)
        self.log.close()
        exit()

    def load_distributions(self, file_location):
        df = pd.read_csv(self.PARAMS_FOLDER + file_location, sep='\t')
        df.columns = ['num', 'prob']
        return df
