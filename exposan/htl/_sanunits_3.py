#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
EXPOsan: Exposition of sanitation and resource recovery systems

This module is developed by:
    Jianan Feng <jiananf2@illinois.edu>
    Yalin Li <mailto.yalin.li@gmail.com>
    
This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/EXPOsan/blob/main/LICENSE.txt
for license details.

References:
    
(1) Li, Y.; Tarpeh, W. A.; Nelson, K. L.; Strathmann, T. J. 
    Quantitative Evaluation of an Integrated System for Valorization of
    Wastewater Algae as Bio-Oil, Fuel Gas, and Fertilizer Products. 
    Environ. Sci. Technol. 2018, 52 (21), 12717–12727. 
    https://doi.org/10.1021/acs.est.8b04035.
    
(2) Leow, S.; Witter, J. R.; Vardon, D. R.; Sharma, B. K.;
    Guest, J. S.; Strathmann, T. J. Prediction of Microalgae Hydrothermal
    Liquefaction Products from Feedstock Biochemical Composition.
    Green Chem. 2015, 17 (6), 3584–3599. https://doi.org/10.1039/C5GC00574D.
    
(3) Snowden-Swan, L. J.; Zhu, Y.; Jones, S. B.; Elliott, D. C.; Schmidt, A. J.; 
    Hallen, R. T.; Billing, J. M.; Hart, T. R.; Fox, S. P.; Maupin, G. D. 
    Hydrothermal Liquefaction and Upgrading of Municipal Wastewater Treatment 
    Plant Sludge: A Preliminary Techno-Economic Analysis; 
    PNNL--25464, 1258731; 2016; https://doi.org/10.2172/1258731.

(4) Jones, S. B.; Zhu, Y.; Anderson, D. B.; Hallen, R. T.; Elliott, D. C.; 
    Schmidt, A. J.; Albrecht, K. O.; Hart, T. R.; Butcher, M. G.; Drennan, C.; 
    Snowden-Swan, L. J.; Davis, R.; Kinchin, C. 
    Process Design and Economics for the Conversion of Algal Biomass to
    Hydrocarbons: Whole Algae Hydrothermal Liquefaction and Upgrading;
    PNNL--23227, 1126336; 2014; 
    https://doi.org/10.2172/1126336.
    
(5) Hao, S.; Choi, Y.-J.; Wu, B.; Higgins, C. P.; Deeb, R.; Strathmann, T. J.
    Hydrothermal Alkaline Treatment for Destruction of Per- and Polyfluoroalkyl
    Substances in Aqueous Film-Forming Foam. Environ. Sci. Technol.
    2021, 55(5), 3283–3295. https://doi.org/10.1021/acs.est.0c06906.
