import pandas as pd
from esdl import esdl_handler
from pathlib import Path
import esdl
from pyecore.resources import ResourceSet, URI
import random
import uuid
import logging

from esdl import SingleValue, QuantityAndUnitType, PhysicalQuantityEnum, UnitEnum, MultiplierEnum

logging.getLogger('esdl').setLevel(logging.ERROR)

##############
# Input data #
##############

furnace_table = pd.read_excel(r'data/furnacepathways_table.xlsx')
furnace_table = furnace_table.set_index('Furnace technology scenario')
furnace_table_new = pd.read_excel(r'data/furnacepathways_table copy.xlsx')
furnace_table_new = furnace_table_new.set_index('Furnace technology scenario')
boiler_table = pd.read_excel(r'data/boilerpathways_table.xlsx')
boiler_table = boiler_table.set_index('Boiler technology scenario')
factor_table = pd.read_excel(r"data/factor_table.xlsx")
factor_table = factor_table.set_index('Value')
prices_default = pd.read_excel(r'data/com_prices.xlsx')
prices_default = prices_default.set_index('Unnamed: 0')
com_factors = pd.read_excel('data/com_price_factors.xlsx').set_index('Commodity prijzen')

offshore_table = pd.read_excel(r'data/offshore_table.xlsx').set_index(['index'])
onshore_wind_table = pd.read_excel(r'data/onshore_wind_table.xlsx').set_index(['index'])
onshore_pv_table = pd.read_excel(r'data/onshore_PV_table.xlsx').set_index(['index'])
free_space_MV_table = pd.read_excel(r'data/area_MV.xlsx').set_index(['index'])
shorepower_table = pd.read_excel(r'data/shorepower_table.xlsx').set_index(['index'])
h2_export_table = pd.read_excel(r'data/H2_export_table.xlsx').set_index(['index'])
area_table = pd.read_excel(r'data/area_table.xlsx')

table_dict = {
    "Synfuel1": "synfuel1_table.xlsx",
    "Synfuel2": "synfuel2_table.xlsx",
    "Synfuel3": "synfuel3_table.xlsx",
    "SynMeOHolefin1": "synmeoh1_table.xlsx",
    "SynMeOHolefin2": "synmeoh2_table.xlsx",
    "SynMeOHolefin3": "synmeoh3_table.xlsx",
    "PlasticOlefin1": "plasticolefin1_table.xlsx",
    "PlasticOlefin2": "plasticolefin2_table.xlsx",
    "BioGasolefin1": "biogasolefin_table.xlsx",
    "Naphta1": "naptha_table.xlsx"
}

locationorder = {}

locationorder['a'] = ["Free_MV", "BP_EurA", "BP_EurA_empty", "Gunvor_EurB", "Gunvor_EurB_empty", "Exxon_BotB",
                      "Exxon_BotB_empty", "ShellRefinery_Per", "ShellRefinery_Per_empty"]
locationorder['b'] = ["Exxon_BotB", "Exxon_BotB_empty", "Free_MV", "ShellRefinery_Per", "ShellRefinery_Per_empty",
                      "BP_EurA", "BP_EurA_empty", "Gunvor_EurB", "Gunvor_EurB_empty"]
locationorder['c'] = locationorder['a'][::-1]


#############################
# General support functions #
#############################

def load_esdl(file_name):
    rset_existing = ResourceSet()
    resource_existing = rset_existing.get_resource(URI(file_name))

    esdl_file = resource_existing.contents[0]
    esdl_description = esdl_file.instance[0]

    carriers = {}

    carriers["Electricity"] = esdl_file.energySystemInformation.carriers.carrier[0]
    carriers["RTL H-gas ODO"] = esdl_file.energySystemInformation.carriers.carrier[1]
    carriers["Green methane"] = esdl_file.energySystemInformation.carriers.carrier[2]
    carriers["RTL G-gas ODO"] = esdl_file.energySystemInformation.carriers.carrier[3]
    carriers["RTL H-gas Non Odorized"] = esdl_file.energySystemInformation.carriers.carrier[4]
    carriers["RTL G-gas Non-Odorized"] = esdl_file.energySystemInformation.carriers.carrier[5]
    carriers["Head Transport H-gas"] = esdl_file.energySystemInformation.carriers.carrier[6]
    carriers["Head Transport G-gas"] = esdl_file.energySystemInformation.carriers.carrier[7]
    carriers["Steam"] = esdl_file.energySystemInformation.carriers.carrier[8]
    carriers["High temperature heat"] = esdl_file.energySystemInformation.carriers.carrier[9]
    carriers["Low temperature heat"] = esdl_file.energySystemInformation.carriers.carrier[10]
    carriers["Grey Hydrogen"] = esdl_file.energySystemInformation.carriers.carrier[11]
    carriers["Blue Hydrogen [Hvision]"] = esdl_file.energySystemInformation.carriers.carrier[12]
    carriers["H2_new"] = esdl_file.energySystemInformation.carriers.carrier[13]
    carriers["Refgas"] = esdl_file.energySystemInformation.carriers.carrier[14]
    carriers["Petcokes"] = esdl_file.energySystemInformation.carriers.carrier[15]
    carriers["Heavy gasoil"] = esdl_file.energySystemInformation.carriers.carrier[16]
    carriers["Coal"] = esdl_file.energySystemInformation.carriers.carrier[17]
    carriers["Biomass"] = esdl_file.energySystemInformation.carriers.carrier[18]
    carriers["CO2_Pure"] = esdl_file.energySystemInformation.carriers.carrier[19]
    carriers["CO2_Biogenic"] = esdl_file.energySystemInformation.carriers.carrier[20]
    carriers["CO2_Fossil"] = esdl_file.energySystemInformation.carriers.carrier[21]
    carriers["Plastic waste"] = esdl_file.energySystemInformation.carriers.carrier[22]
    carriers["Crude oil"] = esdl_file.energySystemInformation.carriers.carrier[23]
    carriers["Methanol"] = esdl_file.energySystemInformation.carriers.carrier[24]
    carriers["Oilrest"] = esdl_file.energySystemInformation.carriers.carrier[25]
    carriers["Res fuel"] = esdl_file.energySystemInformation.carriers.carrier[26]
    carriers["Waste"] = esdl_file.energySystemInformation.carriers.carrier[27]

    sectors = {}
    sectors['Harbour Industral Complex'] = esdl_file.energySystemInformation.sectors.sector[0]
    sectors['Edible oil'] = esdl_file.energySystemInformation.sectors.sector[1]
    sectors['Chemical feedstock'] = esdl_file.energySystemInformation.sectors.sector[2]
    sectors['Non Chloride'] = esdl_file.energySystemInformation.sectors.sector[3]
    sectors['Refinery'] = esdl_file.energySystemInformation.sectors.sector[4]

    return resource_existing, esdl_description, carriers, sectors


def save_esdl(resource_existing, esdl_description, scenario_ID, scenario_year):
    """
    esdl_description = Representation of the new esdl in year ##
    scenario_id = The specific ID of the esdl file
    scenario_id = The specif year of the esdl file. Note; include .esdl at the end
    """

    destination_dir = 'scenarios/{}/{}'.format(scenario_ID, scenario_year)
    Path(destination_dir).mkdir(exist_ok=True, parents=True)

    file_name = 'base.esdl'
    src_file = destination_dir + '/' + file_name

    resource_existing.save(src_file)

    return src_file


def replace_asset_input(asset, old_carriers, new_carrier):
    """ Replaces the input of an asset. This function is meant for changing one input into another.
    Multiple old carriers can be specified in order to change different fossil inputs of different assets to one new carrier. 
    The input ratio of the behaviour remains untouched. """

    old_electricity = False
    for car in old_carriers:
        if car.name == "Electricity":
            old_electricity = True

    elec_ports = []
    if old_electricity:
        for p in asset.port:
            if p.carrier.name == "Electricity":
                elec_ports.append(p)

        for el in elec_ports:
            ratio_dict = {}
            for rel in asset.behaviour[0].mainPortRelation:
                ratio_dict[el.port] = rel.ratio

        if ratio_dict[elec_ports[0]] > ratio_dict[elec_ports[1]]:
            head_e = elec_ports[0]
        else:
            head_e = elec_ports[1]
        old_inport = head_e

    else:
        for p in asset.port:
            if p.carrier in old_carriers:
                old_inport = p

    for con in asset.containingBuilding.asset:
        # check all connections in building with same carrier as new_carrier
        if isinstance(con, (esdl.GConnection, esdl.EConnection)) and con.port[0].carrier == new_carrier:
            for p in con.port:
                if isinstance(p, esdl.OutPort):
                    # get the outport of this new connection
                    new_con_outport = p

        if isinstance(con, (esdl.GConnection, esdl.EConnection)) and con.port[0].carrier in old_carriers:
            for p in con.port:
                if isinstance(p, esdl.OutPort):
                    old_con_outport = p
                    if old_con_outport in old_inport.connectedTo:
                        old_inport.connectedTo.remove(old_con_outport)

    for i in old_carriers:
        if i in ["Petcokes", "Res fuel", "Refgas", "Oilrest"]:
            for prod in asset.containingBuilding.asset:
                if isinstance(prod, esdl.GasProducer) and prod.port[0].carrier == i:
                    for p in prod.port:
                        if isinstance(p, esdl.OutPort):
                            old_con_outport = p
                            if old_con_outport in old_inport.connectedTo:
                                old_inport.connectedTo.remove(old_con_outport)

    old_inport.connectedTo.append(new_con_outport)
    old_inport.carrier = new_carrier


