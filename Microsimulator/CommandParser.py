from Settings import Settings
import pandas as pd
from CHousehold import CHousehold
from CPerson import CPerson
import random


class CommandParser:
    def __init__(self):
        self.settings = Settings()
        self.household_files = None
        self.person_files = None

    def execute(self, commands_file):
        commands = self.get_commands(commands_file)
        self.parse_commands(commands)

        waiting_period = self.settings.waiting_period
        for leave_type in waiting_period:
            waiting_period[leave_type] += self.settings.max_weeks[leave_type]

        if self.settings.spin:
            self.settings.seed = random.random()

        return self.settings

    def get_commands(self, commands_file):
        # Check if commands file exists
        cmd_f = None
        try:
            cmd_f = open(commands_file, 'r')  # Text file with commands
        except FileNotFoundError:
            self.settings.log_error('Commands file was  not found')

        # Read every line in file and get the commands from them
        removed_comments = ''
        for line in cmd_f:
            # Skip lines that start with '*' because they are comments
            if line[0] != '*':
                removed_comments += line
        cmd_f.close()

        # Replace all new lines with spaces
        removed_comments = removed_comments.replace('\n', ' ')

        # Commands are separated by a semicolon
        commands = [c.strip() for c in removed_comments.split(';') if c != '']

        # Convert commands from list to dictionary where key is the command name and value is the fields
        commands_dict = {}
        for command in commands:
            command = command.split(' ', 1)
            cmd_type = command[0].lower()

            if cmd_type in commands_dict:
                self.settings.log_error('Command Error: ' + cmd_type.upper() + ' appears multiple times')
            commands_dict[cmd_type] = commands[1]

        return commands_dict

    def parse_commands(self, commands):
        settings = self.settings

        try:
            self.process_file_cmd(commands['file'])
            self.process_max_weeks(commands['maxweeks'])
            self.process_take_up_rates(commands['takeuprates'])
            self.process_waiting_period(commands['waitingperiod'])
        except KeyError as e:
            missing_command = e.args[0].upper()
            self.settings.log_error('Command Error: ' + missing_command + ' is required but was not supplied')

        if 'benefiteffect' in commands:
            settings.partrate = self.parse_boolean(commands, 'benefiteffect')

        if 'calibrate' in commands:
            settings.calibrate = self.parse_boolean(commands, 'calibrate')

        if 'clonefactor' in commands:
            settings.clone_factor = self.process_clone_factor(commands['clonefactor'])

        if 'dependentallowance' in commands:
            settings.dep_allowance = self.process_dependent_allowance(commands['dependentallowance'])

        if 'detail' in commands:
            settings.level = self.process_detail(commands['detail'])

        if 'eligibilityrules' in commands:
            self.process_eligibility_rules(commands['eligibilityrules'])

        if 'extendleaves' in commands:
            settings.extend_leaves = self.parse_boolean(commands, 'extendleaves')

        if 'extendold' in commands:
            settings.extend_old = self.parse_boolean(commands, 'extendold')

        if settings.extend_leaves and not settings.extend_old:
            try:
                self.process_extend_probabilities(commands['extendprob'])
                self.process_extend_days(commands['extenddays'])
                self.process_extend_proportions(commands['extendproportions'])
            except KeyError as e:
                missing_command = e.args[0]
                self.settings.log_error('EXTENDLEAVES is "Yes" and EXTENDOLD is "No" or not supplied, so ' +
                               missing_command + ' must be supplied')

        if 'fmlaprotectionconstraint' in commands:
            settings.fmla_constraint = self.parse_boolean(commands, 'fmlaprotectionconstraint')

        if 'formula' in commands:
            settings.bformula = self.parse_boolean(commands, 'formula')

        if 'formula2' in commands:
            self.process_formula2(commands['formula2'])
            settings.bformula = False

        if 'government' in commands:
            settings.government = self.parse_boolean(commands, 'government')

        if 'leaveprobabilityfactors' in commands:
            self.process_leave_probability_factors(commands['leaveprobabilityfactors'])

        if 'missingvalue' in commands:
            settings.missing_string = commands['missingvalue']

        if 'needersfullyparticipate' in commands:
            settings.takeup100 = self.parse_boolean(commands, 'needersfullyparticipate')

        if 'randomseed' in commands:
            settings.spin = self.parse_boolean(commands, 'randomseed')

        if 'replacementratio' in commands:
            self.process_replacement_ratio(commands['replacementratio'])

        if 'seanalysis' in commands:
            settings.seanalysis = self.parse_boolean(commands, 'seanalysis')

        if 'selfemployed' in commands:
            settings.selfemployed = self.parse_boolean(commands, 'selfemployed')

        if 'stateofwork' in commands:
            self.process_state_of_work(commands['stateofwork'])

        if 'topoffminlength' in commands:
            self.process_top_off_min_length(commands['topoffminlength'])

        if 'topoffrate1' in commands:
            self.process_top_rate1(commands['topoffrate1'])

        if 'weeklybencap' in commands:
            self.process_weekly_ben_cap(commands['weeklybencap'])

        if 'weightfactor' in commands:
            self.process_weight_factor(commands['weightfactor'])

        # for command in commands:
        #     command = command.split(' ', 1)
        #     cmd_type = command[0].lower()
        #
        #     if cmd_type == 'file':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_file_cmd(cmd_options)
        #
        #     elif cmd_type == 'bennefiteffect':
        #         settings.partrate = self.parse_boolean(command)
        #
        #     elif cmd_type == 'calibrate':
        #         settings.calibrate = self.parse_boolean(command)
        #
        #     elif cmd_type == 'clonefactor':
        #         settings.clone_factor = self.process_clone_factor(command[1])
        #
        #     elif cmd_type == 'dependentallowance':
        #         settings.dep_allowance = self.process_dependent_allowance(command[1])
        #
        #     elif cmd_type == 'detail':
        #         settings.level = self.process_detail(command[1])
        #
        #     elif cmd_type == 'eligibilityrules':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_eligibility_rules(cmd_options)
        #
        #     elif cmd_type == 'extenddays':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_extend_days(cmd_options)
        #
        #     elif cmd_type == 'extendproportion':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_extend_proportions(cmd_options)
        #
        #     elif cmd_type == 'extendprob':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_extend_probabilities(cmd_options)
        #
        #     elif cmd_type == 'extendleaves':
        #         settings.extend_leaves = self.parse_boolean(command)
        #
        #     elif cmd_type == 'extendold':
        #         settings.extend_old = self.parse_boolean(command)
        #
        #     elif cmd_type == 'fmlaprotectionconstraint':
        #         settings.fmla_constraint = self.parse_boolean(command)
        #
        #     elif cmd_type == 'formula':
        #         settings.bformula = self.parse_boolean(command)
        #
        #     elif cmd_type == 'formula2':
        #         self.process_formula2(command[1])
        #
        #     elif cmd_type == 'government':
        #         settings.government = self.parse_boolean(command)
        #
        #     elif cmd_type == 'leaveprobabilityfactors':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_leave_probability_factors(cmd_options)
        #
        #     elif cmd_type == 'maxweeks':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_max_weeks(cmd_options)
        #
        #     elif cmd_type == 'missingvalue':
        #         settings.missing_string = command[1]
        #
        #     elif cmd_type == 'needersfullyparticipate':
        #         settings.takeup100 = self.parse_boolean(command)
        #
        #     elif cmd_type == 'randomseed':
        #         settings.spin = self.parse_boolean(command)
        #
        #     elif cmd_type == 'replacementratio':
        #         self.process_replacement_ratio(command[1])
        #
        #     elif cmd_type == 'seanalysis':
        #         settings.seanalysis = self.parse_boolean(command)
        #
        #     elif cmd_type == 'selfemployed':
        #         settings.selfemployed = self.parse_boolean(command)
        #
        #     elif cmd_type == 'stateofwork':
        #         self.process_state_of_work(command[1])
        #
        #     elif cmd_type == 'takeuprates':
        #         cmd_options = self.parse_cmd_options(command[1], cmd_type)
        #         self.process_take_up_rates(cmd_options)
        #
        #     elif cmd_type == 'topoffminlength':
        #         self.process_top_off_min_length(command[1])
        #
        #     elif cmd_type == 'topoffrate1':
        #         self.process_top_rate1(command[1])

    def parse_cmd_options(self, options, cmd_type):
        opts_dict = {}
        while len(options) > 0:
            options = options.split('=')
            option = options[0].strip().lower()
            rest = options[1].strip()

            if rest[0] == '"':
                rest = rest.split('"', 2)
                value = rest[1].strip()
                options = rest[2].strip()
            else:
                rest = rest.split(' ', 1)
                value = rest[0].strip()
                options = rest[1].strip()

            if option not in opts_dict:
                opts_dict[option] = value
            else:
                self.settings.log_error('The field "' + option + '" appears multiple times in command ' + cmd_type)

        return opts_dict

    def parse_boolean(self, commands, cmd_type):
        if commands[cmd_type].lower() == 'yes':
            return True
        elif commands[cmd_type].lower() == 'no':
            return False
        else:
            self.settings.log_error('Command Error: ' + cmd_type.upper() + ' should be "Yes" or "No"')

    @staticmethod
    def parse_integer(value):
        try:
            return int(value)
        except ValueError:
            return "Error"

    @staticmethod
    def parse_float(value):
        try:
            return float(value)
        except ValueError:
            return "Error"

    @staticmethod
    def is_sorted(lst):
        for i in range(len(lst) - 1):
            if lst[i] > lst[i + 1]:
                return False
        return True

    def process_file_cmd(self, options):
        options = self.parse_cmd_options(options, 'FILE')
        settings = self.settings
        try:
            log_file = options['log']
            settings.log.close()
            log_temp = open(settings.OUTPUT_FOLDER + 'log.txt', 'r')
            content = log_temp.read()
            log_temp.close()

            settings.log = open(settings.OUTPUT_FOLDER + log_file, 'a+')
            settings.log.write(content)

            self.household_files = [f.strip() for f in options['pumsh'].split(',') if f != '']
            self.person_files = [f.strip() for f in options['pumsp'].split(',') if f != '']

            settings.debug_file = options['debug']
            settings.main_file = options['main']
            settings.leaves_file = options['leaves']
            settings.weekly = options['weekly']
            settings.states = options['states']
            settings.benefit = options['benefit']
            settings.employer_pay_file = options['emppay']
            settings.doctor_file = options['doc']
        except KeyError as e:
            missing_field = e.args[0].upper()
            self.settings.log_error('Command Error: ' + missing_field + ' is required but missing from FILE command')

        if 'include' in options:
            settings.include_file = options['include']

    def process_clone_factor(self, value):
        value = self.parse_integer(value)
        if value == "Error" or value < 1:
            self.settings.log_error('Command Error: CLONEFACTOR should be a positive integer')
        return value

    def process_dependent_allowance(self, value):
        value = self.parse_float(value)
        if value == "Error" or value < 0:
            self.settings.log_error('Command Error: DEPENDENTALLOWANCE should be a positive real number')
        return value

    def process_detail(self, value):
        value = self.parse_integer(value)
        if value == "Error" or value < 1 or value > 8:
            self.settings.log_error('Command Error: DETAIL should be a positive integer between 1 and 8')
        return value

    def process_eligibility_rules(self, options):
        options = self.parse_cmd_options(options, 'ELIGIBILTYRULES')
        settings = self.settings
        if 'type' in options:
            el_type = options['type'].lower()
            if el_type == 'fmla':
                settings.fmla_eligr = True
            elif el_type == 'ma_uib':
                settings.ma_uib_eligr = True
            else:
                self.settings.log_error('Command Error: Must provide either FMLA or MA_UIB type in ELIGIBILITYRULES')
            return

        if 'a_earnings' in options:
            settings.earnings_threshold = options['a_earnings']
        if 'b_weeks' in options:
            settings.weeks_threshold = options['b_weeks']
        if 'c_annhours' in options:
            settings.annual_hours_threshold = options['c_annhours']
        if 'd_empsize' in options:
            settings.employer_size_threshold = options['d_empsize']
        if 'rule' in options:
            settings.eligibility_expression = options['rule']

    def process_extend_days(self, options):
        options = self.parse_cmd_options(options, 'EXTENDDAYS')
        extend_days = self.settings.extend_days
        for option in options:
            value = self.parse_integer(options[option])
            if value == 'Error' or value < 0:
                self.settings.log_error('Command Error: The field values in EXTENDDAYS should be non-negative integers')
            options[option] = value

        self.update_leave_dictionaries(extend_days, options)

    def process_extend_proportions(self, options):
        options = self.parse_cmd_options(options, 'EXTENDPROPORTIONS')
        extend_proportions = self.settings.extend_proportions
        for option in options:
            value = self.parse_float(options[option])
            if value == 'Error' or value < 0:
                self.settings.log_error('Command Error: The field values in EXTENDPROPORTIONS '
                               'should be non-negative real numbers')
            options[option] = value

        self.update_leave_dictionaries(extend_proportions, options)

    def process_extend_probabilities(self, options):
        options = self.parse_cmd_options(options, 'EXTENDPROB')
        extend_probabilities = self.settings.extend_probabilities
        for option in options:
            value = self.parse_integer(options[option])
            if value == 'Error':
                self.settings.log_error('Command Error: The field values in EXTENDPROB should be real numbers')
            options[option] = value

        self.update_leave_dictionaries(extend_probabilities, options)

    def process_formula2(self, options):
        options = self.parse_cmd_options(options, 'FORMULA2')
        if self.settings.formula:
            self.settings.log_error('Command Error: FORMULA2 command cannot be present if FORMULA command is "Yes"')

        settings = self.settings
        settings.formula2 = True

        while len(options) > 0:
            split_options = options.split('=', 1)
            key = split_options[0].strip().lower()
            split_options = split_options[1].strip().split(' ', 1)
            value = split_options[0].strip()
            try:
                options = split_options[1].strip()
            except IndexError:
                options = ''

            value = self.parse_float(value)
            if value == 'Error':
                self.settings.log_error('Command Error: FORMULA2 field values should be real numbers')

            if key == 'rate':
                settings.f_rates.append(value)
            if key == 'top':
                settings.f_cutoffs.append(value)
            else:
                self.settings.log_error('Command Error: ' + key.upper() + ' is not a valid field in FORMULA2 command')

        if len(settings.f_cutoffs) < 1:
            self.settings.log_error('Command Error: Must be at least one TOP field in the FORMULA2 command')

        if len(settings.f_rates) != len(settings.f_cutoffs) + 1:
            self.settings.log_error('Command Error: Must be one more RATE field than TOP fields in FORMULA2 command')

        if not self.is_sorted(settings.f_rates):
            self.settings.log_error('Command Error: TOP fields in FORMULA2 command must be in increasing order')

    def process_leave_probability_factors(self, options):
        options = self.parse_cmd_options(options, 'LEAVEPROBABILITYFACTORS')
        leave_probability_factors = self.settings.leave_probability_factors
        for option in options:
            value = self.parse_float(options[option])
            if value == 'Error':
                self.settings.log_error('Command Error: The field values in LEAVEPROBABILITYFACTORS should be real numbers')
            options[option] = value

        self.update_leave_dictionaries(leave_probability_factors, options)

    def process_max_weeks(self, options):
        options = self.parse_cmd_options(options, 'MAXWEEKS')
        max_weeks = self.settings.max_weeks
        for option in options:
            value = self.parse_integer(options[option])
            if value == 'Error' or value < 1:
                self.settings.log_error('Command Error: The field values in MAXWEEKS should be positive integers')
            options[option] = value

        self.update_leave_dictionaries(max_weeks, options)

    def process_replacement_ratio(self, value):
        value = self.parse_float(value)
        if value == 'Error':
            self.settings.log_error('Command Error: REPLACEMENTRATIO should be a real number')
        self.settings.rep_ratio = value

    def process_state_of_work(self, value):
        value = self.parse_integer(value)
        if value == 'Error' or value < 1:
            self.settings.log_error('Command Error: STATEOFWORK should be a positive integer')
        self.settings.stateofwork = value

    def process_take_up_rates(self, options):
        options = self.parse_cmd_options(options, 'TAKEUPRATES')
        take_up_rates = self.settings.take_up_rates
        for option in options:
            value = self.parse_float(options[option])
            if value == 'Error':
                self.settings.log_error('Command Error: The field values in TAKEUPRATES should be real numbers')
            options[option] = value

        self.update_leave_dictionaries(take_up_rates, options)

    def process_top_off_min_length(self, value):
        value = self.parse_integer(value)
        if value == 'Error':
            self.settings.log_error('Command Error: TOPOFFMINLENGTH should be an integer')
        self.settings.topoffminlength = value

    def process_top_rate1(self, value):
        value = self.parse_float(value)
        if value == 'Error':
            self.settings.log_error('Command Error: TOPOFFRATE1 should be a real number')
        self.settings.topoffrate1 = value

    def process_waiting_period(self, options):
        options = self.parse_cmd_options(options, 'WAITINGPERIOD')
        waiting_period = self.settings.waiting_period
        for option in options:
            value = self.parse_integer(options[option])
            if value == 'Error' or value < 0:
                self.settings.log_error('Command Error: The field values in WAITINGPERIOD should be non-negative integers')
            options[option] = value

        self.update_leave_dictionaries(waiting_period, options)

    def process_weekly_ben_cap(self, value):
        value = self.parse_float(value)
        if value == 'Error':
            self.settings.log_error('Command Error: WEEKLYBENCAP should be a real number')
        self.settings.cap = value

    def process_weight_factor(self, value):
        value = self.parse_float(value)
        if value == 'Error':
            self.settings.log_error('Command Error: WEIGHTFACTOR should be a real number')
        self.settings.n_years = value

    @staticmethod
    def update_leave_dictionaries(dictionary, options):
        if 'default' in options:
            for reason in dictionary:
                dictionary[reason] = options['default']

        if 'oh' in options:
            dictionary['Own Health'] = options['oh']

        if 'md' in options:
            dictionary['Maternity'] = options['md']

        if 'nc' in options:
            dictionary['New Child'] = options['nc']

        if 'ic' in options:
            dictionary['Ill Child'] = options['ic']

        if 'is' in options:
            dictionary['Ill Spouse'] = options['is']

        if 'ip' in options:
            dictionary['Ill Parent'] = options['ip']

    def generate_households(self):
        households = []
        previous_p = None  # Previous person in data
        for i in range(len(self.household_files)):
            hh_df = pd.read_csv(self.household_files[i])
            p_df = pd.read_csv(self.person_files[i])

            del hh_df['insp']

            for idx_1, hh_row in hh_df.iterrows():
                household = CHousehold(list(hh_row))

                serialno = hh_row['SERIALNO']
                hh_people = p_df[p_df['SERIALNO'] == serialno]
                previous_ih = None  # Previous person in household

                for idx_2, p_row in hh_people.iterrows():
                    person = CPerson(list(p_row), household)
                    household.people.append(person)

                    if previous_p:
                        previous_p.next = person

                    if previous_ih:
                        previous_ih.next = person

                    previous_p = person
                    previous_ih = person

                households.append(household)

        return households