'''

import biosteam as bst
from qsdsan import SanUnit
from qsdsan.sanunits import HXutility
from exposan.htl._components_2 import create_components

__all__ = ('SludgeLab',
          'HTL',
          'AcidExtraction',
          'HTLmixer',
          'HTLsplitter',
          'StruvitePrecipitation',
          'CHG',
          'MembraneDistillation',
          'H2mixer'
          'HT',
          'HC',
          'WWmixer')

cmps = create_components()

# =============================================================================
# Sludge Lab
# =============================================================================

class SludgeLab(SanUnit):
    
    '''
    SludgeLab is a fake unit that can set up sludge biochemical compositions
    and calculate sludge elemental compositions.
    
    Model method: just _run, no _design or _cost.
    
    Parameters
    ----------
    ins: Iterable (stream)
        fake_sludge
    outs: Iterable (stream)
        real_sludge
    '''

    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream', 
                 sludge_moisture=0.99, sludge_dw_protein=0.341,
                 sludge_dw_lipid=0.226, sludge_dw_carbo=0.167,
                 sludge_P_ratio = 0.019, # data are from SS PNNL 2021
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)
        self.sludge_moisture = sludge_moisture
        self.sludge_dw_protein = sludge_dw_protein
        self.sludge_dw_carbo = sludge_dw_carbo
        self.sludge_dw_lipid = sludge_dw_lipid
        self.sludge_dw_ash = 1 - sludge_dw_protein - sludge_dw_carbo -\
                             sludge_dw_lipid
        self.sludge_P_ratio = sludge_P_ratio
        # set P as an independent variable, assume S (sulfur) is 0
        
    _N_ins = 1
    _N_outs = 1
    
    def _run(self):
        
        fake_sludge = self.ins[0]
        real_sludge = self.outs[0]
        
        real_sludge.imass['H2O'] = fake_sludge.F_mass * self.sludge_moisture
        sludge_dw = fake_sludge.F_mass*(1 - self.sludge_moisture)
        real_sludge.imass['Sludge_protein'] = sludge_dw*self.sludge_dw_protein
        real_sludge.imass['Sludge_carbo'] = sludge_dw*self.sludge_dw_carbo
        real_sludge.imass['Sludge_lipid'] = sludge_dw*self.sludge_dw_lipid
        real_sludge.imass['Sludge_ash'] = sludge_dw*self.sludge_dw_ash
          
    # all sludge elemental analysis are based on empirical equation
    @property
    def sludge_C_ratio(self):
       return self.sludge_dw_carbo*0.44 + self.sludge_dw_lipid*0.75 +\
           self.sludge_dw_protein*0.53
    # https://pubmed.ncbi.nlm.nih.gov/2061559/ (accessed 2022-10-27)
    # https://encyclopedi/a2.thefreedictionary.com/Proteins
    # (accessed 2022-10-27)
    
    @property
    def sludge_H_ratio(self):
       return self.sludge_C_ratio/7
    # based on SS PNNL 2021 data, H ~ C/7
   
    @property
    def sludge_N_ratio(self):
       return self.sludge_dw_protein*0.16
    # https://www.fao.org/3/y5022e/y5022e03.htm#:~:text=On%20the%20basis%20of%
    # 20early,is%20confounded%20by%20two%20considerations (accessed 2022-10-27)
   
    @property
    def sludge_P_ratio(self):
       return self._sludge_P_ratio
    # set P as an indepedent variable since hard to find any association with
    # sludge biochemical compositions
    
    @sludge_P_ratio.setter
    def sludge_P_ratio(self, i):
        if not 0 <= i <= 1:
            raise AttributeError('`sludge_P` must be within [0, 1], '
                                f'the provided value {i} is outside the\
                                range.')
        self._sludge_P_ratio = i
    
    @property
    def sludge_O_ratio(self):
       return 1 - self.sludge_C_ratio - self.sludge_H_ratio -\
           self.sludge_N_ratio - self.sludge_P_ratio - self.sludge_dw_ash*0.75
    # sludge_O is calculated based on mass balance closure and * 0.75 since
    # double count some elements. 0.75 is based on SS PNNL 2021.
    
    @property
    def AOSc(self):
       return (3*self.sludge_N_ratio/14.0067 + 2*self.sludge_O_ratio/15.999 -\
               self.sludge_H_ratio/1.00784)/(self.sludge_C_ratio/12.011)
   
    def _design(self):
        pass
    
    def _cost(self):
        pass

# =============================================================================
# HTL (ignore three phase separator for now, ask Yalin)
# =============================================================================

class HTL(SanUnit):
    
    '''
    HTL converts dewatered sludge to biocrude, aqueous, off-gas, and biochar
    under elevated temperature (350°C) and pressure. The products percentage
    (wt%) can be evaluated using revised MCA model (Li et al., 2017,
    Leow et al., 2018) with known sludge composition (protein%, lipid%,
    and carbohydrate%, all afdw%).
    
    Notice that for HTL we just calculate each phases' total mass (except gas)
    and calculate C, N, and P amount in each phase as properties. We don't
    specify components for oil/char since we want to use MCA model to calculate
    C and N amount and it is not necessary to calculate every possible
    components since they will be treated in HT/AcidEx anyway. We also don't
    specify components for aqueous since we want to calculate aqueous C, N, and
    P based on mass balance closure. But later for CHG, HT, and HC, we specify
    each components (except aqueous phase) for the application of flash,
    distillation column, and CHP units.
    
    Model method: empirical model (based on MCA model and experimental data).
    
    Parameters
    ----------
    ins: Iterable (stream)
        dewatered_sludge
    outs: Iterable (stream)
        biochar, HTLaqueous, biocrude, offgas
    '''
    
    auxiliary_unit_names=('heat_exchanger',)

    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 biocrude_moisture_content=0.056, # Jones PNNL 2014
                 biochar_C_N_ratio=15.5, biochar_C_P_ratio=2.163,
                 # Li EST
                 gas_composition={'CH4':0.050, 'C2H6':0.032,
                                  'CO2':0.918}, # Jones
                 biochar_pre=3029.7*6894.76, # Jones 2014: 3029.7 psia
                 HTLaqueous_pre=30*6894.76, # Jones 2014: 30 psia
                 biocrude_pre=30*6894.76,
                 offgas_pre=30*6894.76,
                 eff_T=60+273.15, # Jones 2014
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)
        self.biocrude_moisture_content = biocrude_moisture_content
        self.biochar_C_N_ratio = biochar_C_N_ratio
        self.biochar_C_P_ratio = biochar_C_P_ratio
        self.gas_composition = gas_composition
        self.biochar_pre = biochar_pre
        self.HTLaqueous_pre = HTLaqueous_pre
        self.biocrude_pre = biocrude_pre
        self.offgas_pre = offgas_pre
        self.eff_T = eff_T
        hx_in = bst.Stream(f'{ID}_hx_in')
        hx_out = bst.Stream(f'{ID}_hx_out')
        self.heat_exchanger = HXutility(ID=f'{ID}_hx', ins=hx_in, outs=hx_out)

    _N_ins = 2
    _N_outs = 4
    
    def _run(self):
        
        dewatered_sludge, base = self.ins
        biochar, HTLaqueous, biocrude, offgas = self.outs
        
        dewatered_sludge_afdw = dewatered_sludge.imass['Sludge_lipid'] +\
                                dewatered_sludge.imass['Sludge_protein'] +\
                                dewatered_sludge.imass['Sludge_carbo']
        
        # NaOH added here. target is 5 M (Shilai Hao EST)
        # for water solution: 5 M NaOH: 20 g NaOH / 100 mL H2O
        # (0.2 kg NaOH / 1 kg H2O)
        # here, the calculation is based on the water amount in the dewatered
        # sludge (assume the initial pH = 7, and solids don't affect pH)
        base.imass['NaOH'] = dewatered_sludge.imass['H2O']*0.2 
        
        lipid_ratio = dewatered_sludge.imass['Sludge_lipid']/\
                      dewatered_sludge_afdw
        protein_ratio = dewatered_sludge.imass['Sludge_protein']/\
                        dewatered_sludge_afdw
        carbo_ratio = dewatered_sludge.imass['Sludge_carbo']/\
                      dewatered_sludge_afdw

        # the following calculations are based on revised MCA model
        biochar.imass['Biochar'] = 0.377*carbo_ratio*dewatered_sludge_afdw  
        
        HTLaqueous.imass['HTLaqueous'] = (0.154*lipid_ratio +\
                                          0.481*protein_ratio)*\
                                          dewatered_sludge_afdw
        # HTLaqueous is TDS in aqueous phase
         
        gas_mass = (0.074*protein_ratio + 0.418*carbo_ratio)*\
                       dewatered_sludge_afdw
                       
        for name, ratio in self.gas_composition.items():
            offgas.imass[name] = gas_mass*ratio
            
        biocrude.imass['Biocrude'] = (0.846*lipid_ratio + 0.445*protein_ratio\
                                      + 0.205*carbo_ratio)*\
                                      dewatered_sludge_afdw
        biocrude.imass['H2O'] = biocrude.imass['Biocrude']/(1 -\
                                self.biocrude_moisture_content) -\
                                biocrude.imass['Biocrude']
                                
        HTLaqueous.imass['H2O'] = dewatered_sludge.imass['H2O'] -\
                                  biocrude.imass['H2O'] +\
                                  dewatered_sludge.imass['Sludge_ash'] +\
                                  base.imass['NaOH']
        # assume ash (all soluble based on Jones) goes to water
        # all NaOH also goes to water to maintain pH for membrane distillation
        
        biochar.phase = 's'
        offgas.phase = 'g'
        
        biochar.P = self.biochar_pre
        HTLaqueous.P = self.HTLaqueous_pre
        biocrude.P = self.biocrude_pre
        offgas.P = self.offgas_pre
        
        for stream in self.outs: stream.T = self.eff_T
        
        self.sludgelab = self.ins[0]._source.ins[0]._source.ins[0].\
                         _source.ins[0]._source.ins[0]._source
        
        # in the case that HTLaqueous_C or HTLaqueous_N is less than 0, which
        # is not likely to happen, we add the following two exceptions.
        if self.HTLaqueous_C < 0:
            raise Exception('double check sludge composition, HTLaqueous_C '\
                            'is not likely to be less than 0, otherwise, we '\
                            'do not need CHG')
        if self.HTLaqueous_N < 0:
            raise Exception('double check sludge composition, HTLaqueous_N '\
                            'is not likely to be less than 0, otherwise, we '\
                            'do not need membrane distillation')
            
        # self.HTLaqueous_P is always larger than 0, since an constraint is
        # added when calculated biochar_P

    @property
    def biochar_C_ratio(self):
        return min(1.75*self.sludgelab.sludge_dw_carbo, 0.65)
    # revised MCA model
    
    @property
    def biochar_N_ratio(self):
        return self.biochar_C_ratio/self.biochar_C_N_ratio 
    
    @property
    def biochar_P_ratio(self):
        return self.biochar_C_ratio/self.biochar_C_P_ratio

    @property
    def biochar_C(self):
        return self.outs[0].F_mass*self.biochar_C_ratio

    @property
    def biochar_N(self):
        return self.outs[0].F_mass*self.biochar_N_ratio

    @property
    def biochar_P(self):
        return min((self.ins[0].F_mass - self.ins[0].imass['H2O'])*\
                    self.sludgelab.sludge_P_ratio, self.outs[0].F_mass*\
                    self.biochar_P_ratio)
    # make sure biochar P smaller than total P

    @property
    def biocrude_C_ratio(self):
        return (self.sludgelab.AOSc*(-8.37) + 68.55)/100 # revised MCA model

    @property
    def biocrude_N_ratio(self):
        return 0.133*self.sludgelab.sludge_dw_protein # revised MCA model

    @property
    def biocrude_C(self):
        return self.outs[2].F_mass*self.biocrude_C_ratio

    @property
    def biocrude_N(self):
        return self.outs[2].F_mass*self.biocrude_N_ratio

    @property
    def offgas_C(self):
        carbon = 0
        for name in self.gas_composition.keys():
            carbon += self.outs[3].imass[name]*cmps[name].i_C
        return carbon   
               
    # C, N, and P in aqueous phase are calculated based on mass balance closure
    @property
    def HTLaqueous_C(self):
        return (self.ins[0].F_mass - self.ins[0].imass['H2O'])*\
                self.sludgelab.sludge_C_ratio - self.biochar_C -\
                self.biocrude_C - self.offgas_C

    @property
    def HTLaqueous_N(self):
        return (self.ins[0].F_mass - self.ins[0].imass['H2O'])*\
                self.sludgelab.sludge_N_ratio - self.biochar_N -\
                self.biocrude_N

    @property
    def HTLaqueous_P(self):
        return (self.ins[0].F_mass - self.ins[0].imass['H2O'])*\
                self.sludgelab.sludge_P_ratio - self.biochar_P

    def _design(self):
        
        hx = self.heat_exchanger
        hx_ins0, hx_outs0 = hx.ins[0], hx.outs[0]
        hx_ins0.mix_from((self.outs[1], self.outs[2], self.outs[3]))
        hx_outs0.mix_from((self.outs[1], self.outs[2], self.outs[3]))
        hx_ins0.T = self.ins[0].T # temperature before/after HTL are similar
        hx.T = hx_outs0.T
        hx.simulate_as_auxiliary_exchanger(ins=hx.ins, outs=hx.outs)
    
    def _cost(self):
        pass

# =============================================================================
# Acid Extraction
# =============================================================================

class AcidExtraction(SanUnit):
    
    '''
    H2SO4 is added to biochar from HTL to extract P. 
    
    Model method: assume P recovery ratio, add filters in _design and _cost.
    
    Parameters
    ----------
    ins: Iterable (stream)
        biochar, acid
    outs: Iterable (stream)
        residual, extracted
    '''
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream', acid_vol=10, P_acid_recovery_ratio=0.95,
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)
        self.acid_vol = acid_vol
        self.P_acid_recovery_ratio = P_acid_recovery_ratio

    _N_ins = 2
    _N_outs = 2
        
    def _run(self):
        
        biochar, acid = self.ins
        residual, extracted = self.outs
        
        acid.imass['H2SO4'] = biochar.F_mass*self.acid_vol*0.5*98.079/1000
        #0.5 M H2SO4 acid_vol (10 mL/1 g) Biochar
        acid.imass['H2O'] = biochar.F_mass*self.acid_vol*1.05 -\
                            acid.imass['H2SO4']
        # 0.5 M H2SO4 density: 1.05 kg/L 
        # https://www.fishersci.com/shop/products/sulfuric-acid-1n-0-5m-
        # standard-solution-thermo-scientific/AC124240010 (accessed 10-6-2022)
        
        residual.imass['Residual'] = biochar.F_mass*(1 - self.ins[0].
                                     _source.biochar_P_ratio*self.
                                     P_acid_recovery_ratio)
        
        extracted.copy_like(acid)
        extracted.imass['P'] = biochar.F_mass - residual.F_mass
        # assume just P can be extracted
        
        residual.phase = 's'
        
        residual.T = extracted.T = biochar.T
        # H2SO4 reacts with biochar to release heat and temperature will be
        # increased mixture's temperature
        
    @property
    def residual_C(self):
        return self.ins[0]._source.biochar_C
    
    @property
    def residual_N(self):
        return self.ins[0]._source.biochar_N

    @property
    def residual_P(self):
        return self.ins[0]._source.biochar_P - self.outs[1].imass['P']
        
    def _design(self):
        pass
    
    def _cost(self):
        pass
    
# =============================================================================
# HTL mixer
# =============================================================================

class HTLmixer(SanUnit):
    '''
    A fake unit that calculates C, N, P, and H2O amount in the mixture of HTL
    aqueous and AcidEx effluent.
    
    Model method: elements separation, don't need _design and _cost.
    
    Parameters
    ----------
    ins: Iterable (stream)
        HTLaqueous, extracted
    outs: Iterable (stream)
        mixture
    '''
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)

    _N_ins = 2
    _N_outs = 1
        
    def _run(self):
        
        HTLaqueous, extracted = self.ins
        mixture = self.outs[0]
        
        mixture.imass['C'] = self.ins[0]._source.HTLaqueous_C
        mixture.imass['N'] = self.ins[0]._source.HTLaqueous_N
        mixture.imass['P'] = self.ins[0]._source.HTLaqueous_P +\
                             extracted.imass['P']
        mixture.imass['H2O'] = HTLaqueous.F_mass + extracted.F_mass -\
                               mixture.imass['C'] - mixture.imass['N'] -\
                               mixture.imass['P']
        # represented by H2O except C, N, P
        
        mixture.T = extracted.T
        mixture.P = extracted.P
        
    def _design(self):
        pass
    
    def _cost(self):
        pass
    
# =============================================================================
# HTLsplitter
# =============================================================================

class HTLsplitter(SanUnit):
    
    '''
    A fake unit that calculates influent based on effluents.
    
    Model method: use experimental data.
    
    Parameters
    ----------
    ins: Iterable (stream)
    flow_in
    outs: Iterable (stream)
    flow_out_1, flow_out_2
    '''
    
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo,init_with)

    _N_ins = 1
    _N_outs = 2
        
    def _run(self):
        
        flow_in = self.ins[0]
        flow_out_1, flow_out_2 = self.outs
        
        flow_in.mix_from((flow_out_1, flow_out_2))
    
    def _design(self):
        pass
    
    def _cost(self):
        pass

# =============================================================================
# Struvite Precipitation
# =============================================================================

class StruvitePrecipitation(SanUnit):
    '''
    extracted_P and HTL aqueous are mixed together (Mixer) before adding
    MgCl2 and struvite precipitation.
    
    Model method: P recovery rate with uncertainty from literature data.
    If mol(N)<mol(P), add NH4Cl to mol(N):mol(P)=1:1
    
    Parameters
    ----------
    ins: Iterable (stream)
        mixture, supply_MgCl2, supply_NH4Cl
    outs: Iterable (stream)
        struvite, effluent
    '''
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream', Mg_P_ratio=1,
                 P_pre_recovery_ratio=0.95, P_in_struvite=0.127,
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)
        self.Mg_P_ratio = Mg_P_ratio
        self.P_pre_recovery_ratio = P_pre_recovery_ratio
        self.P_in_struvite = P_in_struvite

    _N_ins = 3
    _N_outs = 2
        
    def _run(self):
        
        mixture, supply_MgCl2, supply_NH4Cl = self.ins
        struvite, effluent = self.outs
        
        if mixture.imass['P']/30.973762 > mixture.imass['N']/14.0067:
            supply_NH4Cl.imass['NH4Cl'] = (mixture.imass['P']/30.973762 -\
                                           mixture.imass['N']/14.0067)*53.491
        # make sure N:P >= 1:1
        
        supply_MgCl2.imass['MgCl2'] = mixture.imass['P']/30.973762*95.211*\
                                      self.Mg_P_ratio # Mg:P = 1:1
        struvite.imass['Struvite'] = mixture.imass['P']*\
                                     self.P_pre_recovery_ratio/\
                                     self.P_in_struvite
        supply_MgCl2.phase = 's'
        
        effluent.copy_like(mixture)
        effluent.imass['P'] -= struvite.imass['Struvite']*self.P_in_struvite
        effluent.imass['N'] += supply_NH4Cl.imass['NH4Cl']*14.0067/53.491 -\
                               struvite.imass['Struvite']*\
                               self.P_in_struvite/30.973762*14.0067
        effluent.imass['H2O'] += (supply_MgCl2.imass['MgCl2'] +\
                                  supply_NH4Cl.imass['NH4Cl'] -\
                                  struvite.imass['Struvite']*\
                                  (1 - self.P_in_struvite*\
                                  (1+14.0067/30.973762)))
        struvite.phase = 's'    
            
        struvite.T = mixture.T
        effluent.T = mixture.T
        
    @property
    def struvite_P(self):
        return self.outs[0].imass['Struvite']*self.P_in_struvite

    @property
    def struvite_N(self):
        return self.struvite_P*14.0067/30.973762

    def _design(self):
        pass
    
    def _cost(self):
        pass

# =============================================================================
# CHG
# =============================================================================

class CHG(SanUnit):
   
    '''
    CHG serves to reduce the COD content in the aqueous phase and produce fuel
    gas under elevated temperature (350°C) and pressure. The outlet will be
    cooled down and separated by a flash unit.
    
    Model method: use experimental data, assume no NH3 loss for now.
    
    Parameters
    ----------
    ins: Iterable (stream)
        CHGfeed
    outs: Iterable (stream)
        CHGfuelgas, effluent
    '''
    
    auxiliary_unit_names=('heat_exchanger',)
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 gas_composition={'CH4':0.527,
                                  'CO2':0.432,
                                  'C2H6':0.011,
                                  'C3H8':0.030,
                                  'H2':0.0001},
                 # Jones
                 # will not be a variable in uncertainty/sensitivity analysis
                 gas_c_to_total_c=0.764*0.262, # Li EST
                 CHGout_pre = 3065.7*6894.76,
                 # Jones 2014: pressure before flash
                 eff_T=60+273.15, # Jones 2014: temperature after cooler
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)
        self.gas_composition = gas_composition
        self.gas_c_to_total_c = gas_c_to_total_c
        self.CHGout_pre = CHGout_pre
        self.eff_T = eff_T
        hx_in = bst.Stream(f'{ID}_hx_in')
        hx_out = bst.Stream(f'{ID}_hx_out')
        self.heat_exchanger = HXutility(ID=f'{ID}_hx', ins=hx_in, outs=hx_out)
        
    _N_ins = 1
    _N_outs = 1
        
    def _run(self):
        
        CHGfeed = self.ins[0]
        CHGout = self.outs[0]
        
        gas_C_ratio = 0
        for name, ratio in self.gas_composition.items():
            gas_C_ratio += ratio*cmps[name].i_C
        
        gas_mass = CHGfeed.imass['C']*self.gas_c_to_total_c/gas_C_ratio
        
        for name,ratio in self.gas_composition.items():
            CHGout.imass[name] = gas_mass*ratio
            
        CHGout.imass['H2O'] = CHGfeed.F_mass - gas_mass
        # all C, N, and P are accounted in H2O here, but will be calculated as
        # properties.
            
        CHGout.P = self.CHGout_pre
        
        for stream in self.outs: stream.T = self.eff_T
        
    @property
    def CHGout_C(self):
        # not include carbon in gas phase
        return self.ins[0].imass['C']*(1 - self.gas_c_to_total_c)
    
    @property
    def CHGout_N(self):
        return self.ins[0].imass['N']
    
    @property
    def CHGout_P(self):
        return self.ins[0].imass['P']
        
    def _design(self):
        
        hx = self.heat_exchanger
        hx_ins0, hx_outs0 = hx.ins[0], hx.outs[0]
        hx_ins0.mix_from(self.outs)
        hx_outs0.mix_from(self.outs)
        hx_ins0.T = self.ins[0].T # temperature before/after CHG are similar
        hx.T = hx_outs0.T
        hx.simulate_as_auxiliary_exchanger(ins=hx.ins, outs=hx.outs)
    
    def _cost(self):
        pass
    
# =============================================================================
# Membrane Distillation
# =============================================================================

class MembraneDistillation(SanUnit):
    
    '''
    Membrane distillation recovers nitrogen as ammonia sulfate based on vapor
    pressure difference across the hydrophobic membrane.
    
    Model method: 
        1. Feed pH = 10, permeate pH =1.5 (0.5 M H2SO4)
        2. All N in the feed are NH4+/NH3 (Jones PNNL 2014)
        3. 95% NH3 in feed can be transfered to permeate (assume 95% for now,
           use literature data to find a conservative assumpation later)
        4. All NH3 in permeate can form (NH4)2SO4 (which makes sense since
           just water evaporates)
        5. _design and _cost refer to
           A.A. et al., Membrane distillation: A comprehensive review

    Parameters
    ----------
    ins: Iterable (stream)
        influent, acid
    outs: Iterable (stream)
        ammoniasulfate, ww
    '''
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 N_S_ratio=2, pH=10, ammonia_transfer_ratio=0.95,
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)
        self.N_S_ratio = N_S_ratio
        self.pH = pH
        self.ammonia_transfer_ratio = ammonia_transfer_ratio

    _N_ins = 2
    _N_outs = 2
        
    def _run(self):
        
        influent, acid = self.ins
        ammoniumsulfate, ww = self.outs
        
        influent.imass['C'] = self.ins[0]._source.ins[0]._source.CHGout_C
        influent.imass['N'] = self.ins[0]._source.ins[0]._source.CHGout_N
        influent.imass['P'] = self.ins[0]._source.ins[0]._source.CHGout_P
        influent.imass['H2O'] -= (influent.imass['C'] + influent.imass['N'] +\
                                  influent.imass['P'])
        
        acid.imass['H2SO4'] = influent.imass['N']/14.0067/self.N_S_ratio*98.079
        acid.imass['H2O'] = acid.imass['H2SO4']*1000/98.079/0.5*1.05 -\
                            acid.imass['H2SO4']
        
        pKa = 9.26 # ammonia pKa
        ammonia_to_ammonium = 10**(-pKa)/10**(-self.pH)
        ammonia_in_feed = influent.imass['N']/14.0067*ammonia_to_ammonium/(1 +\
                          ammonia_to_ammonium)*17.031

        ammoniumsulfate.imass['NH42SO4'] = ammonia_in_feed*\
                                          self.ammonia_transfer_ratio/34.062*\
                                          132.14
        ammoniumsulfate.imass['H2O'] = acid.imass['H2O']
        ammoniumsulfate.imass['H2SO4'] = acid.imass['H2SO4'] +\
                                         ammoniumsulfate.imass['NH42SO4']/\
                                         132.14*28.0134 -\
                                         ammoniumsulfate.imass['NH42SO4']
                                        
        ww.copy_like(influent) # ww has the same T and P as influent
        ww.imass['N'] -= influent.imass['N']*self.ammonia_transfer_ratio*\
                         ammonia_to_ammonium/(1 + ammonia_to_ammonium)
                         
        ammoniumsulfate.T = acid.T
        ammoniumsulfate.P = acid.P
        # ammoniumsulfate has the same T and P as acid
        
    def _design(self):
        pass
    
    def _cost(self):
        pass

# =============================================================================
# H2mixer
# =============================================================================

class H2mixer(SanUnit):
    '''
    A fake unit that mix H2 and oil.
    
    Model method: mix_from, don't need _design and _cost.
    
    Parameters
    ----------
    ins: Iterable (stream)
        hydrogen, oil
    outs: Iterable (stream)
        mixture
    '''
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)

    _N_ins = 2
    _N_outs = 1
        
    def _run(self):
        
        hydrogen, oil = self.ins
        mixture = self.outs[0]
        
        mixture.mix_from(self.ins)
        mixture.P = min(hydrogen.P, oil.P)

    def _design(self):
        pass
    
    def _cost(self):
        pass

# =============================================================================
# HT
# =============================================================================

class HT(SanUnit):
    
    '''
    Biocrude mixed with H2 are hydrotreated at elevated temperature (405°C)
    and pressure to produce upgraded biooil. Co-products include fuel gas and
    char. The amount of biooil and fuel gas can be estimated using values from
    Li et al., 2018.
    The amount of char can be calculated based on mass closure.
    
    Model method: use experimental data.
    
    Parameters
    ----------
    ins: Iterable (stream)
    mixture
    outs: Iterable (stream)
    HTaqueous, fuel_gas, gasoline, diesel, heavy_oil
    '''
    
    auxiliary_unit_names=('heat_exchanger',)
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 biooil_ratio=0.8, gas_ratio=0.07,
                 # Jones et al., 2014
                 # spreadsheet HT calculation
                 HTout_pre = 717.4*6894.76, # Jones 2014: 55 psia
                 HTrxn_T=402+273.15, # Jones 2014
                 HTout_T=43+273.15,
                 gas_composition = {'CH4':0.285, 'C2H6':0.365, 'C3H8':0.350},
                 # C3H8 includes N-C4H10, N-PENTAN, and HEXANE (stream #339)
                 # will not be a variable in uncertainty/sensitivity analysis
                 oil_composition={'TWOMBUTAN':0.0044, 'NPENTAN':0.0040,
                                  'TWOMPENTA':0.0044, 'HEXANE':0.0035,
                                  'TWOMHEXAN':0.0044, 'HEPTANE':0.0044,
                                  'CC6METH':0.0111, 'PIPERDIN':0.0044,
                                  'TOLUENE':0.0111, 'THREEMHEPTA':0.0111,
                                  'OCTANE':0.0111, 'ETHCYC6':0.0044,
                                  'ETHYLBEN':0.0222, 'OXYLENE':0.0111,
                                  'C9H20':0.0044, 'PROCYC6':0.0044,
                                  'C3BENZ':0.0111, 'FOURMONAN':0,
                                  'C10H22':0.0222, 'C4BENZ':0.0133,
                                  'C11H24':0.0222, 'C10H12':0.0222,
                                  'C12H26':0.0222, 'OTTFNA':0.0111,
                                  'C6BENZ':0.0222, 'OTTFSN':0.0222,
                                  'C7BENZ':0.0222, 'C8BENZ':0.0222,
                                  'C10H16O4':0.0200, 'C15H32':0.0666,
                                  'C16H34':0.1998, 'C17H36':0.0888, 
                                  'C18H38':0.0444, 'C19H40':0.0444,
                                  'C20H42':0.1110, 'C21H44':0.0444,
                                  'TRICOSANE':0.0444, 'C24H38O4':0.0089,
                                  'C26H42O4':0.0111, 'C30H62':0.0022},
                 # Jones et al., 2014
                 # spreadsheet HT calculation
                 # will not be a variable in uncertainty/sensitivity analysis
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)
        self.biooil_ratio = biooil_ratio
        self.gas_ratio = gas_ratio
        self.HTout_pre = HTout_pre
        self.HTrxn_T = HTrxn_T
        self.HTout_T = HTout_T
        self.gas_composition = gas_composition
        self.oil_composition = oil_composition
        hx_in = bst.Stream(f'{ID}_hx_in')
        hx_out = bst.Stream(f'{ID}_hx_out')
        self.heat_exchanger = HXutility(ID=f'{ID}_hx', ins=hx_in, outs=hx_out)

    _N_ins = 1
    _N_outs = 1
        
    def _run(self):
        
        mixture = self.ins [0]
        ht_out = self.outs[0]
        
        H2_split = self.ins[0]._source.ins[0]._source.ins[0]._source.ins[0]._source
        
        # the amount of H2 reactioned is 0.046*biocrude amount (unchangeable)
        # the amount of H2 added can range from 1-3 times rxned amount
        if mixture.imass['H2'] < 0.046*mixture.imass['Biocrude']:
            raise Exception('H2 is too less, should be between '\
              f'[{0.046*mixture.imass["Biocrude"]/H2_split.split[0]:.2f}, '\
              f'{0.138*mixture.imass["Biocrude"]/H2_split.split[0]:.2f}] '\
              'kg/hr')
        elif mixture.imass['H2'] > 0.138*mixture.imass['Biocrude']:
            raise Exception('H2 is too much, should be between '\
              f'[{0.046*mixture.imass["Biocrude"]/H2_split.split[0]:.2f}, '\
              f'{0.138*mixture.imass["Biocrude"]/H2_split.split[0]:.2f}] '\
              'kg/hr')
        
        # *1.4 means biocrude amount + H2 reactioned amount
        biooil_total_mass = mixture.imass['Biocrude']*1.046*self.biooil_ratio
        for name, ratio in self.oil_composition.items():
            ht_out.imass[name] = biooil_total_mass*ratio
        
        gas_mass = mixture.imass['Biocrude']*1.046*self.gas_ratio
        for name, ratio in self.gas_composition.items():
            ht_out.imass[name] = gas_mass*ratio
            
        ht_out.imass['H2'] = mixture.imass['H2'] -\
                             mixture.imass['Biocrude']*0.046
        
        ht_out.imass['H2O'] = mixture.F_mass - biooil_total_mass -\
                              gas_mass - ht_out.imass['H2']
        # use water to represent HT aqueous phase,
        # C and N can be calculated base on MB closure.
        
        ht_out.P = self.HTout_pre
        
        ht_out.T = self.HTout_T
        
        self.HTL = self.ins[0]._source.ins[0]._source.ins[1]._source.ins[0]._source
        
        if self.HTaqueous_C < -0.1*self.HTL.biocrude_C:
            raise Exception('carbon mass balance is out of +/- 10%')
        # allow +/- 10% out of mass balance
        
        if self.HTaqueous_N < -0.1*self.HTL.biocrude_N:
            raise Exception('nitrogen mass balance is out of +/- 10%')
        # allow +/- 10% out of mass balance
        
        # possibility exist that more carbon is in biooil and gas than in
        # biocrude because we use the biooil/gas compositions to calculate
        # carbon. In this case, the C in HT aqueous phase will be negative.
        # It's OK if the mass balance is within +/- 10%. Otherwise, an
        # exception will be raised.
        
    @property
    def biooil_C(self):
        carbon = 0
        for name in self.oil_composition.keys():
            carbon += self.outs[0].imass[name]*cmps[name].i_C
        return carbon

    @property
    def biooil_N(self):
        nitrogen = 0
        for name in self.oil_composition.keys():
            nitrogen += self.outs[0].imass[name]*cmps[name].i_N
        return nitrogen

    @property
    def HTfuel_gas_C(self):
        carbon = 0
        for name in self.gas_composition.keys():
            carbon += self.outs[0].imass[name]*cmps[name].i_C
        return carbon

    @property
    def HTaqueous_C(self):
        return self.HTL.biocrude_C - self.biooil_C - self.HTfuel_gas_C

    @property
    def HTaqueous_N(self):
        return self.HTL.biocrude_N - self.biooil_N

    def _design(self):
        
        hx = self.heat_exchanger
        hx_ins0, hx_outs0 = hx.ins[0], hx.outs[0]
        hx_ins0.mix_from(self.outs)
        hx_outs0.mix_from(self.outs)
        hx_ins0.T = self.HTrxn_T # temperature before/after HT are different
        hx.T = hx_outs0.T
        hx.simulate_as_auxiliary_exchanger(ins=hx.ins, outs=hx.outs)
    
    def _cost(self):
        pass

# =============================================================================
# HC
# =============================================================================
   
class HC(SanUnit):
    
    '''
    Hydrocracking further cracks down heavy part in HT biooil to diesel and
    gasoline.
    
    Model method: use experimental data.
    
    Parameters
    ----------
    ins: Iterable (stream)
    mixture
    outs: Iterable (stream)
    gasoline, diesel, off_gas
    '''
    
    auxiliary_unit_names=('heat_exchanger',)
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 oil_ratio=0.955, off_gas_ratio=0.045,
                 # Jones et al., 2014
                 # spreadsheet HC calculation
                 HC_out_pre=1005.7*6894.76,
                 HC_rxn_T=451+273.15,
                 HC_out_T=60+273.15,
                 gas_composition = {'CO2':0.860, 'CH4':0.140},
                 # will not be a variable in uncertainty/sensitivity analysis
                 oil_composition = {'CYCHEX':0.0389,'HEXANE':0.0116,
                                    'HEPTANE':0.1202, 'OCTANE':0.0851,
                                    'C9H20':0.0952, 'C10H22':0.1231,
                                    'C11H24':0.1764, 'C12H26':0.1382,
                                    'C13H28':0.0974, 'C14H30':0.0486,
                                    'C15H32':0.0340, 'C16H34':0.0201,
                                    'C17H36':0.0045, 'C18H38':0.0010,
                                    'C19H40':0.0052, 'C20H42':0.0003},
                 #combine C20H42 and PHYTANE as C20H42
                 # will not be a variable in uncertainty/sensitivity analysis
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo,init_with)
        self.oil_ratio = oil_ratio
        self.off_gas_ratio = off_gas_ratio
        self.HC_out_pre = HC_out_pre
        self.HC_rxn_T = HC_rxn_T
        self.HC_out_T = HC_out_T
        self.gas_composition = gas_composition
        self.oil_composition = oil_composition
        hx_in = bst.Stream(f'{ID}_hx_in')
        hx_out = bst.Stream(f'{ID}_hx_out')
        self.heat_exchanger = HXutility(ID=f'{ID}_hx', ins=hx_in, outs=hx_out)
        
    _N_ins = 1
    _N_outs = 1
        
    def _run(self):
        
        mixture = self.ins[0]
        hc_out = self.outs[0]
        
        H2_splitter = self.ins[0]._source.ins[0]._source.ins[0]._source.ins[0]._source
        
        # the amount of H2 reactioned is 0.01125*heavy oil amount (unchangeable)
        # H2 amount should be OK here, but in case of not enough, add the
        # following exception (excess is OK):
        if mixture.imass['H2'] < 0.01125*mixture.F_mass:
            raise Exception('H2 is too less, the minimum should be '\
              f'[{0.01125*mixture.F_mass/(1 - H2_splitter.split[0]):.2f}')
    
        hc_oil_mass = mixture.F_mass*1.01125*self.oil_ratio

        for name, ratio in self.oil_composition.items():
            hc_out.imass[name] = hc_oil_mass*ratio

        hc_gas_mass = mixture.F_mass*1.01125*self.off_gas_ratio

        for name, ratio in self.gas_composition.items():
            hc_out.imass[name] = hc_gas_mass*ratio
        
        hc_out.imass['H2'] = mixture.imass['H2'] -\
                             mixture.F_mass*0.01125
        
        hc_out.P = self.HC_out_pre
        hc_out.T = self.HC_out_T
        
        C_in = 0
        total_num = len(list(cmps))
        for num in range(total_num):
            C_in += mixture.imass[str(list(cmps)[num])]*list(cmps)[num].i_C
            
        C_out = self.biooil_C + self.HCfuel_gas_C
        
        if C_out < 0.95*C_in or C_out > 1.05*C_out :
            raise Exception('carbon mass balance is out of +/- 5%')
        # make sure that carbon mass balance is within +/- 10%. Otherwise, an
        # exception will be raised.
        
    @property
    def biooil_C(self):
        carbon = 0
        for name in self.oil_composition.keys():
            carbon += self.outs[0].imass[name]*cmps[name].i_C
        return carbon
    
    @property
    def HCfuel_gas_C(self):
        carbon = 0
        for name in self.gas_composition.keys():
            carbon += self.outs[0].imass[name]*cmps[name].i_C
        return carbon

    def _design(self):
        
        hx = self.heat_exchanger
        hx_ins0, hx_outs0 = hx.ins[0], hx.outs[0]
        hx_ins0.mix_from(self.outs)
        hx_outs0.mix_from(self.outs)
        hx_ins0.T = self.HC_rxn_T # temperature before/after HC are different
        hx.T = hx_outs0.T
        hx.simulate_as_auxiliary_exchanger(ins=hx.ins, outs=hx.outs)
    
    def _cost(self):
        pass
    
class WWmixer(SanUnit):
    '''
    A fake unit that mix all wastewater streams and calculates C, N, P, and H2O
    amount.
    
    Model method: elements calculation, don't need _design and _cost.
    
    Parameters
    ----------
    ins: Iterable (stream)
        supernatant_1, supernatant_2, memdis_ww, ht_ww
    outs: Iterable (stream)
        mixture
    '''
    
    def __init__(self, ID='', ins=None, outs=(), thermo=None,
                 init_with='Stream',
                 **kwargs):
        
        SanUnit.__init__(self, ID, ins, outs, thermo, init_with)

    _N_ins = 4
    _N_outs = 1
        
    def _run(self):
        
        supernatant_1, supernatant_2, memdis_ww, ht_ww = self.ins
        mixture = self.outs[0]
        
        mixture.mix_from(self.ins)
        
        HT = self.ins[3]._source.ins[0]._source.ins[0]._source.ins[0]._source
        
        # only account for C and N from HT if they are not less than 0
        if HT.HTaqueous_C >= 0:
            mixture.imass['C'] += HT.HTaqueous_C
            mixture.imass['H2O'] -= HT.HTaqueous_C
        if HT.HTaqueous_N >=0:
            mixture.imass['N'] += HT.HTaqueous_N
            mixture.imass['H2O'] -= HT.HTaqueous_N

    def _design(self):
        pass
    
    def _cost(self):
        pass