def make_hybrid(asset, carriers, carr, energy_system, furbo):
    if furbo == True:
        tag = "furbo"
    else:
        tag = "other"

        for con in asset.containingBuilding.asset:
            if isinstance(con, esdl.GConnection) and con.port[0].carrier == carr:
                for p in con.port:
                    if isinstance(p, esdl.OutPort):
                        h2_con = p

    esh = esdl_handler.EnergySystemHandler()
    esh.energy_system = energy_system

    for ass in esh.energy_system.eAllContents():
        if isinstance(ass, esdl.Asset) and ass.id == asset.id:
            asset = ass

    # get fossil inport carrier
    for p in asset.port:
        if isinstance(p, esdl.InPort) and p.carrier != carriers['Electricity']:
            old_carrier = p.carrier

    # copy boiler
    new_asset = asset.deepcopy()
    asset.assetType = "fossil_hybrid_{}".format(tag)
    new_asset.id = new_asset.id + "_hybrid"
    new_asset.assetType = "additional_hybrid_{}".format(tag)

    con_steam_check = False
    con_hth_check = False

    for p in new_asset.port:
        if p.carrier == carriers['Electricity']:
            con_elec = p.connectedTo
        if p.carrier == carriers['Steam']:
            con_steam = p.connectedTo
            con_steam_check = True
        if p.carrier == carriers["High temperature heat"]:
            con_hth_check = True
            con_hth = p.connectedTo

    inport_id = "In_{}_hyb".format(new_asset.id)
    outport_id = "Out_{}_hyb".format(new_asset.id)

    if con_hth_check == True:
        if carr == carriers['Electricity']:
            new_inport = esdl.InPort(name="In_hyb", id=inport_id, carrier=carriers['Electricity'])
            for c in con_elec:
                new_inport.connectedTo.append(c)
        else:
            new_inport = esdl.InPort(name="In_hyb", id=inport_id, carrier=carr)
            new_inport.connectedTo.append(h2_con)

        new_outport = esdl.OutPort(name="Out_hyb", id=outport_id, carrier=carriers["High temperature heat"])

        for c in con_hth:
            new_outport.connectedTo.append(c)

    if con_steam_check == True:
        if carr == carriers['Electricity']:
            new_inport = esdl.InPort(name="In_hyb", id=inport_id, carrier=carriers['Electricity'])
            for c in con_elec:
                new_inport.connectedTo.append(c)

        else:
            new_inport = esdl.InPort(name="In_hyb", id=inport_id, carrier=carr)
            new_inport.connectedTo.append(h2_con)

        new_outport = esdl.OutPort(name="Out_hyb", id=outport_id, carrier=carriers["Steam"])

        for c in con_steam:
            new_outport.connectedTo.append(c)

    control_strategy = asset.controlStrategy.deepcopy()
    new_asset.controlStrategy = control_strategy

    for s in esh.energy_system.eAllContents():
        if isinstance(s, esdl.Services):
            s.service.append(control_strategy)

    control_strategy.id = control_strategy.id + "_hybrid"
    control_strategy.outPort = new_outport

    asset.controlStrategy.energyAsset = asset

    new_asset.port.clear()

    new_asset.behaviour[0].mainPort = new_inport
    new_asset.behaviour[0].id = new_asset.behaviour[0].id + "_hybrid"
    ratio = new_asset.behaviour[0].mainPortRelation[1].ratio
    new_asset.behaviour[0].mainPortRelation.clear()
    new_asset.behaviour[0].mainPortRelation.append(esdl.PortRelation(port=new_outport, ratio=ratio))

    new_asset.port.append(new_inport)
    new_asset.port.append(new_outport)
    asset.containingBuilding.asset.append(new_asset)

########################################################################
# Functions for boiler, furnace, powergen and cogen technology changes #
########################################################################

# FURNACE + BOILER = FURBO :)

def apply_furbopath1(carriers, energy_system):
    for element in energy_system.eAllContents():
        if isinstance(element, esdl.Asset) and element.assetType == "Furnace":

            stop = False

            for p in element.port:
                if (isinstance(p, esdl.InPort) and p.carrier.name in ["Petcokes", "Res Fuel", "Oilrest", "Refgas"]):
                    stop = True

            if element.id in ['C85', 'C86', 'C87', 'C88', 'C89', 'C90', 'C91', 'C92', 'C93']:
                stop = True

            if element.id in ['C28', 'C33', 'C34', 'C35', 'C39', 'C42', 'C43', 'C45', 'C47', 'C53', 'C72']:
                stop = True

            if stop == False:
                make_hybrid(element, carriers, carriers['Electricity'], energy_system, True)

        if isinstance(element, esdl.Asset) and element.assetType == "Boiler":

            stop = False

            for p in element.port:
                if isinstance(p, esdl.InPort) and p.carrier.name in ["Petcokes", "Res Fuel", "Oilrest", "Refgas"]:
                    stop = True

            if element.id in ['C85', 'C86', 'C87', 'C88', 'C89', 'C90', 'C91', 'C92', 'C93']:
                stop = True

            if element.id in ['C28', 'C33', 'C34', 'C35', 'C39', 'C42', 'C43', 'C45', 'C47', 'C53', 'C72']:
                stop = True

            if stop == False:
                make_hybrid(element, carriers, carriers['Electricity'], energy_system, True)


def apply_furbopath2(carriers, energy_system):
    for element in energy_system.eAllContents():
        if isinstance(element, esdl.Asset) and element.assetType == "fossil_hybrid_furbo":
            element.assetType = "H2_hybrid_furbo"
            replace_asset_input(element, [carriers["Refgas"], carriers["Petcokes"], carriers["RTL H-gas ODO"],
                                          carriers["Head Transport H-gas"], carriers["Res fuel"],
                                          carriers["RTL H-gas Non Odorized"]], carriers["H2_new"])


def apply_furbopathx(carriers, energy_system, furboType):
    for asset in ['Furnace', 'Boiler']:

        for element in energy_system.eAllContents():

            if isinstance(element, esdl.Asset) and element.assetType == asset:
                stop = False

                if element.id in ['C85', 'C86', 'C87', 'C88', 'C89', 'C90', 'C91', 'C92', 'C93']:
                    stop = True

                for p in element.port:
                    if isinstance(p, esdl.InPort) and p.carrier.name in ["Petcokes", "Res Fuel", "Oilrest", "Refgas"]:
                        stop = True

                if stop == False:
                    if furboType in [3, 4, 5]:
                        if furboType == 3:
                            element.assetType = "E_{}".format(asset)
                            new_carrier = carriers['Electricity']
                        if furboType == 4:
                            element.assetType = "H2_{}".format(asset)
                            new_carrier = carriers["H2_new"]
                        if furboType == 5:
                            element.assetType = "GG_{}".format(asset)
                            new_carrier = carriers['Green methane']

                        replace_asset_input(element,
                                            [carriers["Refgas"], carriers["Petcokes"], carriers["RTL H-gas ODO"],
                                             carriers["Head Transport H-gas"], carriers["Res fuel"],
                                             carriers["RTL H-gas Non Odorized"]], new_carrier)
                        if furboType == 3:
                            for r in (element.behaviour[0].mainPortRelation):
                                if r.port.id == "{}IP2".format(element.id):
                                    element.behaviour[0].mainPortRelation.remove(r)
                            element.port[1].delete()

            if isinstance(element, esdl.Asset) and element.assetType == "GG_{}".format(asset):

                if furboType in [3, 4]:
                    if furboType == 3:
                        element.assetType = "E_{}".format(asset)
                        new_carrier = carriers['Electricity']

                    if furboType == 4:
                        element.assetType = "H2_{}".format(asset)
                        new_carrier = carriers["H2_new"]

                    replace_asset_input(element, [carriers["Green methane"]], new_carrier)

                    if furboType == 3:
                        for r in (element.behaviour[0].mainPortRelation):
                            if r.port.id == "{}IP2".format(element.id):
                                element.behaviour[0].mainPortRelation.remove(r)
                        element.port[1].delete()

            if isinstance(element, esdl.Asset) and element.assetType == 'fossil_hybrid_furbo':

                if furboType == 3:
                    element.assetType = "E_{}".format(asset)
                    new_carrier = carriers['Electricity']

                if furboType == 4:
                    element.assetType = "H2_{}".format(asset)
                    new_carrier = carriers["H2_new"]

                if furboType == 5:
                    element.assetType = "GG_{}".format(asset)
                    new_carrier = carriers['Green methane']

                if furboType == 5 and element.assetType == "additional_hybrid_furbo":
                    break

                replace_asset_input(element, [carriers["Refgas"], carriers["Petcokes"], carriers["RTL H-gas ODO"],
                                              carriers["Head Transport H-gas"], carriers["Res fuel"],
                                              carriers["RTL H-gas Non Odorized"]], new_carrier)

                for int in element.containingBuilding.asset:
                    if isinstance(int, esdl.Asset) and int.assetType == "additional_hybrid_furbo":
                        int.delete()

                if furboType == 3:
                    for r in (element.behaviour[0].mainPortRelation):
                        if r.port.id == "{}IP2".format(element.id):
                            element.behaviour[0].mainPortRelation.remove(r)

                    element.port[1].delete()

            if isinstance(element, esdl.Asset) and element.assetType == 'H2_hybrid_furbo':

                if furboType == 3:
                    element.assetType = "E_asset"
                    new_carrier = carriers['Electricity']
                    replace_asset_input(element, [carriers['H2_new']], carriers['Electricity'])

                if furboType == 4:
                    element.assetType = "H2_asset"
                    new_carrier = carriers["H2_new"]
                    break

                for int in element.containingBuilding.asset:
                    if isinstance(int, esdl.Asset) and int.assetType == "additional_hybrid_furbo":
                        int.delete()

                if furboType == 3:
                    for r in (element.behaviour[0].mainPortRelation):
                        if r.port.id == "{}IP2".format(element.id):
                            element.behaviour[0].mainPortRelation.remove(r)
                    element.port[1].delete()

            if isinstance(element, esdl.Asset) and element.assetType == "GG_asset" and furboType in [3, 4]:

                if furboType == 3:
                    element.assetType = "E_asset"
                    new_carrier = carriers['Electricity']
                if furboType == 4:
                    element.assetType = "H2_asset"
                    new_carrier = carriers["H2_new"]

                replace_asset_input(element, [carriers['Green methane']], new_carrier)

                if furboType == 3:
                    for r in (element.behaviour[0].mainPortRelation):
                        if r.port.id == "{}IP2".format(element.id):
                            element.behaviour[0].mainPortRelation.remove(r)
                    element.port[1].delete()


