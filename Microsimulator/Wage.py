import numpy as np


class Wage:
    def __init__(self, person, uniform1, uniform2, settings):
        self.person = person

        # TODO: Figure out what _2009to2013ACS_ means. Can that be supplied by user? Can we check for it in files?

        year = person.phh.year
        occ = 0
        # The below conditions are dependent on _2009to2013ACS_ boolean
        if year == 2010 or year == 2011:
            occ = person.occp10
        elif year >= 2012:
            occ = person.occp12

        self.occ1 = 0
        self.occ2 = 0
        self.occ3 = 0
        self.occ4 = 0
        self.occ5 = 0
        self.occ6 = 0
        self.occ7 = 0
        self.occ8 = 0
        self.occ9 = 0
        self.occ10 = 0
        self.majocc = 0

        if 10 <= occ <= 950:
            self.occ1 = 1
            self.majocc = 1
        elif 1000 <= occ <= 3540:
            self.occ2 = 1
            self.majocc = 2
        elif 3600 <= occ <= 4650:
            self.occ3 = 1
            self.majocc = 4
        elif 4700 <= occ <= 4965:
            self.occ4 = 1
            self.majocc = 4
        elif 5000 <= occ <= 5940:
            self.occ5 = 1
            self.majocc = 5
        elif 6000 <= occ <= 6130:
            self.occ6 = 1
            self.majocc = 6
        elif 6200 <= occ <= 6940:
            self.occ7 = 1
            self.majocc = 7
        elif 7000 <= occ <= 7630:
            self.occ8 = 1
            self.majocc = 8
        elif 7700 <= occ <= 8965:
            self.occ9 = 1
            self.majocc = 9
        elif 9000 <= occ <= 9750:
            self.occ10 = 1
            self.majocc = 10

        self.vmajocc = np.zeros((10, 1), dtype=np.int)
        if self.majind > 0:
            self.vmajocc[self.majocc - 1][0] = 1

        ind = self.person.indp

        self.ind1 = 0
        self.ind2 = 0
        self.ind3 = 0
        self.ind4 = 0
        self.ind5 = 0
        self.ind6 = 0
        self.ind7 = 0
        self.ind8 = 0
        self.ind9 = 0
        self.ind10 = 0
        self.ind11 = 0
        self.ind12 = 0
        self.ind13 = 0
        self.majind = 0

        if 170 <= ind <= 290:
            self.ind1 = 1
            self.majind = 1
        elif 370 <= ind <= 490:
            self.ind2 = 1
            self.majind = 2
        elif ind == 770:
            self.ind3 = 1
            self.majind = 3
        elif 1070 <= ind <= 3990:
            self.ind4 = 1
            self.majind = 4
        elif 4070 <= ind <= 5790:
            self.ind5 = 1
            self.majind = 5
        elif 6070 <= ind <= 6390 or 570 <= ind <= 690:
            self.ind6 = 1
            self.majind = 6
        elif 6470 <= ind <= 6780:
            self.ind7 = 1
            self.majind = 7
        elif 6870 <= ind <= 7190:
            self.ind8 = 1
            self.majind = 8
        elif 7270 <= ind <= 7790:
            self.ind9 = 1
            self.majind = 9
        elif 7860 <= ind <= 8470:
            self.ind10 = 1
            self.majind = 10
        elif 8560 <= ind <= 8690:
            self.ind11 = 1
            self.majind = 11
        elif 8770 <= ind <= 9290:
            self.ind12 = 1
            self.majind = 12
        elif 9370 <= ind <= 9590:
            self.ind13 = 1
            self.majind = 13

        self.vmajind= np.zeros((13, 1), dtype=np.int)
        if self.majind > 0:
            self.vmajind[self.majind - 1][0] = 1

        weeks_worked = self.get_weeks_worked(uniform1, settings)
        self.weeks_worked = weeks_worked
        if self.person.agep < 16:
            settings.log_error('Error: Age of person is less that 16')

        self.lastyear = False
        self.anydata = True
        self.regression = False
        self.wkly_wage_ly = 0
        self._wkly_wage_re = 0
        self.wagesource = 0
        self.weekly_wage = 0
        self.imputed = False

        if person.pernp > 0:
            self.wkly_wage_ly = person.pernp / weeks_worked
            self.lastyear = True
        else:
            self._wkly_wage_re = 400
            self.regression = True

        if self.lastyear:
            self.weekly_wage = self.wkly_wage_ly
            self.wagesource = 2
        else:
            self.weekly_wage = self._wkly_wage_re
            self.wagesource = 3

        self.weekly_wage *= person.adjinc
        household = person.phh
        self.family_income = 0

        if 1 <= household.hht <= 3:
            self.family_income = household.fincp if person.relp <= 10 else person.pincp

        self.family_income *= household.adjinc

        self.num_employers = self.set_num_employers(uniform2, settings)
        self.num_dep_child_u18 = self.get_num_dep_children()

        if self.num_dep_child_u18 > 0:
            person.nochildren = 0

        if self. family_income > 0:
            self.lnfamic = np.log(self.family_income / 1000)

        self.hourly = False

        self.size_cat = 0
        self.num_employees = 0

    def get_weeks_worked(self, uniform, settings):
        person = self.person
        female = person.female
        lnearn = person.lnearn
        blacknh = person.blacknh
        hispanic = person.hispanic
        age = person.age
        agesq = age ** 2

        fem_cu6 = 1 if person.paoc == 1 else 0
        fem_c617 = 1 if person.paoc == 2 else 0
        fem_cu6and617 = 1 if person.paoc == 3 else 0

        if person.wkw == 1:
            cut = [0.5224694, 0.2447976]
            bx = 0.189324 * lnearn + 0.0586798 * age - 0.0006171 * agesq + 0.4132999 * blacknh + 0.4872967 * hispanic
            return 49 + self.get_cutoff(uniform, cut, bx)

        if person.wkw == 2:
            cut = [3.772264]
            bx = .2685036 * lnearn
            return 47 + self.get_cutoff(uniform, cut, bx)

        if person.wkw == 3:
            cut = [3.003556, 3.058475, 3.426575, 3.572874, 4.20768, 5.034543, 6.385561]
            bx = .2834781 * lnearn + .0081962 * age
            return 39 + self.get_cutoff(uniform, cut, bx)

        if person.wkw == 4:
            cut = [-2.072172, -.0498528, .0400106, 1.296675, 1.338863, 2.015083,
                   2.056791, 2.202369, 2.689453, 3.931339, 4.166763, 4.99875]
            bx = .1713402 * lnearn + .0051267 * age + .0679797 * female + .2305112 * fem_cu6 + \
                 .4374884 * fem_c617 + .239917 * fem_cu6and617
            return 26 + self.get_cutoff(uniform, cut, bx)

        if person.wkw == 5:
            cut = [-1.102674, -.1418321, 1.036483, 1.193323, 1.332839, 1.361465,
                   2.354303, 2.40629, 2.58397, 2.606942, 3.103865, 3.400153]
            bx = .3028055*lnearn - .004904*age + .2187803*hispanic
            return 13 + self.get_cutoff(uniform, cut, bx)

        if person.wkw == 6:
            cut = [.0125678, .9033276, 1.28739, 2.046918, 2.2751223, 2.677372,
                   2.801757, 3.568499, 3.724779, 4.244502, 4.133029, 6.68456]
            bx = .6018275 * lnearn - .0492968 * age + .0002912 * agesq + .2071242 * female
            return self.get_cutoff(uniform, cut, bx)

        else:
            settings.log_error('Error: No weeks worked')

    @staticmethod
    def get_cutoff(uniform, cut, bx):
        cutoff = 0
        cumprob = 0
        for i in cut:
            cutoff += 1
            cumprob = 1 / (1 + np.exp(bx - i))

            if uniform < cumprob:
                break

        return cutoff if uniform < cumprob else cutoff + 1

    def set_num_employers(self, uniform, settings):
        person = self.person

        lths = person.lths
        somecol = person.somecol
        ba = person.ba
        maplus = person.maplus
        hiemp = person.hiemp
        cut = [-2990352, 1.433113]

        bx = -.0652556 * person.age + .0004115 * person.age ** 2 - .42671 * person.asian - \
             .2174653 * person.hispanic - .2763925 * lths + .2760745 * somecol + .3875605 * ba + .3990029 * maplus - \
             .053062 * person.lnearn - .1941105 * hiemp - .2953034 * self.ind4 - .2244062 * self.ind5 - \
             .2785901 * self.ind6 - .244895 * self.ind8 - .2430498 * self.ind13 - .1379493 * self.occ1 + \
             .4069147 * self.occ6 + .3059196 * self.occ7 + .2174528 * self.occ9 + .2036014 * self.occ10

        return self.get_cutoff(uniform, cut, bx)

    def get_num_dep_children(self):
        ndep = 0
        person = self.person
        people_in_hh = person.phh.people

        if person.sfr == 2 or person.sfr == 3:
            for p in people_in_hh:
                if 4 <= p.sfr <= 6 and p.sfn == person.sfn and p.agep < 18:
                    ndep += 1
        elif (person.relp == 0 or person.relp == 1) and person.gcr == 1:
            for p in people_in_hh:
                if p.relp == 7 and p.agep < 18:
                    ndep += 1
        elif person.relp == 0 or person.relp == 1:
            for p in people_in_hh:
                if 2 <= p.relp <= 4 and p.agep < 18:
                    ndep += 1

        return ndep

    def pr_hourly(self, settings):
        person = self.person
        bx = 3.443597 + .5250494 * person.female + .3448871 * person.blacknh - .1509796 * person.age + \
             .0015093 * person.age ** 2 - .9514732 * person.ba - 1.590943 * person.maplus - .8849493 * self.occ1 + \
             .8880488 * self.occ3 + .5734125 * self.occ5 + 1.242109 * self.occ7 + 1.019219 * self.occ8 + \
             1.678 * self.occ9 + 1.079526 * self.occ10 + .3391169 * self.ind5 - .302905 * self.ind8 + \
             .4234983 * self.ind11 - .6188567 * self.ind12

        e = np.exp(bx)
        return e / (1 + e)

    def set_employer_size(self, uniform1, settings):
        person = self.person

        female = person.female
        lnearn = person.lnearn
        blacknh = person.blacknh
        hispanic = person.hispanic
        asian = person.asian
        otherr = person.otherr
        age = person.age
        agesq = age ** 2

        lths = person.lths
        somecol = person.somecol
        ba = person.ba
        maplus = person.maplus
        hiemp = person.hiemp

        size_cat = 0
        num_employees = 0

        bx = -.6182106 - .018312 * age + .5435623 * blacknh - .1784881 * lths + .0461504 * somecol + .0431483 * ba + \
             .0998634 * maplus + .2284372 * lnearn + .4681369 * hiemp - 2.013904 * self.vmajind[1] - \
             1.456223 * self.vmajind[3] - .2249696 * self.vmajind[5] - .2215996 * self.vmajind[6] - \
             .3956034 * self.vmajind[8] - 1.031341 * self.vmajind[9] - .4637155 * self.vmajind[11] - \
             1.838622 * self.vmajind[12] + 1.078739 * self.vmajind[13] - .3426925 * self.vmajocc[1] - \
             .4424592 * self.vmajocc[3] - .3775894 * self.vmajocc[4] - .520554 * self.vmajocc[7]

        prob = np.exp(bx) / (1 + np.exp(bx))

        if uniform1 < prob:
            cut = [-1.538165, -.2119441, .1534289]
            bx = -.0031871 * age + .3443047 * blacknh + .2150592 * asian + .3338452 * otherr - .2515116 * lths + \
                 .0688901 * ba + .1918942 * maplus + .0330519 * lnearn + .1829315 * hiemp - \
                 .3436195 * self.vmajind[1] - .6289225 * self.vmajind[3] + .3339817 * self.vmajind[5] + \
                 .3268252 * self.vmajind[6] + .1384174 * self.vmajind[8] - .3453498 * self.vmajind[9] + \
                 .2640143 * self.vmajind[11] - .4601113 * self.vmajind[12] + .9410239 * self.vmajind[13] + \
                 .1729759 * self.vmajocc[1] + .3053381 * self.vmajocc[2] + .4999731 * self.vmajocc[4] + \
                 .1659095 * self.vmajocc[5] - .5689651 * self.vmajocc[6] - .2406926 * self.vmajocc[7] - \
                 .2386636 * self.vmajocc[9]

            size_cat = 2 + self.get_cutoff(uniform1, cut, bx)

            if size_cat == 3:
                pass
