#Import opentrons and run
#import sys
#!{sys.executable} -m pip install opentrons

import math
from opentrons import simulate
metadata = {'apiLevel': '2.8'}
protocol = simulate.get_protocol_api('2.8')

# Step 2
protocol.pause('Replace tips and add agarose plates')
#change modules 

dilution_plate_1 = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)   #1:10 Dilution from Heatshock Output
temp_hot = protocol.load_module('tempdeck', 4)                #For Heatshock
hot_plate = temp_hot.load_labware('corning_96_wellplate_360ul_flat')
solid_agar_glucose = protocol.load_labware('corning_96_wellplate_360ul_flat', 8)       #Solid Agar pre-made on the reservoir
solid_agar_lupanine = protocol.load_labware('corning_96_wellplate_360ul_flat', 9)      #Solid Agar pre-made on the reservoir
reagents = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 10)
dilution_plate_2 = protocol.load_labware('corning_96_wellplate_360ul_flat', 11)   #1:100 Dilution from Heatshock Output
#also hot_plate from step 1 in module 4 remains unchanged

# Variables
oligos = 96
electroporation = False

#Reagents
CRISPR_plasmid = reagents.wells ('A1') 
PBS = reagents.wells ('A2')
if electroporation == False:
    CaCL_1M = reagents.wells ('A3')

#new pipette tips
tiprack_300 = [
        protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(s), '300ul Tips')
        for s in [2, 5]]

tiprack_20 = [
        protocol.load_labware(
            'opentrons_96_filtertiprack_20ul', str(s), '300ul Tips')
        for s in [3]]

#pipettes
p300 = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=tiprack_300)
p20 = protocol.load_instrument('p20_multi_gen2', 'left', tip_racks=tiprack_20)
protocol.max_speeds['Z'] = 10

def N_to_96(n): #Does not take inputs above 
    if n<=12:
        dest = 'A' + str(n%13)
        return dest
    else:
        raise NameError('N_to_96 input is above 12')


#Add 270ul to dilution_plate_1 and dilution_plate_2 
p300.distribute(270, PBS, dilution_plate_1.columns()[0:12] and dilution_plate_2.columns()[0:12], touch_tip=False, new_tip='once') 

for i in range(1, math.ceil(oligos/8)+1):
    p300.pick_up_tip()
    p300.transfer(30, hot_plate[N_to_96(i)], dilution_plate_1[N_to_96(i)], touch_tip = True, trash = False, new_tip = 'never', blow_out = True, mix_after = (3, 150))
    p300.transfer(30, dilution_plate_1[N_to_96(i)], dilution_plate_2[N_to_96(i)], touch_tip = True, trash = True, new_tip = 'never', blow_out = True, mix_after = (3, 150))
    p300.drop_tip()                                 #Only 1 tip used per transfer between plates per well

#OUTPUT: in dilution_plate_2 in each well, we have bacterial cells in 1:100 dilution with different oligos


#PLATING: Spot 10ul from dilution_plate_2 into solid_agar_glucose
#PLATING: Spot 10ul from dilution_plate_2 into solid_agar_lupanine
## Spoting constants:  

spot_vol=10
#dead_vol=2
spotting_dispense_rate=0.025
stabbing_depth=2
#DEFAULT_HEAD_SPEED = {'x': 400, 'y': 400,'z': 125, 'a': 125}
#SPOT_HEAD_SPEED = {'x': 400, 'y': 400, 'z': 125,'a': 125 // 4}
DISPENSING_HEIGHT = 5
SAFE_HEIGHT = 15  # height avoids collision with agar tray.

# Spot
for i in range(1, math.ceil(oligos/8)+1):
    p20.pick_up_tip()
    p20.aspirate(20, dilution_plate_2[N_to_96(i)])
    p20.move_to(solid_agar_glucose[N_to_96(i)].top(SAFE_HEIGHT))
    p20.move_to(solid_agar_glucose[N_to_96(i)].top(DISPENSING_HEIGHT))
    p20.dispense(volume=spot_vol, rate=spotting_dispense_rate)
    #robot.head_speed(combined_speed=max(SPOT_HEAD_SPEED.values()), **SPOT_HEAD_SPEED)
    #p20.move_to(solid_agar_glucose[N_to_96(i)].top(-1 * stabbing_depth))
    #robot.head_speed(combined_speed=max(DEFAULT_HEAD_SPEED.values()), **DEFAULT_HEAD_SPEED)
    p20.move_to(solid_agar_glucose[N_to_96(i)].top(SAFE_HEIGHT))
    p20.move_to(solid_agar_lupanine[N_to_96(i)].top(SAFE_HEIGHT))
    p20.move_to(solid_agar_lupanine[N_to_96(i)].top(DISPENSING_HEIGHT))
    p20.dispense(volume=spot_vol, rate=spotting_dispense_rate)
    #robot.head_speed(combined_speed=max(SPOT_HEAD_SPEED.values()), **SPOT_HEAD_SPEED)
    #p20.move_to(solid_agar_lupanine[N_to_96(i)].top(-1 * stabbing_depth))
    #robot.head_speed(combined_speed=max(DEFAULT_HEAD_SPEED.values()), **DEFAULT_HEAD_SPEED)
    p20.move_to(solid_agar_lupanine[N_to_96(i)].top(SAFE_HEIGHT))


    # Dispose of dead volume and tip
    # p20.dispense(dead_vol, spotting_waste)
    # p20.blow_out()

    p20.drop_tip()

for line in protocol.commands(): 
        print(line)