def apply_furbomiek(carriers, energy_system, furboType):
    for asset in ['Furnace', 'Boiler']:

        for element in energy_system.eAllContents():

            if isinstance(element, esdl.Asset) and element.assetType == asset:
                stop = False

                if element.id in ['C85', 'C86', 'C87', 'C88', 'C89', 'C90', 'C91', 'C92', 'C93']:
                    stop = True

                if element.id not in ['C28', 'C33', 'C34', 'C35', 'C39', 'C42', 'C43', 'C45', 'C47', 'C53', 'C72']:
                    stop = True

                for p in element.port:
                    if isinstance(p, esdl.InPort) and p.carrier.name in ["Petcokes", "Res Fuel", "Oilrest", "Refgas"]:
                        stop = True

                if stop == False:
                    if furboType in [3, 4, 5]:
                        if furboType == 3:
                            element.assetType = "E_{}".format(asset)
                            new_carrier = carriers['Electricity']
                        if furboType == 4:
                            element.assetType = "H2_{}".format(asset)
                            new_carrier = carriers["H2_new"]
                        if furboType == 5:
                            element.assetType = "GG_{}".format(asset)
                            new_carrier = carriers['Green methane']

                        replace_asset_input(element,
                                            [carriers["Refgas"], carriers["Petcokes"], carriers["RTL H-gas ODO"],
                                             carriers["Head Transport H-gas"], carriers["Res fuel"],
                                             carriers["RTL H-gas Non Odorized"]], new_carrier)
                        if furboType == 3:
                            for r in (element.behaviour[0].mainPortRelation):
                                if r.port.id == "{}IP2".format(element.id):
                                    element.behaviour[0].mainPortRelation.remove(r)
                            element.port[1].delete()


def apply_furbopaths(external_factor, scenario_number, year, carriers, energy_system):
    if external_factor == 5 and year == 2030:
        apply_furbomiek(carriers, energy_system, 3)

    if furnace_table_new.iloc[external_factor - 1].loc[year] == "Boiler1":
        logging.debug("SCENARIO {}: a hybrid fossil / E - switch is happening in year {}".format(scenario_number, year))
        apply_furbopath1(carriers, energy_system)
        return "E"
    if furnace_table_new.iloc[external_factor - 1].loc[year] == "Boiler2":
        logging.debug("SCENARIO {}: a hybrid fossil / H2 - switch is happening in year {}".format(scenario_number, year))
        apply_furbopath2(carriers, energy_system)
        return "H2_new"
    if furnace_table_new.iloc[external_factor - 1].loc[year] == "Boiler3":
        logging.debug("SCENARIO {}: a E - switch is happening in year {}".format(scenario_number, year))
        apply_furbopathx(carriers, energy_system, 3)
        return "E"
    if furnace_table_new.iloc[external_factor - 1].loc[year] == "Boiler4":
        logging.debug("SCENARIO {}: a H2 - switch is happening in year {}".format(scenario_number, year))
        apply_furbopathx(carriers, energy_system, 4)
        return "H2_new"
    if furnace_table_new.iloc[external_factor - 1].loc[year] == "Boiler5":
        logging.debug("SCENARIO {}: a GG - switch is happening in year {}".format(scenario_number, year))
        apply_furbopathx(carriers, energy_system, 5)
        return "GM"


# POWERGEN
def powergen_switch(powergen, new_carrier, carriers):
    for p in powergen.port:
        if isinstance(p, esdl.InPort):
            if p.carrier == carriers['Head Transport H-gas']:
                replace_asset_input(powergen, [carriers['Head Transport H-gas']], new_carrier)
                powergen.assetType = powergen.assetType + '_' + new_carrier.id


def apply_powergenpaths(external_factor, scenario_number, year, carriers, energy_system):
    if external_factor == (year, "H2"):
        for powergen in energy_system.eAllContents():
            if isinstance(powergen, esdl.PowerPlant) and powergen.assetType in ["Powergen_baseload",
                                                                                "Powergen_flexible",
                                                                                "Powergen_baseloadind"]:
                powergen_switch(powergen, carriers['H2_new'], carriers)

    if external_factor == (year, "GG"):
        for powergen in energy_system.eAllContents():
            if isinstance(powergen, esdl.PowerPlant) and powergen.assetType in ["Powergen_baseload",
                                                                                "Powergen_flexible",
                                                                                "Powergen_baseloadind"]:
                powergen_switch(powergen, carriers['Green methane'], carriers)


# COGEN

def cogen_boiler_switch(cogen, new_carrier, carriers):
    cogen.assetType = cogen.assetType + '_boiler_' + new_carrier.name
    for port in cogen.port:
        if port.carrier.name == 'Electricity' and isinstance(port, esdl.OutPort):
            port.delete()

    replace_asset_input(cogen, [carriers['RTL H-gas ODO'], carriers['RTL H-gas Non Odorized'],
                                carriers['Head Transport H-gas'], carriers['Refgas'], carriers['Petcokes']],
                        new_carrier)


def cogen_hybrid_boiler_switch(cogen, carriers, energy_system):
    cogen.assetType = cogen.assetType + '_hybridboiler'
    for port in cogen.port:
        if port.carrier.name == 'Electricity' and isinstance(port, esdl.OutPort):
            port.delete()

    make_hybrid(cogen, carriers, carriers['H2_new'], energy_system, False)


def cogen_switch(cogen, new_carrier, carriers):
    cogen.assetType = cogen.assetType + new_carrier.name
    replace_asset_input(cogen, [carriers['RTL H-gas ODO'], carriers['RTL H-gas Non Odorized'],
                                carriers['Head Transport H-gas'], carriers['Refgas'], carriers['Petcokes']],
                        new_carrier)


def apply_cogenpaths(external_factor, scenario_number, year, carriers, energy_system):
    if external_factor == (year, "E-boiler"):
        logging.debug("COGENS SWITCHED TO {}".format(external_factor[1]))
        for cogen in energy_system.eAllContents():
            if isinstance(cogen, esdl.CHP):
                cogen_boiler_switch(cogen, carriers['Electricity'], carriers)
    if external_factor == (year, "H2-boiler"):
        logging.debug("COGENS SWITCHED TO {}".format(external_factor[1]))
        for cogen in energy_system.eAllContents():
            if isinstance(cogen, esdl.CHP):
                cogen_boiler_switch(cogen, carriers['H2_new'], carriers)
    if external_factor == (year, "H2-hybrid-boiler"):
        logging.debug("COGENS SWITCHED TO {}".format(external_factor[1]))
        for cogen in energy_system.eAllContents():
            if isinstance(cogen, esdl.CHP):
                cogen_hybrid_boiler_switch(cogen, carriers, energy_system)
    if external_factor == (year, "H2-cogen"):
        logging.debug("COGENS SWITCHED TO {}".format(external_factor[1]))
        for cogen in energy_system.eAllContents():
            if isinstance(cogen, esdl.CHP):
                cogen_switch(cogen, carriers['H2_new'], carriers)
    if external_factor == (year, "GG-cogen"):
        logging.debug("COGENS SWITCHED TO {}".format(external_factor[1]))
        for cogen in energy_system.eAllContents():
            if isinstance(cogen, esdl.CHP):
                cogen_switch(cogen, carriers['Green methane'], carriers)


##########################################
# Wind, PV, shorepower mapping functions #
##########################################

def apply_offshorewindgrowth(external_factor, year, energy_system):
    for asset in energy_system.eAllContents():
        if isinstance(asset, esdl.WindTurbine) and asset.name == "Offshore_MV":
            new_value = float(offshore_table.loc[external_factor][year]) * 1000000
            asset.power = new_value
            for p in asset.port:
                if isinstance(p, esdl.OutPort):
                    p.profile[0].multiplier = new_value


def apply_onshorewindgrowth(external_factor, year, energy_system):
    new_value = float(onshore_wind_table.loc[external_factor][year]) * 1000000

    asset_list = []

    for asset in energy_system.eAllContents():
        if isinstance(asset, esdl.Building) and 'OnshoreWind' in asset.name:
            for ep in asset.asset:
                if isinstance(ep, esdl.WindTurbine):
                    asset_list.append(ep)

    new_value_new = (new_value - 100000000) / len(asset_list)

    for ep in asset_list:
        if ep.name == "EnecoWind_MV":

            new_value = 100000000.0

            ep.power = new_value
            for p in ep.port:
                if isinstance(p, esdl.OutPort):
                    p.profile[0].multiplier = new_value
        else:
            ep.power = new_value_new

            for p in ep.port:
                if isinstance(p, esdl.OutPort):
                    p.profile[0].multiplier = new_value_new


