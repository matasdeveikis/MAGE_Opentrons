#Import opentrons and run
#import sys
#!{sys.executable} -m pip install opentrons

import numpy as np
import math
from opentrons import simulate
metadata = {'apiLevel': '2.8'}
protocol = simulate.get_protocol_api('2.8')

#Labware
# Assume that we start with a P. putida strain that has edd deleted and posseses both Cas9 and recombinase plasmids

tiprack_20 = [
        protocol.load_labware(
            'opentrons_96_filtertiprack_20ul', str(s), '300ul Tips')
        for s in [3]]

tiprack_300 = [
        protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(s), '300ul Tips')
        for s in [1, 2]]

temp_hot = protocol.load_module('tempdeck', 4)                #For Heatshock
hot_plate = temp_hot.load_labware('corning_96_wellplate_360ul_flat')

reservoir15 = protocol.load_labware('nest_12_reservoir_15ml', 5)      #Bacterial Culture(A1), LB_Media(A6) and PBS

temp_cold = protocol.load_module('tempdeck', 6) #For Heatshock

cold_plate = temp_cold.load_labware('corning_96_wellplate_360ul_flat')

storage_oligos = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', 7)  #Stores Oligos

tube2 = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 10)

#pipettes
p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=tiprack_20)
p300 = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=tiprack_300)
protocol.max_speeds['Z'] = 10

# Variables
plasmid_conc = 20 * np.ones(1)
oligos = 96
growth_temp = 37
electroporation = False

#Reagents
Bacteria = reservoir15.wells ('A1')
Media = reservoir15.wells ('A6')
PBS = reservoir15.wells ('A7', 'A8', 'A9', 'A10', 'A11', 'A12')
CRISPR_plasmid = tube2.wells ('A1')
if electroporation == False:
    CaCL_1M = tube2.wells ('D6') 

def N_to_96(n): #Does not take inputs above 12
    if n<=12:
        dest = 'A' + str(n%13)
        return dest
    else:
        raise NameError('N_to_96 input is above 12')

#Add cells to each strip
p300.distribute(50, Bacteria, storage_oligos.columns()[0:12], touch_tip = False, new_tip = 'once')

#Add CRISPR plasmid to each of the PCR strip containing different oligos
for i in range(1):
    p20.distribute(50/float(plasmid_conc[i]), CRISPR_plasmid, storage_oligos.columns()[0:12], touch_tip = True, new_tip = 'always', mix_after = (3, 15))

# Heat shock protocol
if electroporation == False:
    temp_cold.set_temperature(4)
    temp_hot.set_temperature(42)
    # Adding 100mM of CaCl
    p20.distribute(5, CaCL_1M, cold_plate.columns()[0:12], touch_tip=True, new_tip='once')
    
    # Moving to cold plate for 15 minute incubation at 4 degrees C
    for i in range(1, math.ceil(oligos/8)+1):
        p300.pick_up_tip(tiprack_300[1][N_to_96(i)])
        p300.transfer(45, storage_oligos[N_to_96(i)], cold_plate[N_to_96(i)], touch_tip = True, new_tip = 'never', blow_out = True, mix_after = (2, 25))
        p300.return_tip(tiprack_300[1][N_to_96(i)])
    
    protocol.delay(minutes = 15) 
    
    # Moving to hot plate for heat shock at 42 degrees C
    for i in range(1, math.ceil(oligos/8)+1):
        p300.pick_up_tip(tiprack_300[1][N_to_96(i)])
        p300.transfer(45, cold_plate[N_to_96(i)], hot_plate[N_to_96(i)], touch_tip = True, new_tip = 'never', blow_out = True)
        p300.return_tip(tiprack_300[1][N_to_96(i)])
        
    # need to figure out how long the operation takes to subtract from this
    protocol.delay(seconds = 90) 
    
    # Moving to hot plate for 5 minute incubation at 4 degrees C
    for i in range(1, math.ceil(oligos/8)+1):
        p300.pick_up_tip(tiprack_300[1][N_to_96(i)])
        p300.transfer(45, hot_plate[N_to_96(i)], cold_plate[N_to_96(i)], touch_tip = True, new_tip = 'never', blow_out = True)
        p300.return_tip(tiprack_300[1][N_to_96(i)])

    p300.pick_up_tip()
    for i in range(1, math.ceil(oligos/8)+1):
        if i <= 6:
            p300.transfer(270, PBS[0], hot_plate[N_to_96(i)], touch_tip=False, new_tip='never')
        else:
            p300.transfer(270, PBS[1], hot_plate[N_to_96(i)], touch_tip=False, new_tip='never')
    p300.drop_tip()
    
    temp_hot.set_temperature(growth_temp)
    protocol.delay(minutes = 5) 
    
    # Moving to hot plate for 60 minute incubation at selected temperature
    for i in range(1, math.ceil(oligos/8)+1):
        p300.pick_up_tip(tiprack_300[1][N_to_96(i)])
        p300.transfer(30, cold_plate[N_to_96(i)], hot_plate[N_to_96(i)], touch_tip = True, new_tip = 'never', blow_out = True, mix_after = (2, 150))
        p300.return_tip(tiprack_300[1][N_to_96(i)])
    
    temp_cold.deactivate()
    protocol.delay(minutes = 60)
    temp_hot.deactivate()
    
    # Moving to distribution plate
    # for i in range(1, math.ceil(oligos/8)+1):
    #     p300.pick_up_tip(tiprack_300[1][N_to_96(i)])
    #     p300.transfer(30, hot_plate[N_to_96(i)], dilution_plate_1[N_to_96(i)], touch_tip = True, trash = False, new_tip = 'never', blow_out = False, mix_after = (3, 15))
    #     p300.return_tip(tiprack_300[1][N_to_96(i)])

# Electroporation protocol
elif electroporation == True:
    pass

for line in protocol.commands(): 
        print(line)