#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code is based on Bwaise systems.py developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/QSDsan/blob/master/LICENSE.txt
for license details.
"""
import numpy as np
import biosteam as bst
import qsdsan as qs
from qsdsan import sanunits as su
from qsdsan import WasteStream, ImpactIndicator, ImpactItem, StreamImpactItem, SimpleTEA, LCA
from _cmps import cmps


# =============================================================================
# Unit parameters
# =============================================================================
bst.settings.set_thermo(cmps)

currency = qs.currency = 'USD'
bst.speed_up()

household_size = 4
get_household_size = lambda: household_size
household_per_toilet = 5
get_household_per_toilet = lambda: household_per_toilet
get_toilet_user = lambda: get_household_size()*get_household_per_toilet()

# Number of people served by the Reclaimer 2.0 (30 users)
#For every 30 users, check the sanunits to add additional units based how you scale up
ppl = 120

#For every 25 people, you will want to add a toilet room (portable toilet/porta potty)
toilets = ppl/25
ppl_toilet = ppl / toilets

#For every 30 people you will want to add a reclaimer unit
reclaimer_units = ppl/30


discount_rate = 0.05
get_discount_rate = lambda: discount_rate

# Time take for full degradation, [yr]
tau_deg = 2
# Log reduction at full degradation
log_deg = 3
# Get reduction rate constant k for COD and N, use a function so that k can be
def get_decay_k(tau_deg=2, log_deg=3):
    k = (-1/tau_deg)*np.log(10**-log_deg)
    return k


max_CH4_emission = 0.25
get_max_CH4_emission = lambda: max_CH4_emission

# =============================================================================
# Prices and GWP CFs
# =============================================================================

# Recycled nutrients are sold at a lower price than commercial fertilizers
price_factor = 0.25
get_price_factor = lambda: price_factor

price_ratio = 1

operator_daily_wage = 29
get_operator_daily_wage = lambda: operator_daily_wage

price_dct = {
    'Electricity': 0.06,
    'wages': 1.213,
    'Concrete': 194,
    'Steel': 2.665,
    'N': 1.507*get_price_factor(),
    'P': 3.983*get_price_factor(),
    'K': 1.333*get_price_factor(),
    'Polymer': 0.75,
    'Resin': 3.335,
    'FilterBag': 4.81,
    'MgOH2': 0,
    'MgCO3': 0.9,
    'H2SO4': 0.3,
    'struvite': 0,
    'salt': 0, 
    'HCl': 0,
    'KCl': 0, 
    'GAC': 0,
    'Zeolite': 0,
    'Conc_NH3': 0, 
    'sludge': 0
    }


GWP_dct = {
    'Electricity': 0.69,
    'CH4': 28,
    'N2O': 265,
    'N': -5.4,
    'P': -4.9,
    'K': -1.5,
    'Polymer':2.8,
    'Resin': 1.612,
    'FilterBag': 0.464,
    'MgOH2': 1.176277921,
    'MgCO3': 1.176277921,
    'H2SO4': 0.158899487,
    'struvite': 0,
    'salt': 0.266695553, 
    'HCl': 0.8,
    'KCl': 0.8,
    'GAC': 8.388648277,
    'Zeolite': 5.175,
    'Conc_NH3':0,
    'sludge':0
    }

items = ImpactItem.get_all_items()


if not items.get('Excavation'):
    import os
    path = os.path.dirname(os.path.realpath(__file__)) + '/data'
    ImpactIndicator.load_from_file(path+'/impact_indicators.csv')
    item_path = path+'/_impact_item.xlsx'
    ImpactItem.load_from_file(item_path)
    del os

GWP = qs.ImpactIndicator.get_indicator('GWP')

bst.PowerUtility.price = price_dct['Electricity']
items['Concrete'].price = price_dct['Concrete']
items['Steel'].price = price_dct['Steel']

# =============================================================================
# Universal units and functions
# =============================================================================

CH4_item = StreamImpactItem(ID='CH4_item', GWP=GWP_dct['CH4'])
N2O_item = StreamImpactItem(ID='N2O_item', GWP=GWP_dct['N2O'])
N_item = StreamImpactItem(ID='N_item', GWP=GWP_dct['N'])
P_item = StreamImpactItem(ID='P_item', GWP=GWP_dct['P'])
K_item = StreamImpactItem(ID='K_item', GWP=GWP_dct['K'])
e_item = ImpactItem(ID='e_item', functional_unit='kWh', GWP=GWP_dct['Electricity'])
polymer_item = StreamImpactItem(ID='polymer_item', GWP=GWP_dct['Polymer'])
resin_item = StreamImpactItem(ID='resin_item', GWP=GWP_dct['Resin'])
filter_bag_item = StreamImpactItem(ID='filter_bag_item', GWP=GWP_dct['FilterBag'])
MgOH2_item = StreamImpactItem(ID='MgOH2_item', GWP=GWP_dct['MgOH2'])
MgCO3_item = StreamImpactItem(ID='MgCO3_item', GWP=GWP_dct['MgCO3'])
H2SO4_item = StreamImpactItem(ID='H2SO4_item', GWP=GWP_dct['H2SO4'])
struvite_item = StreamImpactItem(ID = 'struvite_item', GWP=GWP_dct['struvite'])
salt_item = StreamImpactItem(ID = 'salt_item', GWP=GWP_dct['salt'])
KCl_item = StreamImpactItem(ID = 'KCl_item', GWP=GWP_dct['KCl'])
GAC_item = StreamImpactItem(ID='GAC_item', GWP=GWP_dct['GAC'])
Zeolite_item = StreamImpactItem(ID='Zeolite_item', GWP=GWP_dct['Zeolite'])
Conc_NH3_item = StreamImpactItem(ID='Conc_NH3', GWP=GWP_dct['Conc_NH3'])
HCl = StreamImpactItem(ID='HCl', GWP=GWP_dct['HCl'])
sludge_item = StreamImpactItem(ID = 'sludge_item', GWP=GWP_dct['sludge'])

def batch_create_streams(prefix):
    stream_dct = {}
    stream_dct['CH4'] = WasteStream(f'{prefix}_CH4', phase='g',
                                    stream_impact_item=CH4_item.copy(set_as_source=True))
    stream_dct['N2O'] = WasteStream(f'{prefix}_N2O', phase='g',
                                    stream_impact_item=N2O_item.copy(set_as_source=True))
    stream_dct['liq_N'] = WasteStream(f'{prefix}_liq_N', phase='l', price=price_dct['N'],
                                      stream_impact_item=N_item.copy(set_as_source=True))
    stream_dct['sol_N'] = WasteStream(f'{prefix}_sol_N', phase='l', price=price_dct['N'],
                                      stream_impact_item=N_item.copy(set_as_source=True))
    stream_dct['liq_P'] = WasteStream(f'{prefix}_liq_P', phase='l', price=price_dct['P'],
                                      stream_impact_item=P_item.copy(set_as_source=True))
    stream_dct['sol_P'] = WasteStream(f'{prefix}_sol_P', phase='l', price=price_dct['P'],
                                      stream_impact_item=P_item.copy(set_as_source=True))
    stream_dct['liq_K'] = WasteStream(f'{prefix}_liq_K', phase='l', price=price_dct['K'],
                                      stream_impact_item=K_item.copy(set_as_source=True))
    stream_dct['sol_K'] = WasteStream(f'{prefix}_sol_K', phase='l', price=price_dct['K'],
                                      stream_impact_item=K_item.copy(set_as_source=True))
    stream_dct['polymer'] = WasteStream(f'{prefix}_polymer', phase='s', price=price_dct['Polymer'],
                                      stream_impact_item=resin_item.copy(set_as_source=True))
    stream_dct['resin'] = WasteStream(f'{prefix}_resin', phase='s', price=price_dct['Resin'],
                                      stream_impact_item=resin_item.copy(set_as_source=True))
    stream_dct['filter_bag'] = WasteStream(f'{prefix}_filter_bag', phase='s', price=price_dct['FilterBag'],
                                      stream_impact_item=filter_bag_item.copy(set_as_source=True))
    stream_dct['MgOH2'] = WasteStream(f'{prefix}_MgOH2', phase='s', price=price_dct['MgOH2'],
                                      stream_impact_item=MgOH2_item.copy(set_as_source=True))
    stream_dct['MgCO3'] = WasteStream(f'{prefix}_MgCO3', phase='s', price=price_dct['MgCO3'],
                                      stream_impact_item=MgCO3_item.copy(set_as_source=True))
    stream_dct['H2SO4'] = WasteStream(f'{prefix}_H2SO4', phase='s', price=price_dct['H2SO4'],
                                      stream_impact_item=H2SO4_item.copy(set_as_source=True))
    stream_dct['struvite'] = WasteStream(f'{prefix}_struvite', phase='s', price=price_dct['struvite'],
                                      stream_impact_item=struvite_item.copy(set_as_source=True))
    stream_dct['salt'] = WasteStream(f'{prefix}_salt', phase='s', price=price_dct['salt'],
                                      stream_impact_item=salt_item.copy(set_as_source=True))
    stream_dct['KCl'] = WasteStream(f'{prefix}_KCl', phase='l', price=price_dct['KCl'],
                                      stream_impact_item=KCl_item.copy(set_as_source=True))
    stream_dct['GAC'] = WasteStream(f'{prefix}_GAC', phase='s', price=price_dct['GAC'], 
                                      stream_impact_item=GAC_item.copy(set_as_source=True))
    stream_dct['Zeolite'] = WasteStream(f'{prefix}_Zeolite', phase='s', price=price_dct['Zeolite'], 
                                      stream_impact_item=Zeolite_item.copy(set_as_source=True))
    stream_dct['Conc_NH3'] = WasteStream(f'{prefix}_Conc_NH3', phase='s', price=price_dct['Conc_NH3'], 
                                      stream_impact_item=Conc_NH3_item.copy(set_as_source=True))
    stream_dct['HCl'] = WasteStream(f'{prefix}_HCl', phase='l', price=price_dct['HCl'], 
                                      stream_impact_item=Conc_NH3_item.copy(set_as_source=True))           
  
    

    return stream_dct
    

def add_fugitive_items(unit, item):
    unit._run()
    for i in unit.ins:
        i.stream_impact_item = item.copy(set_as_source=True)
        


# %%

# =============================================================================
# Scenario A (sysA): Duke Reclaimer Design 2.0 Solids Treatment Only 
# =============================================================================

flowsheetA = bst.Flowsheet('sysA')
bst.main_flowsheet.set_flowsheet(flowsheetA)

streamsA = batch_create_streams('A')

#################### Human Inputs ####################
A1 = su.Excretion('A1', outs=('urine','feces'))

###################### Treatment ######################
#Septic Tank 
A3 = su.PrimaryReclaimer('A3', ins=(A1-0, streamsA['MgOH2']), 
                    outs=('A3_treated', 'A3_CH4', 'A3_N2O', 'A3_sludge', streamsA['struvite']), 
                    decay_k_COD=get_decay_k(tau_deg, log_deg), 
                    decay_k_N=get_decay_k(tau_deg, log_deg),
                    max_CH4_emission=get_max_CH4_emission())

A4 = su.SludgePasteurization('A4', ins=(A3-3, 'air', 'lpg'), outs=('treated_sludge'),
                                 heat_loss=0.1, target_MC = 0.1, sludge_temp = 283.15, 
                              temp_pasteurization=343.15, lhv_lpg = 48.5)


#Double check the mixer
A8 = su.Mixer('A8', ins=(A3-1), outs=streamsA['CH4'])
A8.specification = lambda: add_fugitive_items(A8, CH4_item)
A8.line = 'fugitive CH4 mixer' 
        
A9 = su.Mixer('A9', ins=(A3-2), outs=streamsA['N2O'])
A9.specification = lambda: add_fugitive_items(A9, N2O_item)
A9.line = 'fugitive N2O mixer'

############### Simulation, TEA, and LCA ###############
sysA = bst.System('sysA', path= (A1, A3, A4))
sysA.simulate()

power = sum([u.power_utility.rate for u in sysA.units])

teaA = SimpleTEA(system=sysA, discount_rate=get_discount_rate(),  
                  start_year=2020, lifetime=20, uptime_ratio=1, 
                  lang_factor=None, annual_maintenance=0, 
                  annual_labor = (A4._calc_labor_cost() * 8760))

lcaA = LCA(system=sysA, lifetime=20, lifetime_unit='yr', uptime_ratio=1,
            e_item=lambda: power*(365*24)*20)

# =============================================================================
# System B Duke Reclaimer 2.0 Full System on grid-tied energy
# =============================================================================
flowsheetB= bst.Flowsheet('sysB')
bst.main_flowsheet.set_flowsheet(flowsheetB)

streamsB = batch_create_streams('B')

#################### Human Inputs ####################
B1 = su.Excretion('B1', outs=('urine','feces'))

################### User Interface ###################
#Reclaimer 2.0 can process ~30L/hr(net), 720L/24 hours of constant operation
#flush volume of 6L per flush determines the number of users would be 120 users
B2 = su.MURTToilet('B2', ins=(B1-0, B1-1,
                              'toilet_paper', 'flushing_water',
                              'cleansing_water', 'desiccant'),
                    outs=('mixed_waste', 'B2_CH4', 'B2_N2O'),
                    decay_k_COD=get_decay_k(tau_deg, log_deg), 
                    decay_k_N=get_decay_k(tau_deg, log_deg),
                    max_CH4_emission=get_max_CH4_emission(),
                    N_user=ppl_toilet, ppl = ppl, lifetime=8,
                    if_flushing=True, if_desiccant=False, if_toilet_paper=True,
                    CAPEX = 0, OPEX_over_CAPEX= 0.07) 

##################### Treatment ######################
B3 = su.PrimaryReclaimer('B3', ins=(B1-0, streamsB['MgOH2']), 
                    outs=('B3_treated', 'B3_CH4', 'B3_N2O', 'B3_sludge', streamsB['struvite']), 
                    decay_k_COD=get_decay_k(tau_deg, log_deg), 
                    decay_k_N=get_decay_k(tau_deg, log_deg),
                    max_CH4_emission=get_max_CH4_emission())

B4 = su.SludgePasteurization('B4', ins=(B3-3, 'air', 'lpg'), outs=('treated_sludge'),
                                 heat_loss=0.1, target_MC = 0.1, sludge_temp = 283.15, 
                              temp_pasteurization=343.15, lhv_lpg = 48.5)

B5 = su.Ultrafiltration('B5', ins=(B3-0), outs = ('B5_treated', 'retentate'))
                        
B6 = su.IonExchangeReclaimer('B6', ins=(B5-0, streamsB['Zeolite'], streamsB['GAC'], streamsB['KCl']),
                                outs=('B6_treated', 'SpentZeolite', 'SpentGAC',streamsB['Conc_NH3']),
                                decay_k_COD=get_decay_k(tau_deg, log_deg), 
                                decay_k_N=get_decay_k(tau_deg, log_deg),
                                max_CH4_emission=get_max_CH4_emission(), if_gridtied=True)

B7 = su.ECR_Reclaimer('B7', ins=(B6-0), 
                    outs = ('B7_treated'),
                    decay_k_COD=get_decay_k(tau_deg, log_deg),)


B8 = su.Mixer('B8', ins=(B3-1), outs=streamsB['CH4'])
B8.specification = lambda: add_fugitive_items(B7, CH4_item)
B8.line = 'fugitive CH4 mixer' 
        
B9 = su.Mixer('B9', ins=(B3-2), outs=streamsB['N2O'])
B9.specification = lambda: add_fugitive_items(B8, N2O_item)
B9.line = 'fugitive N2O mixer'

################## Other impacts and costs ##################
B10 = su.HousingReclaimer('B10', ins=(B7-0), outs = ('B10_out'))
B11 = su.SystemReclaimer('B11', ins=(B10-0), outs = ('B11_out'))


############### Simulation, TEA, and LCA ###############
sysB = bst.System('sysB', path= (B1, B3, B4, B5, B6, B7, B8, B9, B10, B11))
sysB.simulate()

def update_labor_costs_sysB():
    teaB.annual_labor = (B4._calc_maintenance_labor_cost() * 8760) + (B6._calc_maintenance_labor_cost() * 8760)


powerB = sum([u.power_utility.rate for u in sysB.units])

teaB = SimpleTEA(system=sysB, discount_rate=get_discount_rate(),  
                  start_year=2020, lifetime=20, uptime_ratio=1, 
                  lang_factor=None, annual_maintenance=0, 
                  annual_labor = (B4._calc_labor_cost() * 8760) 
                  + (B6._calc_labor_cost() * 8760))  

lcaB = LCA(system=sysB, lifetime=20, lifetime_unit='yr', uptime_ratio=1,
            e_item=lambda: powerB*(365*24)*20)

# =============================================================================
# System C Duke Reclaimer 2.0 coupled with solar volatic system 
# =============================================================================
flowsheetC= bst.Flowsheet('sysC')
bst.main_flowsheet.set_flowsheet(flowsheetC)

streamsC = batch_create_streams('C')

#################### Human Inputs ####################
C1 = su.Excretion('C1', outs=('urine','feces'))

################### User Interface ###################
#Reclaimer 2.0 can process ~30L/hr(net), 720L/24 hours of constant operation
#flush volume of 6L per flush determines the number of users would be 120 users
C2 = su.MURTToilet('C2', ins=(C1-0, C1-1,
                              'toilet_paper', 'flushing_water',
                              'cleansing_water', 'desiccant'),
                    outs=('mixed_waste', 'C2_CH4', 'C2_N2O'),
                    decay_k_COD=get_decay_k(tau_deg, log_deg), 
                    decay_k_N=get_decay_k(tau_deg, log_deg),
                    max_CH4_emission=get_max_CH4_emission(),
                    N_user=ppl_toilet, ppl = ppl, lifetime=8, 
                    if_flushing=True, if_desiccant=False, if_toilet_paper=True,
                    CAPEX = 0,
                    OPEX_over_CAPEX= 0.07) 

###################### Treatment ######################
#Septic Tank 
C3 = su.PrimaryReclaimer('C3', ins=(C2-0, streamsC['MgOH2']), 
                    outs=('C3_treated', 'C3_CH4', 'C3_N2O', 'C3_sludge', streamsC['struvite']), 
                    decay_k_COD=get_decay_k(tau_deg, log_deg), 
                    decay_k_N=get_decay_k(tau_deg, log_deg),
                    max_CH4_emission=get_max_CH4_emission())

C4 = su.SludgePasteurization('C4', ins=(C3-3, 'air', 'lpg'), outs=('treated_sludge'),
                                  heat_loss=0.1, target_MC = 0.1, sludge_temp = 283.15, 
                              temp_pasteurization=343.15, lhv_lpg = 48.5)


C5 = su.Ultrafiltration('C5', ins=(C3-0), outs = ('C5_treated', 'retentate'))
                        
C6 = su.IonExchangeReclaimer('C6', ins=(C5-0, streamsC['Zeolite'], streamsC['GAC'], streamsC['KCl']),
                                outs=('C6_treated', 'SpentZeolite', 'SpentGAC',streamsC['Conc_NH3']),
                                decay_k_COD=get_decay_k(tau_deg, log_deg), 
                                decay_k_N=get_decay_k(tau_deg, log_deg),
                                max_CH4_emission=get_max_CH4_emission(), if_gridtied=True)

C7 = su.ECR_Reclaimer('C7', ins=(C6-0), 
                    outs = ('C7_treated'),
                    decay_k_COD=get_decay_k(tau_deg, log_deg),)


C8 = su.Mixer('C8', ins=(C3-1, C2-1), outs=streamsC['CH4'])
C8.specification = lambda: add_fugitive_items(C7, CH4_item)
C8.line = 'fugitive CH4 mixer' 
        
C9 = su.Mixer('B9', ins=(C3-2, C2-2), outs=streamsC['N2O'])
C9.specification = lambda: add_fugitive_items(C8, N2O_item)
C9.line = 'fugitive N2O mixer'

################## Other impacts and costs ##################
C10 = su.HousingReclaimer('C10', ins=(C7-0), outs = ('C10_out'))
C11 = su.SystemReclaimer('C11', ins=(C10-0), outs = ('C11_out'))
C12 = su.SolarReclaimer('C12', ins=(C11-0), outs = ('C12_out'))

############### Simulation, TEA, and LCA ###############
sysC = bst.System('sysC', path= (C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12))
sysC.simulate()

def update_labor_costs_sysC():
    teaC.annual_labor = (C4._calc_maintenance_labor_cost() * 8760) + (C6._calc_maintenance_labor_cost() * 8760)

powerC = 0
teaC = SimpleTEA(system=sysC, discount_rate=get_discount_rate(),  
                  start_year=2020, lifetime=20, uptime_ratio=1,
                  lang_factor=None, annual_maintenance=0,
                  annual_labor = (C4._calc_labor_cost() * 8760) 
                  + (C6._calc_labor_cost() * 8760) 
                  + (C12._calc_labor_cost() * 8760))  

lcaC = LCA(system=sysC, lifetime=20, lifetime_unit='yr', uptime_ratio=1,
            e_item=lambda: powerC*(365*24)*20)


# =============================================================================
# Scenario D (sysD): Targeted Nitrogen Removal Only 
# =============================================================================

flowsheetD = bst.Flowsheet('sysD')
bst.main_flowsheet.set_flowsheet(flowsheetD)

streamsD = batch_create_streams('D')

#################### Human Inputs ####################
D1 = su.Excretion('D1', outs=('urine','feces')) 

###################### Treatment ######################
D3 = su.PrimaryReclaimer('D3', ins=(D1-0, streamsD['MgOH2']), 
                    outs=('D3_treated', 'D3_CH4', 'D3_N2O', 'D3_sludge', streamsD['struvite']), 
                    decay_k_COD=get_decay_k(tau_deg, log_deg), 
                    decay_k_N=get_decay_k(tau_deg, log_deg),
                    max_CH4_emission=get_max_CH4_emission())



D4 = su.Ultrafiltration('D4', ins=(D3-0), outs = ('D4_treated', 'retentate'))
                        
D5 = su.IonExchangeReclaimer('D5', ins=(D4-0, streamsD['Zeolite'], streamsD['GAC'], streamsD['KCl']),
                                outs=('D5_treated', 'SpentZeolite', 'SpentGAC',streamsD['Conc_NH3']),
                                decay_k_COD=get_decay_k(tau_deg, log_deg), 
                                decay_k_N=get_decay_k(tau_deg, log_deg),
                                max_CH4_emission=get_max_CH4_emission())

D6 = su.Mixer('D6', ins=(D3-1), outs=streamsD['CH4'])
D6.specification = lambda: add_fugitive_items(D6, CH4_item)
D6.line = 'fugitive CH4 mixer' 
        
D7 = su.Mixer('D7', ins=(D3-2), outs=streamsD['N2O'])
D7.specification = lambda: add_fugitive_items(D7, N2O_item)
D7.line = 'fugitive N2O mixer'

################## Other impacts and costs ##################
D8 = su.HousingReclaimer('D8', ins=(D5-0), outs = ('D8_out'))
D9 = su.SystemReclaimer('D9', ins=(D8-0), outs = ('D9_out'))

############### Simulation, TEA, and LCA ###############
sysD = bst.System('sysD', path= (D1, D3, D4, D5, D6, D7, D8, D9))
sysD.simulate()

powerD = sum([u.power_utility.rate for u in sysD.units])

teaD = SimpleTEA(system=sysD, discount_rate=get_discount_rate(),  
                  start_year=2020, lifetime=20, uptime_ratio=1, 
                  lang_factor=None, annual_maintenance=0, 
                  annual_labor = (D5._calc_labor_cost() * 8760))
                    


lcaD = LCA(system=sysD, lifetime=20, lifetime_unit='yr', uptime_ratio=1,
            e_item=lambda: powerD*(365*24)*20)


# =============================================================================
# Summarizing Functions
# =============================================================================

sys_dct = {
    'ppl':  dict(sysA=ppl, sysB=ppl, sysC=ppl, sysD = ppl),
    'input_unit': dict(sysA=A1, sysB=B1, sysC=C1, sysD=D1),
    'liq_unit': dict(sysA=None, sysB=None, sysC=None, sysD=None),
    'sol_unit': dict(sysA=None, sysB=None, sysC=None, sysD=None),
    'gas_unit': dict(sysA=None, sysB=None, sysC=None, sysD=None),
    'stream_dct': dict(sysA=streamsA, sysB=streamsB, sysC=streamsC, sysD=streamsD),
    'TEA': dict(sysA=teaA, sysB = teaB, sysC = teaC, sysD=teaD),
    'LCA': dict(sysA=lcaA, sysB=lcaB, sysC=lcaC, sysD=lcaD),
    'cache': dict(sysA={}, sysB={}, sysC={}, sysD={}),
    }


system_streams = {sysA:streamsA, sysB:streamsB, sysC:streamsC, sysD:streamsD}

#learning curve assumptions
percent_CAPEX_to_scale = 0.1 #this number is the decimal of the fraction of scost of pecialty parts/cost of total parts
get_percent_CAPEX_to_scale = lambda: percent_CAPEX_to_scale

number_of_units = 100000

percent_limit = 0.015
get_percent_limit = lambda: percent_limit

learning_curve_percent=0.925
get_learning_curve_percent = lambda: learning_curve_percent

def get_scaled_capital(tea):
    CAPEX_to_scale = tea.annualized_CAPEX * get_percent_CAPEX_to_scale()
    CAPEX_not_scaled = tea.annualized_CAPEX - CAPEX_to_scale
    scaled_limited = CAPEX_to_scale * get_percent_limit()
    b=(np.log(get_learning_curve_percent())/np.log(2))
    scaled_CAPEX_annualized  = (CAPEX_to_scale - scaled_limited)*number_of_units**b+scaled_limited    
    new_CAPEX_annualized = scaled_CAPEX_annualized + CAPEX_not_scaled    
    return new_CAPEX_annualized

#shions code
def get_cost_capex(unit,tea,ppl):
    capex = 0
    if type(unit)== tuple:
        for i in unit:
            capex+=tea.get_unit_annualized_CAPEX(i)/365/ppl
    return capex

def get_cost_scaled_capex(unit,tea,ppl):
    capex = 0
    if type(unit)== tuple:
        for i in unit:
            capex+=tea.get_unit_annualized_CAPEX(i)/365/ppl
            capex_to_scale = capex * get_percent_CAPEX_to_scale()
            capex_not_scaled = capex - capex_to_scale
            scaled_limited = capex_to_scale * get_percent_limit()
            b=(np.log(get_learning_curve_percent())/np.log(2))
            annualized_scaled_capex = (capex_to_scale - scaled_limited)*number_of_units**b+scaled_limited  
            scaled_capex = annualized_scaled_capex + capex_not_scaled
    return scaled_capex

def get_cost_opex(unit,ppl):
    opex = 0
    if type(unit)== tuple:
        for i in unit:
            opex+=sum(i._add_OPEX.values())*24/ppl
            for stream in i.ins:
                opex+=stream.imass['Polyacrylamide']*streamsA['polymer'].price*24/ppl
                opex+=stream.imass['MagnesiumHydroxide']*streamsA['MgOH2'].price*24/ppl
                opex+=stream.imass['MgCO3']*streamsA['MgCO3'].price*24/ppl
                opex+=stream.imass['H2SO4']*streamsA['H2SO4'].price*24/ppl
                opex+=stream.imass['FilterBag']*streamsA['filter_bag'].price*24/ppl
                opex+=stream.imass['Polystyrene']*streamsA['resin'].price*24/ppl
                opex+=stream.imass['GAC']*streamsA['GAC'].price*24/ppl
                opex+=stream.imass['Zeolite']*streamsA['Zeolite'].price*24/ppl
                opex+=stream.imass['SodiumHydroxide']*streamsA['NaOH'].price*24/ppl
    return opex

def get_cost_opex_labor(unit,ppl):
    opex = 0
    if type(unit)== tuple:
        for i in unit:
            opex=i._calc_maintenance_labor_cost()*24/ppl
    return opex

def get_cost_opex_replacement(unit,ppl):
    opex = 0
    if type(unit)== tuple:
        for i in unit:
            opex=i._calc_replacement_cost()*24/ppl
    return opex
    
def get_cost_electricity(unit,ppl):
    electricity = 0
    if type(unit)== tuple:
        for i in unit:
            electricity+=i.power_utility.cost*24/ppl
    return electricity

def get_cost_opex_streams(unit,ppl):
    opex = 0
    if type(unit)== tuple:
        for i in unit:
            for stream in i.ins:
                opex+=stream.imass['MagnesiumHydroxide']*streamsA['MgOH2'].price*24/ppl
                opex+=stream.imass['MgCO3']*streamsA['MgCO3'].price*24/ppl
                opex+=stream.imass['H2SO4']*streamsA['H2SO4'].price*24/ppl
                opex+=stream.imass['FilterBag']*streamsA['filter_bag'].price*24/ppl
                opex+=stream.imass['GAC']*streamsA['GAC'].price*24/ppl              
                opex+=stream.imass['Zeolite']*streamsA['Zeolite'].price*24/ppl
    return opex
        
def get_ghg_electricity(unit,ppl):
    electricity = 0
    if type(unit)== tuple:
        for i in unit:
            electricity+=i.power_utility.consumption*i.uptime_ratio*e_item.CFs['GlobalWarming']*12*365/ppl
            electricity+=-i.power_utility.production*i.uptime_ratio*e_item.CFs['GlobalWarming']*12*365/ppl
    return electricity


def get_total_inputs(unit):
    if len(unit.ins) == 0: # Excretion units do not have ins
        ins = unit.outs
    else:
        ins = unit.ins
    inputs = {}
    inputs['COD'] = sum(i.COD*i.F_vol/1e3 for i in ins)
    inputs['N'] = sum(i.TN*i.F_vol/1e3 for i in ins)
    inputs['NH3'] = sum(i.imass['NH3'] for i in ins)
    inputs['P'] = sum(i.TP*i.F_vol/1e3 for i in ins)
    inputs['K'] = sum(i.TK*i.F_vol/1e3 for i in ins)
    hr = 365 * 24
    for i, j in inputs.items():
        inputs[i] = j * hr
    return inputs

def get_recovery(ins=None, outs=None, hr=365*24, ppl=1, if_relative=True):
    try: iter(outs)
    except: outs = (outs,)
    non_g = tuple(i for i in outs if i.phase != 'g')
    recovery = {}
    recovery['COD'] = sum(i.COD*i.F_vol/1e3 for i in non_g)
    recovery['N'] = sum(i.TN*i.F_vol/1e3 for i in non_g)
    recovery['NH3'] = sum(i.imass['NH3'] for i in non_g)
    recovery['P'] = sum(i.TP*i.F_vol/1e3 for i in non_g)
    recovery['K'] = sum(i.TK*i.F_vol/1e3 for i in non_g)
    for i, j in recovery.items():
        if if_relative:
            inputs = get_total_inputs(ins)
            recovery[i] /= inputs[i]/hr * ppl
        else:
            recovery[i] /= 1/hr * ppl
    return recovery

def get_stream_emissions(streams=None, hr=365*24, ppl=1):
    try: iter(streams)
    except: streams = (streams,)
    emission = {}
    factor = hr / ppl
    for i in streams:
        if not i.stream_impact_item: continue
        emission[f'{i.ID}'] = i.F_mass*i.stream_impact_item.CFs['GlobalWarming']*factor
    return emission

#20 corresponds to year
def get_fugitive_emissions(streams=None, hr=365*24*20):
    try: iter(streams)
    except: streams = (streams,)
    factor = hr
    emission=0
    for i in streams:
        if not i.stream_impact_item: continue
        emission = i.F_mass*i.stream_impact_item.CFs['GlobalWarming']*factor
    return emission

#N2O and CH4 emissions
def get_fugitive_gases(system_num=None):
    fugitive_streams = ('CH4', 'N2O')
    gases = 0
    for i in fugitive_streams:
        gases+=get_fugitive_emissions(system_streams[system_num][i])
    return gases

def get_summarizing_fuctions():
    func_dct = {}
    func_dct['get_annual_cost'] = lambda tea, ppl: (tea.EAC-tea.annualized_CAPEX
                                                    +get_scaled_capital(tea))/ppl
    func_dct['get_annual_CAPEX'] = lambda tea, ppl: get_scaled_capital(tea)/ppl
    func_dct['get_annual_energy'] = lambda tea, ppl: sum(i.power_utility.cost for i in tea.units)*tea.operating_hours/ppl
    func_dct['get_annual_OPEX'] = lambda tea, ppl: (tea.AOC/ppl -(sum(i.power_utility.cost for i in tea.units)
                                                    *tea.operating_hours/ppl) - (tea.annual_labor/ppl))
    func_dct['get_annual_labor'] = lambda tea, ppl: tea.annual_labor/ppl
    func_dct['get_annual_sales'] = lambda tea, ppl: (tea.sales/ppl)
    ind = 'GlobalWarming'
    func_dct['get_annual_GWP'] = \
        lambda lca, ppl: lca.total_impacts[ind]/lca.lifetime/ppl
    func_dct['get_constr_GWP'] = \
        lambda lca, ppl: lca.total_construction_impacts[ind]/lca.lifetime/ppl
    func_dct['get_trans_GWP'] = \
        lambda lca, ppl: lca.total_transportation_impacts[ind]/lca.lifetime/ppl  
    func_dct['get_CH4_N2O_GWP'] = \
        lambda sys, lca, ppl: get_fugitive_gases(sys)/lca.lifetime/ppl
    func_dct['get_stream_items_emission_GWP'] = \
        lambda sys, lca, ppl: (lca.get_stream_impacts(stream_items=lca.stream_inventory, kind='direct_emission')[ind]) \
            /lca.lifetime/ppl - (get_fugitive_gases(sys)/lca.lifetime/ppl) #maybe ignore
    func_dct['get_offset_GWP'] = \
        lambda lca, ppl: lca.get_stream_impacts(stream_items=lca.stream_inventory, kind='offset')[ind] \
            /lca.lifetime/ppl
    func_dct['get_other_GWP'] = \
        lambda lca, ppl: lca.total_other_impacts[ind]/lca.lifetime/ppl
    return func_dct


def print_summaries(systems):
    try: iter(systems)
    except: systems = (systems, )
    func = get_summarizing_fuctions()
    for sys in systems:
        sys.simulate()
        ppl = sys.path[1].ppl
        print(f'\n---------- Summary for {sys} ----------\n')
        tea = sys_dct['TEA'][sys.ID]
        tea.show()
        print('\n')
        lca = sys_dct['LCA'][sys.ID]
        lca.show()
        
        unit = f'{currency}/cap/yr'
        print(f'\nTotal cost: {func["get_annual_cost"](tea, ppl):.2f} {unit}.')
        print(f'Capital: {func["get_annual_CAPEX"](tea, ppl):.2f} {unit}.')
        print(f'Energy: {func["get_annual_energy"](tea,ppl):.2f} {unit}.')
        print(f'Operating: {func["get_annual_OPEX"](tea, ppl):.2f} {unit}.')
        print(f'Labor: {func["get_annual_labor"](tea, ppl):.2f} {unit}.')
        print(f'Sales: {func["get_annual_sales"](tea, ppl):.2f} {unit}.')
        
        unit = f'{GWP.unit}/cap/yr'
        print(f'\nNet emission: {func["get_annual_GWP"](lca, ppl):.2f} {unit}.')
        print(f'Construction: {func["get_constr_GWP"](lca, ppl):.2f} {unit}.')
        print(f'Transportation: {func["get_trans_GWP"](lca, ppl):.2f} {unit}.')
        print(f'Fugitive gas: {func["get_CH4_N2O_GWP"](sys, lca, ppl):.2f} {unit}.')
        print(f'Stream items emission: {func["get_stream_items_emission_GWP"](sys, lca, ppl):.2f} {unit}.')
        print(f'Offset: {func["get_offset_GWP"](lca, ppl):.2f} {unit}.')
        print(f'Other: {func["get_other_GWP"](lca, ppl):.2} {unit}.\n')


def save_all_reports():
    path = '/Users/torimorgan/opt/anaconda3/lib/python3.8/site-packages/exposan/Duke_Reclaimer'
    for i in (sysA,lcaA, sysB,lcaB, sysC,lcaC, sysD,lcaC):
        if isinstance(i, bst.System):
            i.simulate()
            i.save_report(f'{path}/{i.ID}.xlsx')
        else:
            i.save_report(f'{path}/{i.system.ID}_lca.xlsx')

__all__ = ('sysA', 'sysB', 'sysC', 'sysD', 
           'teaA', 'teaB', 'teaC', 'teaD', 
           'lcaA', 'lcaB', 'lcaC', 'lcaD',
           'print_summaries', 'save_all_reports',
            *(i.ID for i in sysA.units),
            *(i.ID for i in sysB.units),
            *(i.ID for i in sysC.units),
            *(i.ID for i in sysD.units)
            )