def apply_onshoresolargrowth(external_factor, year, energy_system):
    new_value = float(onshore_pv_table.loc[external_factor][year])

    asset_list = []

    for asset in energy_system.eAllContents():
        if isinstance(asset, esdl.Building) and 'OnshoreSolar' in asset.name:
            for ep in asset.asset:
                if isinstance(ep, esdl.ElectricityProducer):
                    asset_list.append(ep)

    new_value = new_value / len(asset_list)
    new_value = new_value * 1000000

    for ep in asset_list:
        ep.power = new_value
        for p in ep.port:
            if isinstance(p, esdl.OutPort):
                p.profile[0].multiplier = new_value


def apply_shorepowergrowth(external_factor, year, energy_system):
    shorepower_locations = ["D81_E", "D82_E", "D83_E", "D84_E", "D85_E", "D86_E", "D87_E", "D88_E", "D89_E", "D90_E"]

    for asset in energy_system.eAllContents():

        if isinstance(asset, esdl.ElectricityDemand) and asset.id in shorepower_locations:
            new_value = (float(shorepower_table.loc[external_factor][year]) / len(shorepower_locations)) * 1000000
            asset.power = new_value

            for p in asset.port:
                if isinstance(p, esdl.InPort):
                    p.profile[0].multiplier = new_value


############################################
# Closing and capacity reduction functions #
############################################

def close_area(areas, energy_system):
    """
    Input the list of area owners which should be closed/deleted
    """
    for area_name in areas:
        for element in energy_system.eAllContents():
            if isinstance(element, esdl.Building) and element.name == area_name:
                connections = [asset for asset in element.asset if
                               isinstance(asset, (esdl.EConnection, esdl.GConnection))]
                element.asset.clear()
                element.asset.extend(connections)

                id = element.name
                name = element.name
                location = element.geometry

                area = element.area

                new_value = float(area_table['buildingDensity'][area_table['Name'] == area_name])
                new_value = new_value * 5
                area.buildingDensity = new_value
                logging.debug(area_name, "closed")


def close_others_init(year, energy_system):
    other_sites = ['Lyondell_MVB', 'Neste_MVB', 'Bungeloders_MVB', 'Indorama_EurA', 'Caldic_EurC', 'AlcoEnergy_EurC',
                   'AVR_BotA', 'Cabot_BotA', 'EKC_BotA', 'Invista_BotA', 'ENCI_Eur', 'Climax_BotA', 'Ducor_BotA',
                   'Nouryon_BotA', 'Wilmar_Per', 'Arkema_Per', 'Cerexagri_Per']

    if year == 2025:
        ten_list = []
        twenty1_list = []
        fifty_list = []
        twenty_list = []

        for i in range(2):
            choice = random.choice(other_sites)
            other_sites.remove(choice)
            ten_list.append(choice)
        for i in range(3):
            choice = random.choice(other_sites)
            other_sites.remove(choice)
            twenty1_list.append(choice)
        for i in range(8):
            choice = random.choice(other_sites)
            other_sites.remove(choice)
            fifty_list.append(choice)
        for i in range(4):
            choice = random.choice(other_sites)
            other_sites.remove(choice)
            twenty_list.append(choice)

    return ten_list, twenty_list, fifty_list, twenty1_list


def close_others2(external_factor, ten_list, twenty_list, fifty_list, twenty1_list, year, energy_system):
    median_dict = {
        'a': 2035,
        'b': 2040,
        'c': 2045,
        'd': 2050,
        'e': 0
    }

    median = median_dict[external_factor]

    if year == median - 5:
        close_area(ten_list, energy_system)
        half_capacity(twenty1_list, energy_system)
    if year == median:
        close_area(twenty1_list, energy_system)
        close_area(fifty_list, energy_system)
    if year == median + 5:
        close_area(twenty_list, energy_system)


def close_refineries(external_factor, external_factor2, external_factor3, year, energy_system):
    refinery_sites = ['Exxon_BotB', 'ShellRefinery_Per']

    if external_factor == "a":

        if external_factor3 == 'a':
            if year == 2035:
                close_area(refinery_sites, energy_system)
        if external_factor3 == 'b':
            if year == 2040:
                close_area(refinery_sites, energy_system)
            if year == 2035:
                half_capacity(refinery_sites, energy_system)
        if external_factor3 == 'c':
            if year == 2040:
                close_area(refinery_sites, energy_system)
        if external_factor3 == 'd':
            if year == 2040:
                half_capacity(refinery_sites, energy_system)
            if year == 2045:
                close_area(refinery_sites, energy_system)

    else:

        if external_factor2 == 'a':
            if year == 2035:
                half_capacity(refinery_sites, energy_system)
            if year == 2040:
                close_area(refinery_sites, energy_system)
        if external_factor2 == 'b':
            if year == 2040:
                close_area(refinery_sites, energy_system)
        if external_factor2 == 'c':
            if year == 2040:
                half_capacity(refinery_sites, energy_system)
            if year == 2045:
                close_area(refinery_sites, energy_system)
        if external_factor2 == 'd':
            if year == 2045:
                close_area(refinery_sites, energy_system)
        if external_factor2 == 'e':
            if year == 2045:
                half_capacity(refinery_sites, energy_system)
            if year == 2050:
                close_area(refinery_sites, energy_system)
        if external_factor2 == 'f':
            if year == 2050:
                half_capacity(refinery_sites, energy_system)
        if external_factor2 == 'g':
            if year == 2050:
                close_area(refinery_sites, energy_system)


def half_capacity(sites, energy_system):
    """
    Input the list of site names which should be halfed in capacity
    """
    for site_name in sites:
        for element in energy_system.eAllContents():
            if isinstance(element, esdl.Building) and element.name == site_name:
                element.area.buildingDensity = element.area.buildingDensity * 2
                for asset in element.asset:
                    if isinstance(asset, (esdl.ElectricityDemand, esdl.GasDemand, esdl.HeatingDemand)):
                        asset.power = asset.power / 2
                        logging.debug(asset.name, asset.id, "reduced to", asset.power)


def half_capacity_plus(sites, energy_system):
    """
    Input the list of site names which should +50% in capacity
    """

    for site_name in sites:
        for element in energy_system.eAllContents():
            if isinstance(element, esdl.Building) and element.name == site_name:
                element.area.buildingDensity = element.area.buildingDensity / 1.5
                for asset in element.asset:
                    if isinstance(asset, (esdl.ElectricityDemand, esdl.GasDemand, esdl.HeatingDemand)):
                        asset.power = asset.power * 1.5
                        logging.debug(asset.name, asset.id, "increased with 50% to", asset.power)


def apply_closingpaths_new(scenario, scenario_number, year, energy_system):
    close_cluster = False

    factor_pvc = scenario['x10']
    pvc_close = False

    factor_pur = scenario['x11']
    pur_close = False
    pur_half = False

    factor_epox = scenario['x12']
    epox_half = False

    if factor_pvc == 'a' and year >= 2030:
        pvc_close = True
    if factor_pvc == 'b' and year >= 2035:
        pvc_close = True
    if factor_pvc == 'c' and year >= 2040:
        pvc_close = True
    if factor_pvc == 'd' and year >= 2045:
        pvc_close = True
    if factor_pvc == 'e' and year >= 2050:
        pvc_close = True

    if pvc_close == True:
        if factor_pur == 'a' and year >= 2035:
            pur_close = True
        if factor_pur == 'b' and year >= 2040:
            pur_close = True
        if factor_pur == 'c' and year >= 2045:
            pur_close = True
        if factor_pur == 'd' and year >= 2050:
            pur_close = True
        if factor_pur == 'a' and year >= 2030:
            pur_half = True
        if factor_pur == 'b' and year >= 2035:
            pur_half = True
        if factor_pur == 'c' and year >= 2040:
            pur_half = True
        if factor_pur == 'd' and year >= 2045:
            pur_half = True
        if factor_pur == 'e' and year >= 2050:
            pur_half = True

    if pvc_close and pur_close:
        close_cluster = True

    if pvc_close and pur_half:
        if factor_epox == 'a' and year >= 2030:
            epox_half = True
        if factor_epox == 'b' and year >= 2035:
            epox_half = True
        if factor_epox == 'c' and year >= 2040:
            epox_half = True
        if factor_epox == 'd' and year >= 2045:
            epox_half = True
        if factor_epox == 'e' and year >= 2050:
            epox_half = True

    if pvc_close and pur_half and epox_half:
        close_cluster = True

    if close_cluster == True:
        close_area(
            ['Huntsman_BotA', 'Hexion_BotA', 'AirProducts_BotA', 'AirProductsCHP_BotA', 'Shinetsu_BotA', 'Hexion_Per',
             'Tronox_BotA', 'Nouryon_BotA'], energy_system)
        ex_list = [('2a', ['Gunvor_EurB']), ('2b', ['BP_EurA']), (3, ['VPREnergy_EurC'])]
    else:
        ex_list = [('2a', ['Gunvor_EurB']), ('2b', ['BP_EurA', ]), (3, ['VPREnergy_EurC']),
                   (10, ['Huntsman_BotA', 'Hexion_BotA', 'AirProducts_BotA', 'AirProductsCHP_BotA']),
                   (11, ['Shinetsu_BotA']),
                   (12, ['Hexion_Per']), (13, ['Tronox_BotA'])]

    for ex in ex_list:

        factor = scenario['x{}'.format(ex[0])]

        if ex[0] in [2, 3]:

            if year == 2025:
                if factor == 'a':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'b':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2030:
                if factor == 'b' or factor == 'c':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'd':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2035:
                if factor == 'd':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))

        if ex[0] in [10, 11, 13]:

            if year == 2030:
                if factor == 'a':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2035:
                if factor == 'a':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'b':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2040:
                if factor == 'b':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'c':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))
                if factor == 'g':
                    half_capacity_plus(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} 50% increased capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2045:
                if factor == 'c':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'd':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2050:
                if factor == 'd':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'e':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

        if ex[0] in [12]:

            if year == 2025:
                if factor == 'a':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2030:
                if factor == 'a':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'b':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2035:
                if factor == 'b':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'c':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2040:
                if factor == 'c':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'd':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2045:
                if factor == 'd':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'e':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))

            if year == 2050:
                if factor == 'e':
                    close_area(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} closed in {}'.format(scenario_number, ex[1], year))
                if factor == 'f':
                    half_capacity(ex[1], energy_system)
                    logging.debug('SCENARIO {}: {} half capacity in {}'.format(scenario_number, ex[1], year))


