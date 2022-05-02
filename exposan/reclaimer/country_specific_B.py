#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 12:17:55 2022

@author: torimorgan
"""


import models as m
import pandas as pd
from systems import price_dct
from chaospy import distributions as shape
import biosteam as bst
from biosteam.evaluation import Model
from exposan import reclaimer as DR
from qsdsan.utils import (
    load_data, data_path,
    AttrSetter, AttrFuncSetter, DictAttrSetter,
    FuncGetter,
    time_printer
    )
from qsdsan import currency, ImpactItem

systems = DR.systems
sys_dct = systems.sys_dct
price_dct = systems.price_dct
GWP_dct = systems.GWP_dct
GWP = systems.GWP


su_data_path = data_path + 'sanunit_data/'

# add energy_price as a parameter to the new_model

input_dct = {
    'China': {'energy_GWP': ('uniform', 0.745, 0.712133646, 0.848557635), 
              'energy_price': 0.084,
              'wages': ('uniform', 6.26, 4.695, 7.825), 
              'NaCl': ('uniform', 0.35, 0.2625, 0.4375), 
              'construction': 32.66,
              'e_cal': 3191,
              'p_anim':40,
              'p_veg':60.63,
              'price_ratio':0.610},
    # 'India': {'energy_GWP': ('uniform', 0.852, 0.805105241, 0.958663233), 
    #           'energy_price': 0.081,
    #           'wages': ('uniform', 3.64, 3.094, 4.186), 
    #           'NaCl': ('uniform', 0.47, 0.3525, 0.5875), 
    #           'construction': 16.85,
    #           'e_cal': 2533,
    #           'p_anim':15,
    #           'p_veg': 48.35,
    #           'price_ratio':0.300},
    # 'South Africa': {'energy_GWP': ('uniform', 0.955, 0.909088322, 1.086711278), 
    #           'energy_price': 0.14,
    #           'wages': ('uniform', 2.95, 2.2125, 3.6875), 
    #           'NaCl': ('uniform', 0.225, 0.16875, 0.28125), 
    #           'construction': 11.76,
    #           'e_cal': 2899,
    #           'p_anim':36.03,
    #           'p_veg': 48.33,
    #           'price_ratio':0.460},
    # 'Senegal': {'energy_GWP': ('uniform', 0.939, 0.850772468, 1.016179461), 
    #           'energy_price': 0.186,
    #           'wages': ('uniform', 3.64, 3.094, 4.186), 
    #           'NaCl': ('uniform', 0.05, 0.0375, 0.0625), 
    #           'construction': 16.85,
    #           'e_cal': 2545,
    #           'p_anim': 13.69,
    #           'p_veg': 48.67,
    #           'price_ratio':0.408},
    # 'Uganda': {'energy_GWP': ('uniform', 0.159, 0.1113, 0.19875), 
    #           'energy_price': 0.184,
    #           'wages': ('uniform', 1.33, 0.9975, 1.6625), 
    #           'NaCl': ('uniform', 0.284, 0.213, 0.355), 
    #           'construction': 6.12,
    #           'e_cal': 1981,
    #           'p_anim': 12.25,
    #           'p_veg': 34.69,
    #           'price_ratio':0.348},
    # 'Worst': {'energy_GWP': ('uniform', 1.046968, 0.785, 1.3087),
    #           'energy_price': 0.378,
    #           'wages': ('uniform', 40.11565476, 30.087, 50.143),
    #           'NaCl': ('uniform', 0.47, 0.3525, 0.5875),
    #           'construction': 40.7322619,
    #           'e_cal': 3885,
    #           'p_anim': 104.98,
    #           'p_veg': 73.29,
    #           'price_ratio':1.370785956},
    # 'Median': {'energy_GWP': ('uniform', 0.686, 0.5145, 0.8575), 
    #           'energy_price': 0.129,
    #           'wages': ('uniform', 3.70, 2.775, 4.625), 
    #           'NaCl': ('uniform', 0.284, 0.213, 0.355), 
    #           'construction': 3.64,
    #           'e_cal': 2864,
    #           'p_anim': 36.04,
    #           'p_veg': 43.75,
    #           'price_ratio':0.479},
    # 'Best': {'energy_GWP': ('uniform', 0.009, 0.012, 0.015),
    #           'energy_price': 0,
    #           'wages': ('uniform',  0.0375, 0.05, 0.0625),
    #           'NaCl': ('uniform',  0.0375, 0.050, 0.0625),
    #           'construction': 0.14,
    #           'e_cal': 1786,
    #           'p_anim': 6.55,
    #           'p_veg': 24.81,
    #           'price_ratio': 0.174},
    }

b = price_dct['Electricity']

def run_country(dct):
    results = {}
    

    
    # all_paramsA = modelB.get_parameters()

    
    for country, country_dct in dct.items():
        sysB = systems.sysB
        sysB.simulate()
        streams = sys_dct['stream_dct'][sysB.ID]
        # operator
        # sysB._TEA.annual_labor = country_dct['operator']* 3*365
        
        modelB = Model(sysB, m.add_metrics(sysB))
        # paramA = modelB.parameter

        
        # Shared parameters
        modelB = m.add_shared_parameters(sysB, modelB, country_specific=True)
        param = modelB.parameter
        
        
        #price ratio
        i = country_dct['price_ratio']
        # i=1
        # If stream items put it back in
        # price_dct = systems.price_dct
        # old_price_ratio = systems.price_ratio
        # for stream in ('LPG'):
        #     # new_price = price_dct[stream] = price_dct[stream] * i/old_price_ratio 
        #     # streams[stream].price = new_price
        #     old_price = price_dct[stream]
        #     new_price = old_price * i/old_price_ratio
        #     # if stream=='GAC': print(f'\n old price is {old_price}, new price is {new_price}')
        #     # streams[stream].price = new_price
        systems.price_ratio = i
        for u in sysB.units:
            if hasattr(u, 'price_ratio'):
                u.price_ratio = i
        
        # wages
        kind, low_val, peak_val, max_val = country_dct['wages']
        b=peak_val
        if kind == 'triangle':
            D = shape.Triangle(lower=low_val, midpoint=peak_val, upper=max_val)
        else:
            D = shape.Uniform(lower=low_val,upper=max_val)
        @param(name='Labor wages', element=systems.B1, kind='coupled', units='USD/h',
               baseline=b, distribution=D)
        def set_labor_wages(i):
            labor_cost = 0
            for u in sysB.units:
                if hasattr(u, '_calc_maintenance_labor_cost'):
                    u.wages = i
                    labor_cost += u._calc_maintenance_labor_cost()
            sysB.TEA.annual_labor = labor_cost
        
        #energy_GWP
        kind, low_val, peak_val, max_val = country_dct['energy_GWP']
        b=peak_val
        if kind == 'triangle':
            D = shape.Triangle(lower=low_val, midpoint=peak_val, upper=max_val)
        else:
            D = shape.Uniform(lower=low_val,upper=max_val)
        # @param(name='Electricity CF', element='LCA', kind='isolated',
        #         units='kg CO2-eq/kWh', baseline=b, distribution=D)            
        @param(name='Electricity CF', element=systems.B1, kind='coupled',
                units='kg CO2-eq/kWh', baseline=b, distribution=D)
        def set_electricity_CF(i):
            GWP_dct['Electricity'] = ImpactItem.get_item('e_item').CFs['GlobalWarming'] = i
            GWP_dct['Electricity'] = systems.e_item.CFs['GlobalWarming'] = i
            
        # energy_price
        bst.PowerUtility.price = country_dct['energy_price']
        
                # Diet and excretion
        B1 = systems.B1
        # p_anim
        B1.p_anim = country_dct['p_anim']
        
        # p_veg
        B1.p_veg = country_dct['p_veg']
        
        # e_cal
        B1.e_cal = country_dct['e_cal']
        
        path = su_data_path + '_excretion.tsv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B1, exclude=('e_cal','p_anim','p_veg'))

        # #NaCl
        # kind, low_val, peak_val, max_val = country_dct['NaCl']
        # b=peak_val
        # if kind == 'triangle':
        #     D = shape.Triangle(lower=low_val, midpoint=peak_val, upper=max_val)
        # else:
        #     D = shape.Uniform(lower=low_val,upper=max_val)
        # @param(name='NaCl price', element='TEA', kind='isolated', units='USD/kg',
        #         baseline=b, distribution=D)
        # def set_NaCl_price(i):
        #     price_dct['NaCl'] = streams['NaCl'].price = i

        # kind, low_val, peak_val, max_val = country_dct['NaCl']
        # b=peak_val
        # if kind == 'triangle':
        #     D = shape.Triangle(lower=low_val, midpoint=peak_val, upper=max_val)
        # else:
        #     D = shape.Uniform(lower=low_val,upper=max_val)
        # @param(name='NaCl1 price', element='TEA', kind='isolated', units='USD/kg',
        #         baseline=b, distribution=D)
        # def set_NaCl1_price(i):
        #     price_dct['NaCl1'] = streams['NaCl1'].price = i       
            ########## Related to human input ##########

        
        #MURT Toilet
        B2 = systems.B2
        path = su_data_path + '_murt_toilet.tsv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B2, exclude=('MCF_decay', 'N2O_EF_decay', 'OPEX_over_CAPEX'))

        b = B2.MCF_decay
        D = shape.Triangle(lower=0.05, midpoint=b, upper=0.15)
        @param(name='MCF_decay', element=B2, kind='coupled',
               units='fraction of anaerobic conversion of degraded COD',
               baseline=b, distribution=D)
        def set_MCF_decay(i):
            B2.toilet_MCF_decay = i
        
        b = B2.N2O_EF_decay
        D = shape.Triangle(lower=0, midpoint=b, upper=0.001)
        @param(name='N2O_EF_decay', element=B2, kind='coupled',
               units='fraction of N emitted as N2O',
               baseline=b, distribution=D)
        def set_N2O_EF_decay(i):
            B2.toilet_N2O_EF_decay = i
        
        # AnMBR
        # PrimaryReclaimer
        B3 = systems.B3
        path = su_data_path + '_primary_reclaimer.csv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B3)

        #Sludge Pasteurization
        B4 = systems.B4
        path = su_data_path + '_sludge_pasteurization.tsv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B4,  exclude=('wages'))

       
        
        # Ultrafiltration
        B5 = systems.B5
        path = su_data_path + '_ultrafiltration_reclaimer.csv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B5)
        
        # Ion exchange
        B6 = systems.B6
        path = su_data_path + '_ion_exchange_reclaimer.csv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B6, exclude=('wages'))
        
        # ECR
        B7 = systems.B7
        path = su_data_path + '_ECR_reclaimer.csv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B7)
        
        #Housing
        B10 = systems.B10
        path = su_data_path + '_housing_reclaimer.csv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B10)

        #Mischelaneous
        B11 = systems.B11
        path = su_data_path + '_system_reclaimer.csv'
        data = load_data(path)
        m.batch_setting_unit_params(data, modelB, B11)
                
        modelB.parameters = [i for i in modelB.parameters if i.name!='Wages']                    
        results[country] = m.run_uncertainty(model=modelB, N=1000)

        
    return results





#need results folder in the file where this is located
def save_uncertainty_results(results):
    import os
    #path = os.path.dirname(os.path.realpath(__file__))
    path = ('/Users/torimorgan/Documents/GitHub/EXPOsan/exposan/reclaimer/')
    path += '/results'
    
    # path += '/results'
    if not os.path.isdir(path):
         os.mkdir(path)
    del os


    for country, dct in results.items():
        file_name = path+'/'+country+'BF.xlsx'
        if dct['parameters'] is None:
            raise ValueError('No cached result, run model first.')
        with pd.ExcelWriter(file_name) as writer:
            dct['parameters'].to_excel(writer, sheet_name='Parameters')
            dct['data'].to_excel(writer, sheet_name='Uncertainty results')
            if 'percentiles' in dct.keys():
                dct['percentiles'].to_excel(writer, sheet_name='Percentiles')
            dct['spearman'].to_excel(writer, sheet_name='Spearman')
            # model.table.to_excel(writer, sheet_name='Raw data')



results = run_country(dct=input_dct)
save_uncertainty_results(results)