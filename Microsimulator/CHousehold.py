class CHousehold:
    firstHH = None
    lastHH = None

    def __init__(self, data):
        self.rt, self.serialno, self.division, self.puma00, self.puma10, self.region, self.st, self.adjhsg, \
        self.adjinc, self.wgtp, self.np, self.type, self.acr, self.ags, self.bath, self.bdsp, self.bld, self.bus, \
        self.conp, self.elep, self.fs, self.fulp, self.gasp, self.hfl, self.mhp, self.mrgi, self.mrgp, self.mrgt, \
        self.mrgx, self.refr, self.rmsp, self.rntm, self.rntp, self.rwat, self.rwatpr, self.sink, self.smp, self.stov, \
        self.tel, self.ten, self.toil, \
        self.vacs, self.valp, self.veh, self.watp, self.ybl, self.fes, self.fincp, self.fparc, self.grntp, self.grpip, \
        self.hhl, self.hht, self.hincp, self.hugcl, self.hupac, self.hupaoc, self.huparc, self.kit, self.lngi, \
        self.multg, self.mv, self.noc, self.npf, self.npp, self.nr, self.nrc, self.ocpip, self.partner, self.plm, \
        self.psf, self.r18, self.r60, self.r65, self.resmode, self.smocp, self.smx, self.srnt, self.sval, self.taxp, \
        self.wif, self.wkexrel, self.workstat, self.facrp, self.fagsp, self.fbathp, self.fbdsp, self.fbldp, \
        self.fbusp, self.fconp, self.felep, self.ffsp, self.ffulp, self.fgasp, self.fhflp, self.finsp, self.fkitp, \
        self.fmhp, self.fmrgip, self.fmrgp, self.fmrgtp, self.fmrgxp, self.fmvp, self.fplmp, self.frefrp, self.frmsp, \
        self.frntmp, self.frntp, self.frwatp, self.frwatprp, self.fsinkp, self.fsmp, self.fsmxhp, self.fsmxsp, \
        self.fstovp, self.ftaxp, self.ftelp, self.ftenp, self.ftoilp, self.fvacsp, self.fvalp, self.fvehp, self.fwatp, \
        self.fyblp, self.wgtp1, self.wgtp2, self.wgtp3, self.wgtp4, self.wgtp5, self.wgtp6, self.wgtp7, self.wgtp8, \
        self.wgtp9, self.wgtp10, self.wgtp11, self.wgtp12, self.wgtp13, self.wgtp14, self.wgtp15, self.wgtp16, \
        self.wgtp17, self.wgtp18, self.wgtp19, self.wgtp20, self.wgtp21, self.wgtp22, self.wgtp23, self.wgtp24, \
        self.wgtp25, self.wgtp26, self.wgtp27, self.wgtp28, self.wgtp29, self.wgtp30, self.wgtp31, self.wgtp32, \
        self.wgtp33, self.wgtp34, self.wgtp35, self.wgtp36, self.wgtp37, self.wgtp38, self.wgtp39, self.wgtp40, \
        self.wgtp41, self.wgtp42, self.wgtp43, self.wgtp44, self.wgtp45, self.wgtp46, self.wgtp47, self.wgtp48, \
        self.wgtp49, self.wgtp50, self.wgtp51, self.wgtp52, self.wgtp53, self.wgtp54, self.wgtp55, self.wgtp56, \
        self.wgtp57, self.wgtp58, self.wgtp59, self.wgtp60, self.wgtp61, self.wgtp62, self.wgtp63, self.wgtp64, \
        self.wgtp65, self.wgtp66, self.wgtp67, self.wgtp68, self.wgtp69, self.wgtp70, self.wgtp71, self.wgtp72, \
        self.wgtp73, self.wgtp74, self.wgtp75, self.wgtp76, self.wgtp77, self.wgtp78, self.wgtp79, self.wgtp80, \
        self.ffincp, self.fgrntp, self.fhincp, self.fsmoc = data

        self.adjinc /= 1000000
        self.adjhsg /= 1000000
        self.year = int(str(self.serialno)[:4])

        self.extra1 = 0
        self.extra2 = 0
        self.extra3 = 0

        self.people = []

        # If np == 0, then the household doesn't have any interviewed person