####################
# H-VISION and CCS #
####################

def make_hybrid_HVision(carriers, energy_system):
    esh = esdl_handler.EnergySystemHandler()
    esh.energy_system = energy_system

    for ass in esh.energy_system.eAllContents():

        # do something to the RG GasHeater(s) of Shell and BP
        if isinstance(ass, esdl.GasHeater) and ass.id in ["C8", "C11", "C70", "C73"]:

            asset = ass

            # get the HVision connection (outport)
            for con in ass.containingBuilding.asset:
                if isinstance(con, esdl.GConnection) and con.port[0].carrier == carriers["Blue Hydrogen [Hvision]"]:
                    for p in con.port:
                        if isinstance(p, esdl.OutPort):
                            h2_con = p

            # copy furnace/boiler
            new_asset = asset.deepcopy()
            asset.assetType = "refgas_hybrid"
            new_asset.id = new_asset.id + "refgas_hybrid"
            new_asset.assetType = "blue_hydrogen_hybrid"

            con_steam_check = False
            con_hth_check = False

            # gather where new asset is connected to on different ports
            for p in new_asset.port:
                if p.carrier == carriers['Steam']:
                    con_steam = p.connectedTo
                    con_steam_check = True
                if p.carrier == carriers["High temperature heat"]:
                    con_hth_check = True
                    con_hth = p.connectedTo

            # for furnaces
            if con_hth_check == True:

                # define new ports
                new_inport = esdl.InPort(name="In_hyb", id="In_hyb_{}".format(new_asset.id),
                                         carrier=carriers["Blue Hydrogen [Hvision]"])
                new_inport.connectedTo.append(h2_con)
                new_outport = esdl.OutPort(name="Out_hyb", id="Out_hyb_{}".format(new_asset.id),
                                           carrier=carriers["High temperature heat"])

                for c in con_hth:
                    new_outport.connectedTo.append(c)

            # for boilers
            if con_steam_check == True:

                # define new ports
                new_inport = esdl.InPort(name="In_hyb", id="In_hyb_{}".format(new_asset.id),
                                         carrier=carriers["Blue Hydrogen [Hvision]"])
                new_inport.connectedTo.append(h2_con)
                new_outport = esdl.OutPort(name="Out_hyb", id="Out_hyb_{}".format(new_asset.id),
                                           carrier=carriers["Steam"])

                for c in con_steam:
                    new_outport.connectedTo.append(c)

            control_strategy = esdl.DrivenByDemand(outPort=new_outport, name="DbD_{}".format(new_asset.id),
                                                   id="DbD_{}".format(new_asset.id))
            new_asset.controlStrategy = control_strategy

            for s in esh.energy_system.eAllContents():
                if isinstance(s, esdl.Services):
                    s.service.append(control_strategy)

            asset.controlStrategy.energyAsset = asset

            new_asset.port.clear()
            new_asset.behaviour.clear()

            new_asset.port.append(new_inport)
            new_asset.port.append(new_outport)

            asset.containingBuilding.asset.append(new_asset)


def build_ATR(carriers, energy_system, HV_option):
    id = 0

    for carr in [carriers["Refgas"], carriers["RTL H-gas Non Odorized"]]:
        id = id + 1

        new_ATR = esdl.GenericConversion(
            name="HVision_ATR_{}".format(carr.id),
            power=100000000000.0,  # max power of this ATR is regulated via the refgas input
            id="HVision_ATR_{}".format(carr.id),
            efficiency=0.71
        )

        new_inport = esdl.InPort(id="ATRIP1_{}".format(id), carrier=carr)
        new_outport = esdl.OutPort(id="ATROP1_{}".format(id), carrier=carriers["Blue Hydrogen [Hvision]"])
        new_outport2 = esdl.OutPort(id="ATROP2_{}".format(id), carrier=carriers["CO2_Pure"])

        new_ATR.controlStrategy = esdl.DrivenByDemand(id=str(uuid.uuid4()),
                                                      name="DrivenByDemand for HVision_ATR_{}".format(id),
                                                      energyAsset=new_ATR, outPort=new_outport)
        new_ATR.port.append(new_inport)
        new_ATR.port.append(new_outport)
        new_ATR.port.append(new_outport2)

        new_relation = esdl.PortRelation(ratio=1 / 0.71, port=new_outport)  # hydrogen
        new_relation1 = esdl.PortRelation(ratio=2936.0, port=new_outport2)  # CO2

        new_ATR.behaviour.append(
            esdl.InputOutputRelation(id=str(uuid.uuid4()), mainPort=new_inport, name="IOR_{}".format(new_ATR.id)))
        new_ATR.behaviour[0].mainPortRelation.append(new_relation)
        new_ATR.behaviour[0].mainPortRelation.append(new_relation1)

        asset = new_ATR

        for s in energy_system.eAllContents():
            if isinstance(s, esdl.Building) and s.name == "Free_MV":
                building = s
                s.asset.append(asset)

        # Get connection on site or fossil network
        for network in building.asset:
            if isinstance(network, esdl.GConnection) and network.port[0].carrier == carr:
                for p in network.port:
                    if isinstance(p, esdl.OutPort):
                        new_inport.connectedTo.append(p)

            # Connect Hydrogen output ATR to network
            if isinstance(network, esdl.GConnection) and network.name == 'Free_MV_H2_Hvision_Network':
                for p in network.port:
                    if isinstance(p, esdl.InPort):
                        new_outport.connectedTo.append(p)

            #  Connect CO2 output to CO2 network
            if isinstance(network, esdl.GConnection) and network.name == 'Free_MV_CO2_P_Network':
                for p in network.port:
                    if isinstance(p, esdl.InPort):
                        new_outport2.connectedTo.append(p)

        for s in energy_system.eAllContents():
            if isinstance(s, esdl.Services):
                s.service.append(new_ATR.controlStrategy)

            if isinstance(s, esdl.GasProducer) and s.name == "R13_H2_Hvision_Supplier":
                s.delete()


