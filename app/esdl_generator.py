from mapping_functions import *
from datetime import datetime
import boto3
import os

esdl_file = 'data/2021_hic_description.esdl'
s3_client = boto3.client('s3')


def generate_esdl(scenario_uuid, scenario, bucket_name):
    new_name = "2021"
    resource_existing, esdl_description, carriers, sectors = load_esdl(esdl_file)
    energy_system = resource_existing.contents[0]
    # init function for closing of plants (external factor 14)
    ten_list, twenty_list, fifty_list, twenty1_list = close_others_init(2025, energy_system)
    # LNG factor
    esdl_dict = {}
    for year in range(2025, 2055, 5):
        # adjustment of InstanceDate (required for ETM requests)
        for ins in energy_system.eAllContents():
            if isinstance(ins, esdl.Instance) and ins.name in ["2021", new_name]:
                ins.date = esdl.InstanceDate(date=datetime(year, 1, 1, 0, 0, 0))
                new_name = str(year) + "_base"
                ins.name = new_name

        # add commodity prices
        add_commodityprices(scenario['x28'], year, energy_system)

        # apply free space MV factor
        apply_MV_freespace(scenario['x4'], year, energy_system)

        # applying capacity reduction functions
        apply_closingpaths_new(scenario, scenario_uuid, year, energy_system)
        close_others2(scenario['x14'], ten_list, twenty_list, fifty_list, twenty1_list, year, energy_system)

        # applying boiler/furnace mapping function, related to external factor 16
        dom_tech = apply_furbopaths(scenario['boiler_path'], scenario_uuid, year, carriers, energy_system)
        apply_cogenpaths(scenario['cogen_path'], scenario_uuid, year, carriers, energy_system)
        apply_powergenpaths(scenario['powergen_path'], scenario_uuid, year, carriers, energy_system)

        # apply onshore / offshore renewable paths
        apply_onshorewindgrowth(scenario['x18'], year, energy_system)
        apply_onshoresolargrowth(scenario['x19'], year, energy_system)
        apply_offshorewindgrowth(scenario['x20'], year, energy_system)
        apply_H2export(scenario['x23'], year, energy_system)
        apply_Ggasswitch(scenario['x24'], scenario['x25'], year, carriers, energy_system)
        apply_shorepowergrowth(scenario['x26'], year, energy_system)

        # apply HVISION and CCS
        apply_CCSBase(scenario['x1'], year, carriers, energy_system)
        apply_HVision(scenario['x35'], year, carriers, energy_system)

        # nuclear plant
        place_nuclearplant(scenario['x17'], year, carriers, energy_system)
        close_refineries(scenario['x1'], scenario['x39'], scenario['x40'], year, energy_system)

        place_synfuels(scenario['x49'], scenario['x50'], scenario['x5'], scenario['x6'], scenario['x7'],
                       scenario['x8'], scenario['x9'], dom_tech, year, energy_system)
        apply_elecfill(scenario['x15'], year, energy_system)

        esdl_path = save_esdl(resource_existing, esdl_description, scenario_uuid, str(year))
        esdl_dict[year] = esdl_path
        ETM_scenario = pd.Series({"contextScenario": add_ETMscenario(scenario['x34'], year)})
        s3_client.put_object(
            Bucket=bucket_name,
            Key=scenario_uuid + '/' + str(year) + '/contextScenario.json',
            Body=ETM_scenario.to_json()
        )
        s3_client.upload_file(
            Filename=esdl_path,
            Bucket=bucket_name,
            Key=scenario_uuid + '/' + str(year) + '/base.esdl'
        )
        os.remove(esdl_path)
        logging.info('Created and upload the base.esdl for UUID {} and year {}'.format(scenario_uuid, year))

    return esdl_dict
