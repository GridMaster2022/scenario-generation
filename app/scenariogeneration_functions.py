import pandas as pd
import random
import string
import json

from esdl.resources.xmlresource import XMLResource
from datetime import datetime
from pathlib import Path
import uuid
import esdl
from pyecore.resources import ResourceSet, URI
import uuid
import copy
import random
import os
import shutil
import uuid
import glob
import numpy as np

from ema_workbench import Model, RealParameter, CategoricalParameter, em_framework, perform_experiments

furnace_table = pd.read_excel(r'data/furnacepathways_table.xlsx')
furnace_table = furnace_table.set_index('Furnace technology scenario')
furnace_table_new = pd.read_excel(r'data/furnacepathways_table copy.xlsx')
furnace_table_new = furnace_table_new.set_index('Furnace technology scenario')
boiler_table = pd.read_excel(r'data/boilerpathways_table.xlsx')
boiler_table = boiler_table.set_index('Boiler technology scenario')
factor_table = pd.read_excel(r"data/factor_table.xlsx")
factor_table = factor_table.set_index('Value')
area_table = pd.read_excel(r'data/area_table.xlsx')


def adjust_scenariosspace(external_factor, dom_factor, other_options, percentage, scenario_space):
    length = len(scenario_space[external_factor])
    number_hvision = round((percentage / 100) * length)
    number_other = length - number_hvision

    replace_list = [dom_factor] * number_hvision

    while len(replace_list) < length:
        replace_list.append(random.choice(other_options))

    random.shuffle(replace_list)

    scenario_space[external_factor] = replace_list


def add_furbopaths(scenario_space):
    furnacepath_dict = {}

    for p in furnace_table_new['Scenario class'].unique():
        furnacepath_dict[p] = []

    for i, row in furnace_table_new.iterrows():
        furnacepath_dict[row['Scenario class']].append(i)

    boiler_powergen_dict = {
        1: ["Fossil"],
        2: ["H2"],
        3: ["H2", "GG", "Fossil"],
        4: ["H2"],
        5: ["GG"]
    }

    boiler_cogen_dict = {
        3: ["E-boiler", "H2-cogen", "GG-cogen", "H2-hybrid-boiler"],
        4: ["H2-boier", "H2-cogen", "GG-cogen"],  
        5: ["GG-boiler", "GG-cogen"],
        1: ["Fossil"],
        2: ["H2-cogen", "H2-hybrid-boiler"]  
    }

    scenario_space['boiler_path'] = None
    scenario_space['powergen_path'] = None
    scenario_space['cogen_path'] = None

    for i in range(scenario_space.shape[0]):

        dom_tech = scenario_space.loc[i]['x16']

        if dom_tech == "a":
            scenario_space.at[i, 'boiler_path'] = 25
        if dom_tech == "b":
            scenario_space.at[i, 'boiler_path'] = 5
        if dom_tech == "c":
            scenario_space.at[i, 'boiler_path'] = 78
        if dom_tech == "d":
            scenario_space.at[i, 'boiler_path'] = 31
        if dom_tech == "e":
            scenario_space.at[i, 'boiler_path'] = 7
        if dom_tech == "f":
            scenario_space.at[i, 'boiler_path'] = 82
        if dom_tech == "g":
            scenario_space.at[i, 'boiler_path'] = 37
        if dom_tech == "h":
            scenario_space.at[i, 'boiler_path'] = 63

        first_tech = None
        first_year = None

        for y in range(2025, 2055, 5):

            value = furnace_table_new.iloc[scenario_space.loc[i]['boiler_path'] - 1].loc[y]

            if type(value) == str and first_tech == None:
                first_tech = int(value[-1])
                powergen_tech = random.choice(boiler_powergen_dict[first_tech])
                cogen_tech = random.choice(boiler_cogen_dict[first_tech])
                first_year = y
                scenario_space.at[i, 'powergen_path'] = (first_year, powergen_tech)
                scenario_space.at[i, 'cogen_path'] = (first_year, cogen_tech)