def refgas_Hvision(carriers, energy_system, HV_option):
    new_power_0_Shell = {
        "SHELL PERGEN": {'power': 699000000.0, 'inport': "C67IP1"},
        "AL PERGEN": {'power': 699000000.0, 'inport': "C63IP1"},
        "BOILER": {'power': 92000000.0, 'inport': "C70IP1"},
        "FURNACE": {'power': 680000000.0, 'inport': "C73IP1"}
    }

    new_power_1_Shell = {
        "SHELL PERGEN": {'power': 699000000.0, 'inport': "C67IP1"},
        "AL PERGEN": {'power': 556000000.0, 'inport': "C63IP1"},
        "BOILER": {'power': 92000000.0, 'inport': "C70IP1"},
        "FURNACE": {'power': 430000000.0, 'inport': "C73IP1"},
        "ATR": {'power': 250000000.0, 'inport': "ATRIP1_1"}
    }

    new_power_2_Shell = {
        "SHELL PERGEN": {'power': 699000000.0, 'inport': "C67IP1"},
        "AL PERGEN": {'power': 413000000.0, 'inport': "C63IP1"},
        "BOILER": {'power': 92000000.0, 'inport': "C70IP1"},
        "FURNACE": {'power': 180000000.0, 'inport': "C73IP1"},
        "ATR": {'power': 786000000.0, 'inport': "ATRIP1_1"}
    }

    new_power_3_Shell = {
        "SHELL PERGEN": {'power': 699000000.0, 'inport': "C67IP1"},
        "AL PERGEN": {'power': 413000000.0, 'inport': "C63IP1"},
        "BOILER": {'power': 0.0, 'inport': "C70IP1"},
        "FURNACE": {'power': 180000000.0, 'inport': "C73IP1"},
        "ATR": {'power': 878000000.0, 'inport': "ATRIP1_1"}
    }

    new_power_0_BP = {
        "BOILER": {'power': 327000000.0, 'inport': "C11IP1"},
        "FURNACE": {'power': 566000000.0, 'inport': "C8IP1"}
    }

    new_power_1_BP = {
        "BOILER": {'power': 327000000.0, 'inport': "C11IP1"},
        "FURNACE": {'power': 316000000.0, 'inport': "C8IP1"},
        "ATR": {'power': 250000000.0, 'inport': "ATRIP1_1"}
    }

    new_power_2_BP = {
        "BOILER": {'power': 327000000.0, 'inport': "C11IP1"},
        "FURNACE": {'power': 66000000.0, 'inport': "C8IP1"},
        "ATR": {'power': 500000000.0, 'inport': "ATRIP1_1"}
    }

    new_power_3_BP = {
        "BOILER": {'power': 0.0, 'inport': "C11IP1"},
        "FURNACE": {'power': 66000000.0, 'inport': "C8IP1"},
        "ATR": {'power': 827000000.0, 'inport': "ATRIP1_1"}
    }

    if HV_option == 0:
        dict_Shell = new_power_0_Shell
        dict_BP = new_power_0_BP
    if HV_option == 1:
        dict_Shell = new_power_1_Shell
        dict_BP = new_power_1_BP
    if HV_option == 2:
        dict_Shell = new_power_2_Shell
        dict_BP = new_power_2_BP
    if HV_option == 3:
        dict_Shell = new_power_3_Shell
        dict_BP = new_power_3_BP

    for gp in energy_system.eAllContents():

        if isinstance(gp, esdl.GasProducer) and gp.name == "ShellRefinery_Per_RG_Producer":
            for i in gp.port:
                start = i.profile[0].startDate
                end = i.profile[0].endDate

            count = 0
            for i in dict_Shell.values():
                count = count + 1
                new_producer = esdl.GasProducer(name="ShellRefinery_Per_RG_Producer", id="R33_RG_{}".format(count),
                                                power=i['power'])
                new_producer.geometry = gp.geometry

                for asset in energy_system.eAllContents():
                    if isinstance(asset, (esdl.GasHeater, esdl.CHP, esdl.PowerPlant, esdl.GenericConversion)):
                        for port in asset.port:
                            if port.id == i['inport']:
                                inport = port

                new_outport = esdl.OutPort(carrier=carriers['Refgas'], name='Out', id="R33_RG{}_OP1".format(count),
                                           connectedTo=[inport])
                new_outport.profile.append(
                    esdl.InfluxDBProfile(measurement="gridmaster_profiles", multiplier=(i['power']),
                                         database="energy_profiles", name="ShellRefinery_Per_profile",
                                         field="ShellRefinery_Per_profile", host="http://influxdb",
                                         id="ShellRefinery_Per_profile_RG", startDate=start, endDate=end, port=8086))
                new_outport.profile[0].profileQuantityAndUnit = esdl.QuantityAndUnitType(physicalQuantity="POWER",
                                                                                         description="POWER in W",
                                                                                         unit="WATT",
                                                                                         id=str(uuid.uuid4()))
                new_producer.port.append(new_outport)
                gp.containingBuilding.asset.append(new_producer)

            gp.delete()
            break

        if isinstance(gp, esdl.GasProducer) and gp.name == "BP_EurA_RG_Producer":
            for i in gp.port:
                start = i.profile[0].startDate
                end = i.profile[0].endDate

            count = 0
            for i in dict_BP.values():
                count = count + 1
                new_producer = esdl.GasProducer(name="BP_EurA_RG_Producer", id="R29_RG_{}".format(count),
                                                power=i['power'])
                new_producer.geometry = gp.geometry

                for asset in energy_system.eAllContents():
                    if isinstance(asset, (esdl.GasHeater, esdl.CHP, esdl.PowerPlant, esdl.GenericConversion)):
                        for port in asset.port:
                            if port.id == i['inport']:
                                inport = port

                new_outport = esdl.OutPort(carrier=carriers['Refgas'], name='Out', id="R29_RG{}_OP1".format(count),
                                           connectedTo=[inport])
                new_outport.profile.append(
                    esdl.InfluxDBProfile(measurement="gridmaster_profiles", multiplier=(i['power']),
                                         database="energy_profiles", name="BP_EurA_profile", field="BP_EurA_profile",
                                         host="http://influxdb", id="BP_EurA_profile", startDate=start, endDate=end,
                                         port=8086))
                new_outport.profile[0].profileQuantityAndUnit = esdl.QuantityAndUnitType(physicalQuantity="POWER",
                                                                                         description="POWER in W",
                                                                                         unit="WATT",
                                                                                         id=str(uuid.uuid4()))
                new_producer.port.append(new_outport)
                gp.containingBuilding.asset.append(new_producer)

            gp.delete()


def coalplants_HVision(carriers, energy_system, HV_option):
    if HV_option == 1:
        H2_ratio = 0.1
    if HV_option in [2, 3]:
        H2_ratio = 0.2

    for cp in energy_system.eAllContents():
        if isinstance(cp, esdl.PowerPlant) and cp.name in ['Unipermpp3_MVB_Powergen_baseload',
                                                           'Engiecoal_MVB_Powergen_baseload']:
            id = cp.id

            for con in cp.containingBuilding.asset:
                if isinstance(con, esdl.GConnection) and con.port[0].carrier == carriers["Blue Hydrogen [Hvision]"]:
                    for p in con.port:
                        if isinstance(p, esdl.OutPort):
                            port_con = p
                        if isinstance(p, esdl.InPort) and cp.name == 'Engiecoal_MVB_Powergen_baseload':
                            inport_con = p

            if cp.name == 'Engiecoal_MVB_Powergen_baseload':
                for con in energy_system.eAllContents():
                    if isinstance(con, esdl.GasNetwork) and con.name == "H2_Hvision_Network":
                        for p in con.port:
                            if isinstance(p, esdl.OutPort):
                                p.connectedTo.append(inport_con)

            new_inport = esdl.InPort(id=id + "IP2", name="In2", carrier=carriers['Blue Hydrogen [Hvision]'],
                                     connectedTo=[port_con])
            cp.port.append(new_inport)
            new_relation = esdl.PortRelation(ratio=(1 / H2_ratio), port=new_inport)
            cp.behaviour[0].mainPortRelation.append(new_relation)

            for beh in cp.behaviour[0].mainPortRelation:
                if beh.port.id == id + "OP1":
                    beh.ratio = 1 / 0.46


def apply_HVision(external_factor, year, carriers, energy_system):
    HV_option = ord(external_factor) - 97

    if HV_option == 1:
        size = 4.97
    if HV_option == 2:
        size = 13.95
    if HV_option == 3:
        size = 18.25
    else:
        size = 0

    # apply CCS BASE
    apply_CCSBase_ESDL_mutation(carriers, energy_system)

    if year == 2030 and HV_option == 1:

        for a in energy_system.eAllContents():
            if isinstance(a, esdl.Area) and a.name == "Free_MV":
                if size > a.buildingDensity:
                    logging.debug("NOT ENOUGH SPACE FOR HVISION")
                else:
                    a.buildingDensity = a.buildingDensity - size
                    build_ATR(carriers, energy_system, HV_option)
                    make_hybrid_HVision(carriers, energy_system)
                    coalplants_HVision(carriers, energy_system, HV_option)
                    refgas_Hvision(carriers, energy_system, HV_option)
                    logging.debug("HVISION OPTION 1 IS BUILD")

    if year == 2035 and HV_option in [2, 3]:

        for a in energy_system.eAllContents():
            if isinstance(a, esdl.Area) and a.name == "Free_MV":
                if size > a.buildingDensity:
                    logging.debug("NOT ENOUGH SPACE FOR HVISION")
                else:
                    a.buildingDensity = a.buildingDensity - size
                    build_ATR(carriers, energy_system, HV_option)
                    make_hybrid_HVision(carriers, energy_system)
                    coalplants_HVision(carriers, energy_system, HV_option)
                    refgas_Hvision(carriers, energy_system, HV_option)
                    logging.debug("HVISION OPTION {} IS BUILD".format(str(HV_option)))


def apply_CCSBase(external_factor, year, carriers, energy_system):
    if external_factor == 'b' and year == 2030:
        apply_CCSBase_ESDL_mutation(carriers, energy_system)
        logging.debug("CCS BASE APPLIED")


def apply_CCSBase_ESDL_mutation(carriers, energy_system):
    ccs_sink = None
    for asset in energy_system.eAllContents():
        if isinstance(asset, esdl.SinkConsumer) and any(p.carrier == carriers["CO2_Pure"] for p in asset.port):
            ccs_sink = asset
            break

    for asset in energy_system.eAllContents():
        if isinstance(asset, esdl.Asset) and asset.id in ["C48", "C49", "C32", "C31", "C62", "C65", "C66", "C67",
                                                          "C68"]:
            for port in asset.port:
                if port.carrier.id == "CO2_F":
                    old_id = port.id
                    port_relation = None
                    if isinstance(asset, esdl.EnergyAsset) \
                            and asset.behaviour is not None \
                            and any(isinstance(x, esdl.InputOutputRelation) for x in asset.behaviour):
                        asset_behaviour = None
                        for behaviour in asset.behaviour:
                            if isinstance(behaviour, esdl.InputOutputRelation):
                                for relation in behaviour.mainPortRelation:
                                    if relation.port.id == port.id:
                                        port_relation = relation
                                        asset_behaviour = behaviour
                                        break
                        port.delete()
                        for con in asset.containingBuilding.asset:
                            if isinstance(con, esdl.GConnection) and con.port[0].carrier == carriers["CO2_Pure"]:
                                for con_port in con.port:
                                    if isinstance(con_port, esdl.InPort):
                                        new_port = con_port
                                    else:
                                        # con_port is the outport of GConnection. connect this to the inport of the
                                        # SinkConsumer
                                        if ccs_sink is not None:
                                            sink_in_port = None
                                            for sink_port in ccs_sink.port:
                                                if isinstance(sink_port, esdl.InPort):
                                                    sink_in_port = sink_port
                                            if sink_in_port is None:
                                                sink_in_port = esdl.InPort(id=str(uuid.uuid4()),
                                                                           name='{}IP1'.format(ccs_sink.name),
                                                                           carrier=carriers["CO2_Pure"])
                                                ccs_sink.port.append(sink_in_port)
                                            sink_in_port.connectedTo.append(con_port)
                        new_outport = esdl.OutPort(id=old_id, carrier=carriers["CO2_Pure"], connectedTo=[new_port])
                        asset.port.append(new_outport)
                        if port_relation is not None:
                            port_relation.port = new_outport
                            asset_behaviour.mainPortRelation.append(port_relation)


