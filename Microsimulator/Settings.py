import pathlib


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
        self.bformula = False
        self.f_rates = []
        self.f_cutoffs = []

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
