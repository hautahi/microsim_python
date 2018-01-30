import numpy as np

class CPerson:
    firstPP = None
    lastPP = None

    def __init__(self, data, household):
        self.phh = household
        self.next_ih = None
        self.next = None

        self.sporder, self.puma00, self.puma10, self.st, self.adjinc, self.pwgtp, self.agep, self.cit, self.citwp05, \
        self.citwp12, self.cow, self.ddrs, self.dear, self.deye, self.dout, self.dphy, self.drat, self.dratx, \
        self.drem, self.eng, self.fer, self.gcl, self.gcm, self.gcr, self.hins1, self.hins2, self.hins3, self.hins4, \
        self.hins5, self.hins6, self.hins7, self.intp, self.jwmnp, self.jwrip, self.jwtr, self.lanx, self.mar, \
        self.marhd, self.marhm, self.marht, self.marhw, self.marhyp05, self.marhyp12, self.mig, self.mil, self.mlpa, \
        self.mlpb, self.mlpcd, self.mlpe, self.mlpfg, self.mlph, self.mlpi, self.mlpj, self.mlpk, self.nwab, \
        self.nwav, self.nwla, self.nwlk, self.nwre, self.oip, self.pap, self.relp, self.retp, self.sch, self.schg, \
        self.schl, self.semp, self.sex, self.ssip, self.ssp, self.wagp, self.wkhp, self.wkl, self.wkw, self.wrk, \
        self.yoep05, self.yoep12, self.anc, self.anc1p05, self.anc1p12, self.anc2p05, self.anc2p12, self.decade, \
        self.dis, self.drivesp, self.esp, self.esr, self.fod1p, self.fod2p, self.hicov, self.hisp, self.indp, \
        self.jwap, self.jwdp, self.lanp05, self.lanp12, self.migpuma00, self.migpuma10, self.migsp05, self.migsp12, \
        self.msp, self.naicsp, self.nativity, self.nop, self.oc, self.occp10, self.occp12, self.paoc, self.pernp, \
        self.pincp, self.pobp05, self.pobp12, self.povpip, self.powpuma00, self.powpuma10, self.powsp05, self.powsp12, \
        self.privcov, self.pubcov, self.qtrbir, self.rac1p, self.rac2p05, self.rac2p12, self.rac3p05, self.rac3p12, \
        self.racaian, self.racasn, self.racblk, self.racnhpi, self.racnum, self.racsor, self.racwht, self.rc, \
        self.sciengp, self.sciengrlp, self.sfn, self.sfr, self.socp10, self.socp12, self.vps, self.waob, self.fagep, \
        self.fancp, self.fcitp, self.fcitwp, self.fcowp, \
        self.fddrsp, self.fdearp, self.fdeyep, self.fdoutp, self.fdphyp, self.fdratp, self.fdratxp, self.fdremp, \
        self.fengp, self.fesrp, self.fferp, self.ffodp, self.fgclp, self.fgcmp, self.fgcrp, self.fhins1p, \
        self.fhins2p, self.fhins3c, self.fhins3p, self.fhins4c, self.fhins4p, self.fhins5c, self.fhins5p, \
        self.fhins6p, self.fhins7p, self.fhisp, self.findp, self.fintp, self.fjwdp, self.fjwmnp, self.fjwrip, \
        self.fjwtrp, self.flanp, self.flanxp, self.fmarhdp, self.fmarhmp, self.fmarhtp, self.fmarhwp, self.fmarhyp, \
        self.fmarp, self.fmigp, self.fmigsp, self.fmilpp, self.fmilsp, self.foccp, self.foip, self.fpap, self.fpobp, \
        self.fpowsp, self.fracp, self.frelp, self.fretp, self.fschgp, self.fschlp, self.fschp, self.fsemp, self.fsexp, \
        self.fssip, self.fssp, self.fwagp, self.fwkhp, self.fwklp, self.fwkwp, self.fwrkp, self.fyoep, self.pwgtp1, \
        self.pwgtp2, self.pwgtp3, self.pwgtp4, self.pwgtp5, self.pwgtp6, self.pwgtp7, self.pwgtp8, self.pwgtp9, \
        self.pwgtp10, self.pwgtp11, self.pwgtp12, self.pwgtp13, self.pwgtp14, self.pwgtp15, self.pwgtp16, \
        self.pwgtp17, self.pwgtp18, self.pwgtp19, self.pwgtp20, self.pwgtp21, self.pwgtp22, self.pwgtp23, \
        self.pwgtp24, self.pwgtp25, self.pwgtp26, self.pwgtp27, self.pwgtp28, self.pwgtp29, self.pwgtp30, \
        self.pwgtp31, self.pwgtp32, self.pwgtp33, self.pwgtp34, self.pwgtp35, self.pwgtp36, self.pwgtp37, \
        self.pwgtp38, self.pwgtp39, self.pwgtp40, self.pwgtp41, self.pwgtp42, self.pwgtp43, self.pwgtp44, \
        self.pwgtp45, self.pwgtp46, self.pwgtp47, self.pwgtp48, self.pwgtp49, self.pwgtp50, self.pwgtp51, \
        self.pwgtp52, self.pwgtp53, self.pwgtp54, self.pwgtp55, self.pwgtp56, self.pwgtp57, self.pwgtp58, \
        self.pwgtp59, self.pwgtp60, self.pwgtp61, self.pwgtp62, self.pwgtp63, self.pwgtp64, self.pwgtp65, \
        self.pwgtp66, self.pwgtp67, self.pwgtp68, self.pwgtp69, self.pwgtp70, self.pwgtp71, self.pwgtp72, \
        self.pwgtp73, self.pwgtp74, self.pwgtp75, self.pwgtp76, self.pwgtp77, self.pwgtp78, self.pwgtp79, \
        self.pwgtp80, self.fdisp, self.fpernp, self.fpincp, self.fprivcovp, self.fpubcovp = data

        self.adjinc /= 1000000
        if type(self.occp10) == str:
            self.occp10 = int(''.join(c for c in self.occp10 if c.isdigit()))
        if type(self.occp12) == str:
            self.occp12 = int(''.join(c for c in self.occp12 if c.isdigit()))

        self.nochildren = 1
        self.lnfaminc = 0
        self.lnearn = np.log(self.pernp)

        self.female = 1 if self.sex == 2 else 0
        self.male = 0 if self.sex == 2 else 1

        self.lths = 1 if self.schl <= 15 else 0
        self.somecol = 1 if 18 <= self.schl <= 20 else 0
        self.ba = 1 if self.schl == 21 else 0
        self.maplus = 1 if self.schl >= 22 else 0
        self.colgrad = 1 if self.schl >= 21 else 0

        self.married = 1 if self.mar == 1 else 0
        self.widowed = 1 if self.mar == 2 else 0
        self.divorced = 1 if self.mar == 3 else 0
        self.separated = 1 if self.mar == 4 else 0
        self.nevermarried = 1 if self.mar == 5 else 0
        self.sepdivwidowed = 1 if 2 <= self.mar <= 4 else 0

        self.blacknh = 0
        self.hispanic = 0
        self.asian = 0
        self.otherr = 0

        if self.hisp > 1:
            self.hispanic = 1
        elif self.rac1p == 2:
            self.blacknh = 1
        elif self.rac1p == 6:
            self.asian = 1
        elif self.rac1p != 1:
            self.otherr = 1

        self.hiemp = 1 if self.hins1 == 1 else 0