###########################
# Other mapping functions #
###########################

def apply_miek_elec(external_factor, year, energy_system):
    assetname = 'Electrolyzer'
    dom_tech = "E"
    buildings = {
        'UniperMPP3_MVB': (0.5, 1),
        "Free_MV_building": (2.0, 4)
    }

    for new_building in buildings:

        if external_factor == 'b' and year == 2030:

            esh = esdl_handler.EnergySystemHandler()
            esh.energy_system = energy_system
            carriers = energy_system.energySystemInformation.carriers.carrier

            for c in carriers:
                if c.id == dom_tech:
                    dom_c = c

            size = 0
            assetlist = []

            building_found = False

            for build in esh.energy_system.eAllContents():
                if isinstance(build, esdl.Building) and build.name == "Toolbox":
                    building = build
                if isinstance(build, esdl.Building) and build.name == new_building:
                    new_build = build
                    building_found = True

            if building_found == False:
                return False

            for asset in building.asset:

                if isinstance(asset, esdl.Asset) and asset.name == assetname:
                    if asset.surfaceArea > 0:
                        size = size + (buildings[new_building][1] * asset.surfaceArea)

                    new_asset = asset.deepcopy()
                    new_profile = asset.controlStrategy.profile.deepcopy()
                    code = str(uuid.uuid4())
                    new_asset.id = asset.id + '_' + code

                    if assetname == "Electrolyzer":
                        new_control_strategy = esdl.DrivenByProfile(energyAsset=new_asset, id=new_asset.id + "_CS",
                                                                    port=new_asset.port[1], profile=new_profile)
                        new_asset.controlStrategy = new_control_strategy

                        # quick fix for smaller electrolyzers
                        new_asset.controlStrategy.profile.multiplier = float(buildings[new_building][0])
                        new_asset.power = float(buildings[new_building][0])

                        for s in esh.energy_system.eAllContents():
                            if isinstance(s, esdl.Services):
                                s.service.append(new_control_strategy)

                    for port in new_asset.port:
                        port.id = port.id + '_' + code

                        if assetname == "Electrolyzer" and isinstance(port, esdl.OutPort):
                            new_asset.controlStrategy.outPort = port

                    assetlist.append(new_asset)

            if new_build.area.buildingDensity > size:

                new_build.area.buildingDensity = new_build.area.buildingDensity - size

                for a in assetlist:
                    new_build.asset.append(a)

                    for port in a.port:
                        if isinstance(port, esdl.InPort):
                            for con in new_build.asset:
                                if isinstance(con, (esdl.EConnection, esdl.GConnection)) and con.port[
                                    0].carrier == port.carrier:
                                    for p in con.port:
                                        if isinstance(p, esdl.OutPort):
                                            p.connectedTo.append(port)
                        if isinstance(port, esdl.OutPort):
                            for con in new_build.asset:
                                if isinstance(con, (esdl.EConnection, esdl.GConnection)) and con.port[
                                    0].carrier == port.carrier:
                                    for p in con.port:
                                        if isinstance(p, esdl.InPort):
                                            p.connectedTo.append(port)

                    logging.debug("added", a.name, "to", new_build.name)

                profiles = []
                for prof in energy_system.eAllContents():
                    if isinstance(prof, esdl.DrivenByProfile):
                        profiles.append(prof)

                for p in profiles:
                    asset_name = p.id.strip("_CS")

                    for a in energy_system.eAllContents():
                        if isinstance(a, esdl.Electrolyzer) and a.id == asset_name:
                            p.energyAsset = a

                energy_system = esh.energy_system


def apply_H2export(external_factor, year, energy_system):
    for asset in energy_system.eAllContents():
        if isinstance(asset, esdl.GasDemand) and asset.name == "ExportH2_new_Hinterland":
            new_value = float(h2_export_table.loc[external_factor][year]) * 1000000
            asset.power = new_value
            asset.port[0].profile[0].multiplier = new_value


def add_ETMscenario(external_factor, year):
    ETM_ID_dict = {

        "IA2025": 1472751,
        "IA2030": 1472752,
        "IA2035": 1472753,
        "IA2040": 1472754,
        "IA2045": 1472755,
        "IA2050": 1472756,
        "ND2025": 1472757,
        "ND2030": 1472758,
        "ND2035": 1472759,
        "ND2040": 1472760,
        "ND2045": 1472761,
        "ND2050": 1472762

    }

    if external_factor == "a":
        etm_scenario_id = "ND" + str(year)
    if external_factor == "b":
        etm_scenario_id = "IA" + str(year)

    return ETM_ID_dict[etm_scenario_id]


def place_nuclearplant(external_factor, year, carriers, energy_system):
    nuclear_space = 20

    place_nuclear = False

    if external_factor == 'b' and year == 2035:
        place_nuclear = True
    if external_factor == 'c' and year == 2040:
        place_nuclear = True

    if place_nuclear == True:

        for area in energy_system.eAllContents():

            if isinstance(area, esdl.Area) and area.name == 'Free_MV':

                if area.buildingDensity - nuclear_space:
                    logging.debug("NOT ENOUGH SPACE FOR THE NUCLEAR PLANT")
                    break

                else:
                    area.buildingDensity = area.buildingDensity - nuclear_space
                    nuclear_plant = esdl.ElectricityProducer(name="Nuclear Plant", id="Nuclear Plant",
                                                             power=1600000000.0)
                    area.buildingDensity = area.buildingDensity - nuclear_space
                    inport = esdl.InPort(id="In", carrier=esdl.EnergyCommodity(name='Uranium', id='Uranium'))
                    nuclear_plant.port.append(inport)
                    area.asset.append(nuclear_plant)


def apply_Ggasswitch(external_factor_24, external_factor_25, year, carriers, energy_system):
    switch_dict = {

        'a': (carriers['Green methane'], "high"),
        'b': (carriers['Green methane'], "low"),
        'c': (carriers['H2_new'], "high"),
        'd': (carriers['H2_new'], "low"),
        'e': (carriers['Electricity'], "high_alt"),
        'f': (carriers['Electricity'], "low_alt")
    }

    year_dict = {
        'a': 2040,
        'b': 2040,
        'c': 2045,
        'd': 2050
    }

    ex_24 = switch_dict[external_factor_24]
    ex_25 = year_dict[external_factor_25]

    if year == ex_25:

        for built in energy_system.eAllContents():
            if isinstance(built, esdl.GasDemand) and built.name == "BuiltEnvironment":
                built.port[0].carrier = ex_24[0]

            if isinstance(built, esdl.GasDemand) and built.name in ["PeakShaver_MV", "MixStation_Per"]:

                if not external_factor_24 in ['e', 'f']:

                    for con in energy_system.eAllContents():
                        if isinstance(con, esdl.GConnection) and con.name == "{}_{}_Network".format(built.name,
                                                                                                    ex_24[0].id):
                            for p in con.port:
                                if isinstance(p, esdl.OutPort):
                                    con_port = p

                    built.port[0].connectedTo.clear()
                    built.port[0].carrier = ex_24[0]
                    logging.debug("{}_{}_Network".format(built.name, ex_24[0].id))
                    built.port[0].connectedTo.append(con_port)

                    built.name = built.name + "_" + ex_24[1]

                else:
                    built.port[0].profile.multiplier = 0.0
                    built.power = 0.0

                    built.name = built.name + "_" + "OFF"


def apply_MV_freespace(external_factor, year, energy_system):
    for a in energy_system.eAllContents():

        if isinstance(a, esdl.Area) and a.id == "Free_MV_area":

            if year == 2025:
                a.buildingDensity = 0.0

            added_space = float(free_space_MV_table.loc[external_factor][year])
            a.buildingDensity = a.buildingDensity + added_space

            logging.debug("MAASVLAKTE II SITE GREW WITH {} AND IS NOW {} HA BIG".format(added_space, a.buildingDensity))


def add_commodityprices(external_factor, year, energy_system):
    for com in energy_system.eAllContents():
        if isinstance(com, esdl.GasCommodity) and com.id in ['GM', "H2_new", "RTLG_ODO", "RTLH_NODO", "RTLG_NODO",
                                                             "HTLH", "HTLG", "BM"]:

            com_in = com.id

            if com.id in ["RTLG_ODO", "RTLH_NODO", "RTLG_NODO", "HTLH", "HTLG"]:
                com_in = "GAS"

            price_value = float(prices_default.loc[[com_in]][year])

            factor = float(com_factors.loc[[com_in]][external_factor])
            price_value = price_value * factor

            dt_profile = SingleValue(value=price_value)

            euro_per_mw = QuantityAndUnitType(id=str(uuid.uuid4()), description='PriceInEuros',
                                              physicalQuantity=PhysicalQuantityEnum.COST,
                                              unit=UnitEnum.EURO, perMultiplier=MultiplierEnum.MEGA,
                                              perUnit=UnitEnum.WATT)

            dt_profile.profileQuantityAndUnit = euro_per_mw
            com.cost = dt_profile

        if isinstance(com, esdl.GasCommodity) and com.id in ["H2_Hvision"]:
            com_in = com.id

            price_value = 0.5

            dt_profile = SingleValue(value=price_value)

            euro_per_mw = QuantityAndUnitType(id=str(uuid.uuid4()), description='PriceInEuros',
                                              physicalQuantity=PhysicalQuantityEnum.COST,
                                              unit=UnitEnum.EURO, perMultiplier=MultiplierEnum.MEGA,
                                              perUnit=UnitEnum.WATT)

            dt_profile.profileQuantityAndUnit = euro_per_mw
            com.cost = dt_profile


