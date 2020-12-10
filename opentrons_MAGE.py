#Import opentrons and run
#import sys
#!{sys.executable} -m pip install opentrons

import numpy as np
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
        for s in [2]]

temp_hot = protocol.load_module('tempdeck', 4)                #For Heatshock
hot_plate = temp_hot.load_labware('corning_96_wellplate_360ul_flat')

bacteria_media = protocol.load_labware('nest_12_reservoir_15ml', 5)      #Bacterial Culture(A1) + LB_Media(A6)

temp_cold = protocol.load_module('tempdeck', 6) #For Heatshock

cold_plate = temp_cold.load_labware('corning_96_wellplate_360ul_flat')

storage_oligos = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', 7)  #Stores Oligos

reagents = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 10)


# 384 well plate example
# ot_384 = protocol.load_labware('corning_384_wellplate_112ul_flat', 10)

temp_cold.set_temperature(4)
temp_hot.set_temperature(42)

#pipettes
p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=tiprack_20)
p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=tiprack_300)
protocol.max_speeds['Z'] = 10

#Reagents
Bacteria = bacteria_media.wells ('A1')
Media = bacteria_media.wells ('A6')
CRISPR_plasmid = reagents.wells ('A1') 
CaCL_1M = reagents.wells ('A2') 
PBS = reagents.wells ('A3')


# Variables
plasmid_conc = 20 * np.ones(1)
oligos = 96
growth_temp = 37

#Add cells to each strip
p300.distribute(50, Bacteria, storage_oligos.columns()[0:12], touch_tip=False, new_tip='once')

#Add CRISPR plasmid to each of the PCR strip containing different oligos
for i in range(1):
    p20.distribute(50/float(plasmid_conc), CRISPR_plasmid, storage_oligos.columns()[0:12], touch_tip=True, new_tip='always') # A1 is where the CRISPR plasmids are located on the tuberack
# Could we do touch_tip=False, new_tip='never' here to save on tips

# To-do - electroporation option

# Heat shock protocol - save tips from here?
# Adding 100mM of CaCl
p20.distribute(5, CaCL_1M, cold_plate.columns()[0:12], touch_tip=True, new_tip='once')

for i in range(0, 12):
    p300.pick_up_tip()   
    p300.transfer(45, storage_oligos.columns()[i], cold_plate.columns()[i], touch_tip=True, new_tip='never')
    p300.return_tip()
    
protocol.delay(minutes = 15) 

for i in range(0, 12):
    p300.pick_up_tip()   
    p300.transfer(45, cold_plate.columns()[i], hot_plate.columns()[i], touch_tip=True, new_tip='never')
    p300.return_tip()
    
# need to figure out how long the operation takes to subtract from this
protocol.delay(seconds = 90) 

for i in range(0, 12):
    p300.pick_up_tip()   
    p300.transfer(45, hot_plate.columns()[i], cold_plate.columns()[i], touch_tip=True, new_tip='never')
    p300.return_tip()
    
p300.distribute(270, Media, hot_plate.columns()[0:12], touch_tip=False, new_tip='once')
temp_hot.set_temperature(growth_temp)
protocol.delay(minutes = 5) 

for i in range(0, 12):
    p300.pick_up_tip()   
    p300.transfer(30, cold_plate.columns()[i], hot_plate.columns()[i], touch_tip=True, new_tip='never')
    p300.return_tip()
protocol.delay(minutes = 60)

# Step 2
protocol.pause('Replace tips and add agarose plates')
#change modules 
dilution_plate_1 = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)   #1:10 Dilution from Heatshock Output
solid_agar_glucose = protocol.load_labware('axygen_1_reservoir_90ml', 8)       #Solid Agar pre-made on the reservoir
solid_agar_lupanine = protocol.load_labware('axygen_1_reservoir_90ml', 9)      #Solid Agar pre-made on the reservoir
dilution_plate_2 = protocol.load_labware('corning_96_wellplate_360ul_flat', 11)   #1:100 Dilution from Heatshock Output

protocol.resume()

p300.distribute(270, PBS, dilution_plate_1.columns()[0:12], touch_tip=False, new_tip='once')

for i in range(0, 12):
    p300.pick_up_tip()   
    p300.transfer(30, hot_plate.columns()[i], dilution_plate_1.columns()[i], touch_tip=True, new_tip='never')
    p300.return_tip()





#Insert 180ul of LB_Media(H1) from bacteria_media into each well of dilution_plate_1
#p300.distribute(180, reservoir.wells('H1'), dilution_plate_1.columns()[0:12])

#Take 20ul from PCR_STRIP that has undergone heat shock and place in dilution_plate_1 + MIX

#Insert 180ul of LB_Media(H1) from bacteria_media into each well of dilution_plate_2

#Take 20ul from dilution_plate_1 that is now in 1:10 dilution and place in dilution_plate_2 + MIX to get 1:100 dilution

##OUTPUT: in dilution_plate_2 in each well, we have bacterial cells in 1:100 dilution with different oligos




#PLATING: Spot 10ul from dilution_plate_2 into solid_agar_glucose

#PLATING: Spot 10ul from dilution_plate_2 into solid_agar_lupanine

for line in protocol.commands(): 
        print(line)