def create_scenariospace_LHS(number):
    def function(x1=None, x2=None, x3=None, x4=None, x5=None, x6=None, x7=None, x8=None, x9=None, x10=None, x11=None,
                 x12=None, x13=None, x14=None, x15=None, x16=None, x17=None, x18=None, x19=None, x20=None, x21=None,
                 x22=None, x23=None, x24=None, x25=None, x26=None, x27=None, x28=None, x29=None, x30=None, x31=None,
                 x32=None, x33=None, x34=None, x35=None, x36=None, x37=None, x38=None, x39=None, x40=None, x41=None,
                 x42=None, x43=None, x44=None, x45=None, x46=None, x47=None, x48=None, x49=None, x50=None, SOM=None):
        return

    model = Model('simplemodel', function=function)

    model.uncertainties = [
        CategoricalParameter('x1', ('a', 'b', 'c')),
        CategoricalParameter('x2', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x3', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x4', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x5', ('b', 'c', 'd', 'e')),
        CategoricalParameter('x6', ('b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x7', ('b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x8', ('b', 'c')),
        CategoricalParameter('x9', ('b', 'c', 'd', 'e')),
        CategoricalParameter('x10', ('a', 'b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x11', ('a', 'b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x12', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x13', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x14', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x15', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x16', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x17', ('a', 'b', 'c')),
        CategoricalParameter('x18', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x19', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x20', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x22', ('a', 'b')),  
        CategoricalParameter('x23', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x24', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x25', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x26', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x28', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x34', ('a', 'b')),
        CategoricalParameter('x35', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x36', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x38', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x39', ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')),
        CategoricalParameter('x40', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x41', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x42', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x43', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x44', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x45', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x46', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x47', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x48', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x49', ('a', 'b')),
        CategoricalParameter('x50', ('a', 'b', 'c')),
        CategoricalParameter('SOM', ('a', 'b', 'c', 'd'))
    ]

    results2 = perform_experiments(model, number)

    df = pd.DataFrame(np.array(results2, dtype=object)[0], dtype=object)
    df = df.drop(['scenario', 'policy', 'model'], axis=1)

    add_furbopaths(df)

    return df


def create_full_scenariospace_LHS():
    def function(x0=None, x1=None, x2a=None, x2b=None, x3=None, x4=None, x5=None, x6=None, x7=None, x8=None, x9=None,
                 x10=None, x11=None, x12=None, x13=None, x14=None, x15=None, x16=None, x16a=None, x17=None, x18=None,
                 x19=None, x20=None, x21=None, x22=None, x23=None, x24=None, x25=None, x26=None, x27=None, x28=None,
                 x29=None, x30=None, x31=None, x32=None, x33=None, x34=None, x35=None, x36=None, x37=None, x38=None,
                 x39=None, x40=None, x41=None, x42=None, x43=None, x44=None, x45=None, x46=None, x47=None, x48=None,
                 x49=None, x50=None, SOM=None):
        return

    model = Model('simplemodel', function=function)

    model.uncertainties = [
        CategoricalParameter('x0', ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')),
        CategoricalParameter('x2a', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x3', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x4', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x5', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x6', ('a', 'b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x7', ('a', 'b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x8', ('a', 'b', 'c')),
        CategoricalParameter('x9', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x10', ('a', 'b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x11', ('a', 'b', 'c', 'd', 'e', 'f', 'g')),
        CategoricalParameter('x12', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x13', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x14', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x15', ('a', 'b', 'c', 'd', 'e')),
        CategoricalParameter('x16a', ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')),
        CategoricalParameter('x17', ('a', 'b', 'c')),
        CategoricalParameter('x18', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x19', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x20', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x22', ('a', 'b')),  
        CategoricalParameter('x23', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x24', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x25', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x26', ('a', 'b', 'c', 'd')),
        CategoricalParameter('x28', ('a', 'b', 'c', 'd', 'e', 'f')),
        CategoricalParameter('x34', ('a', 'b')),
        CategoricalParameter('x49', ('a', 'b')),
        CategoricalParameter('x50', ('a', 'b', 'c')),
    ]

    results2 = perform_experiments(model, 101)

    df = pd.DataFrame(np.array(results2, dtype=object)[0], dtype=object)
    df = df.drop(['scenario', 'policy', 'model'], axis=1)

    manual_scenarios = pd.read_excel(r'data/manual_scenarios.xlsx').set_index("Unnamed: 0")
    table_factor0 = pd.read_excel(r'data/scenario_factor0.xlsx').set_index('factor 0')
    table_factor16a = pd.read_excel(r'data/scenario_factor16a.xlsx').set_index('factor')

    keys = list(range(101, 110))
    values = ["Siemens 4", "Gasunie 4", "Siemens 1", "Gasunie 2", "Siemens 3", "Siemens 5", "Siemens 2", "Gasunie 3",
              "Gasunie 1"]
    name_dict = dict(zip(keys, values))

    manual_scenarios = manual_scenarios.transpose()

    index_dict = {}
    for c in manual_scenarios.columns:
        index_dict[c] = "x" + str(c)

    manual_scenarios = manual_scenarios.rename(columns=index_dict)
    df = df.append(manual_scenarios, ignore_index=True)

    for i, x in df.iterrows():
        for y in [1, 35, 36, 39, 40, 45]:
            string = 'x' + str(y)
            df.at[i, string] = table_factor0[x['x0']][y]

        if table_factor0[x['x0']]['2b'] == '2a':
            df.at[i, 'x2b'] = x['x2a']
        else:
            df.at[i, 'x2b'] = table_factor0[x['x0']]['2b']

        for z in [16, 46, 47, 48]:
            string = 'x' + str(z)
            df.at[i, string] = table_factor16a[x['x16a']][z]

    df = df.sort_index(axis=1)

    for i, x in df.iterrows():
        if i < 101:
            df.at[i, 'name'] = 'LHS {}'.format(i + 1)
        else:
            df.at[i, 'name'] = name_dict[i]

        df.at[i, "uuid"] = str(uuid.uuid4())

    add_furbopaths(df)

    for c in ['uuid', 'name']:
        col = df.pop(c)
        df.insert(0, col.name, col)

    return df