def place_new_asset(assetname, new_building, dom_tech, energy_system):
    esh = esdl_handler.EnergySystemHandler()
    esh.energy_system = energy_system
    carriers = energy_system.energySystemInformation.carriers.carrier

    for c in carriers:
        if c.id == dom_tech:
            dom_c = c

    size = 0
    assetlist = []

    building_found = False

    for build in esh.energy_system.eAllContents():
        if isinstance(build, esdl.Building) and build.name == "Toolbox":
            building = build
        if isinstance(build, esdl.Building) and build.name == new_building:
            new_build = build
            building_found = True

    if building_found == False:
        return False

    for asset in building.asset:

        if isinstance(asset, esdl.Asset) and asset.name == assetname:
            if asset.surfaceArea > 0:
                size = size + asset.surfaceArea

            if isinstance(asset, esdl.GasDemand) and dom_tech == "E" and asset.name in ["SynMeOHolefin1",
                                                                                        "SynMeOHolefin2",
                                                                                        "SynMeOHolefin3"]:

                new_asset = esdl.ElectricityDemand(
                    name=asset.name,
                    power=asset.power,
                    sector=asset.sector,
                    id=asset.id + "_rep_E",
                    surfaceArea=asset.surfaceArea
                )

                new_inport = asset.port[0].deepcopy()
                new_inport.carrier = dom_c
                new_asset.port.append(new_inport)

            else:
                new_asset = asset.deepcopy()

            if isinstance(new_asset, esdl.GasDemand) and dom_tech in ["H2_new", "GM"] and new_asset.name in [
                "SynMeOHolefin1", "SynMeOHolefin2", "SynMeOHolefin3"]:
                new_asset.port[0].carrier = dom_c

            if assetname == "Electrolyzer":
                new_profile = asset.controlStrategy.profile.deepcopy()

            code = str(uuid.uuid4())
            new_asset.id = asset.id + '_' + code

            if assetname == "Electrolyzer":
                new_control_strategy = esdl.DrivenByProfile(energyAsset=new_asset, id=new_asset.id + "_CS",
                                                            port=new_asset.port[1], profile=new_profile)
                new_asset.controlStrategy = new_control_strategy

                # quick fix for smaller electrolyzers
                new_asset.controlStrategy.profile.multiplier = new_asset.controlStrategy.profile.multiplier / 2
                new_asset.power = new_asset.power / 2

                for s in esh.energy_system.eAllContents():
                    if isinstance(s, esdl.Services):
                        s.service.append(new_control_strategy)

            for port in new_asset.port:
                port.id = port.id + '_' + code

                if assetname == "Electrolyzer" and isinstance(port, esdl.OutPort):
                    new_asset.controlStrategy.outPort = port
            # logging.debug("ASSET APPENDED")
            assetlist.append(new_asset)

    if new_build.area.buildingDensity > size:

        new_build.area.buildingDensity = new_build.area.buildingDensity - size

        for a in assetlist:
            new_build.asset.append(a)

            for port in a.port:
                if isinstance(port, esdl.InPort):
                    for con in new_build.asset:
                        if isinstance(con, (esdl.EConnection, esdl.GConnection)) and con.port[
                            0].carrier == port.carrier:
                            for p in con.port:
                                if isinstance(p, esdl.OutPort):
                                    p.connectedTo.append(port)
                if isinstance(port, esdl.OutPort):
                    for con in new_build.asset:
                        if isinstance(con, (esdl.EConnection, esdl.GConnection)) and con.port[
                            0].carrier == port.carrier:
                            for p in con.port:
                                if isinstance(p, esdl.InPort):
                                    p.connectedTo.append(port)

            logging.debug("added", a.name, "to", new_build.name)

        profiles = []
        for prof in energy_system.eAllContents():
            if isinstance(prof, esdl.DrivenByProfile):
                profiles.append(prof)

        for p in profiles:
            asset_name = p.id.strip("_CS")

            for a in energy_system.eAllContents():
                if isinstance(a, esdl.Electrolyzer) and a.id == asset_name:
                    p.energyAsset = a

        energy_system = esh.energy_system

        return True

    else:
        return False


def place_synfuels(ex_49, ex_50, ex_5, ex_6, ex_7, ex_8, ex_9, dom_tech, year, energy_system):
    if ex_49 == "a":
        techorder = [["Synfuel1", "Synfuel2", "Synfuel3"], ["SynMeOHolefin1", "SynMeOHolefin2", "SynMeOHolefin3"],
                     ["PlasticOlefin1", "PlasticOlefin2"], ["BioGasolefin1"], ["Naphta1"]]
    else:
        techorder = [["Synfuel1", "Synfuel2", "Synfuel3"], ["SynMeOHolefin1", "SynMeOHolefin2", "SynMeOHolefin3"],
                     ["PlasticOlefin1", "PlasticOlefin2"], ["BioGasolefin1"], ["Naphta1"]]
        techorder = techorder[::-1]

    place_list = []
    for tech in techorder:
        for t in tech:
            table = pd.read_excel(r'data/{}'.format(table_dict[t])).set_index('index')

            if t in ["Synfuel1", "Synfuel2", "Synfuel3"]:
                ex_factor2 = ex_6
            if t in ["SynMeOHolefin1", "SynMeOHolefin2", "SynMeOHolefin3"]:
                ex_factor2 = ex_7
            if t in ["PlasticOlefin1", "PlasticOlefin2"]:
                ex_factor2 = ex_9
            if t in ["BioGasolefin1"]:
                ex_factor2 = ex_8
            if t in ["Naphta1"]:
                ex_factor2 = ex_5

            if ex_factor2 == 'a':
                continue

            count = table[year][ex_factor2]

            for i in range(count):
                place_list.append(t)

    place_order = locationorder[ex_50]

    for a in place_list:

        for p in place_order:

            if place_new_asset(a, p, dom_tech, energy_system):
                break

            else:
                continue


def apply_elecfill(ex, year, energy_system):
    dom_tech = None

    if ex == 'a':
        return

    if year == 2025:
        return

    if ex == 'b':
        fill_percentage = 0.25
    if ex == 'c':
        fill_percentage = 0.5
    if ex == 'd':
        fill_percentage = 0.75
    if ex == 'e':
        fill_percentage = 1

    building_list = ['Lyondell_MVB', 'Neste_MVB', 'Bungeloders_MVB', 'Indorama_EurA', 'Caldic_EurC', 'AlcoEnergy_EurC',
                     'AVR_BotA', 'Cabot_BotA', 'EKC_BotA', 'Invista_BotA', 'ENCI_Eur', 'Climax_BotA', 'Ducor_BotA',
                     'Nouryon_BotA', 'Wilmar_Per', 'Arkema_Per', 'Cerexagri_Per', 'Huntsman_BotA', 'Hexion_BotA',
                     'AirProducts_BotA', 'Shinetsu_BotA', 'Hexion_Per', 'Tronox_BotA', 'Nouryon_BotA']

    electrolyzer_space = 6

    for b in building_list:

        for build in energy_system.eAllContents():
            if isinstance(build, esdl.Building) and build.name == b:
                new_build = build

        free_space = new_build.area.buildingDensity
        fill_space = free_space * fill_percentage
        fill_count = divmod(fill_space, electrolyzer_space)[0]

        for i in range(int(fill_count)):
            place_new_asset("Electrolyzer", b, dom_tech, energy_system)

        if fill_count > 0:

            elec_building = False

            for build in energy_system.eAllContents():
                check_name = b.replace("_", "elec_", 1)
                if isinstance(build, esdl.Building) and build.name == check_name:
                    elec_building = True
                    elec_build = build

            if elec_building == True:
                for con in elec_build.asset:
                    if isinstance(con, esdl.EConnection):
                        for p in con.port:
                            if isinstance(p, esdl.OutPort):
                                out_port_con = p

                for elec in new_build.asset:
                    if isinstance(elec, esdl.Electrolyzer):
                        elec.port[0].connectedTo.clear()
                        elec.port[0].connectedTo.append(out_port_con)

            else:
                new_build_copy = new_build.deepcopy()

                new_build_copy.name = new_build_copy.name.replace("_", "elec_", 1)
                new_build_copy.id = new_build_copy.id.replace("_", "elec_", 1)

                for a in new_build_copy.asset:
                    if isinstance(a, esdl.EConnection):
                        econ = a
                        econ.name = econ.name.replace("_", "elec_", 1)
                        econ.id = econ.id.replace("_", "elec_", 1)

                for p in econ.port:
                    p.id = p.id.replace("_", "elec_", 1)

                for elec in new_build.asset:
                    if isinstance(elec, esdl.Electrolyzer):
                        elec.port[0].connectedTo.clear()
                        econ.port[1].connectedTo.append(elec.port[0])

                new_build_copy.asset.clear()
                new_build_copy.asset.append(econ)
                new_build.area.asset.append(new_build_copy)