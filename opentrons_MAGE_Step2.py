# import opentrons and run
# import sys
# !{sys.executable} -m pip install opentrons

import math
from opentrons import simulate
metadata = {'apiLevel': '2.8'}
protocol = simulate.get_protocol_api('2.8')

# Step 2
protocol.pause('Replace tips and add agarose plates')
# change modules 
dilution_plate_1 = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)   # 1:10 Dilution from Heatshock Output
dilution_plate_2 = protocol.load_labware('corning_96_wellplate_360ul_flat', 4)   # 1:100 Dilution from Heatshock Output
reservoir15 = protocol.load_labware('nest_12_reservoir_15ml', 5)      # Bacterial Culture(A1), LB_Media(A6) and PBS
temp_hot = protocol.load_module('tempdeck', 6)                # Heated plate from step 1 in module 6 remains unchanged
hot_plate = temp_hot.load_labware('corning_96_wellplate_360ul_flat')
solid_agar_glucose = protocol.load_labware('corning_96_wellplate_360ul_flat', 10)       # Solid Agar pre-made on the reservoir
solid_agar_lupanine = protocol.load_labware('corning_96_wellplate_360ul_flat', 11)      # Solid Agar pre-made on the reservoir

# add new pipette tips
tiprack_300 = [
        protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(s), '300ul Tips')
        for s in [2, 3]]

tiprack_20 = [
        protocol.load_labware(
            'opentrons_96_filtertiprack_20ul', str(s), '300ul Tips')
        for s in [7, 8]]


# Variables
oligos = input("Input number of mutagenic oligos to be used: ")
electroporation = False

# Reagents
Bacteria = reservoir15.wells ('A1')
Media = reservoir15.wells ('A6')
PBS = reservoir15.wells ('A7', 'A8', 'A9', 'A10', 'A11', 'A12')

# Pipettes
p300 = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=tiprack_300)
p20 = protocol.load_instrument('p20_multi_gen2', 'left', tip_racks=tiprack_20)
protocol.max_speeds['Z'] = 10

def N_to_96(n): #Does not take inputs above 
    if n<=12:
        dest = 'A' + str(n%13)
        return dest
    else:
        raise NameError('N_to_96 input is above 12')


# Add 270ul to dilution_plate_1 and dilution_plate_2 
    p300.pick_up_tip()
    for i in range(1, math.ceil(float(oligos)/8)+1):
        if i <= 6:
            p300.transfer(270, PBS[2], dilution_plate_1[N_to_96(i)], touch_tip=False, new_tip='never')
            p300.transfer(270, PBS[3], dilution_plate_2[N_to_96(i)], touch_tip=False, new_tip='never')
        else:
            p300.transfer(270, PBS[4], dilution_plate_1[N_to_96(i)], touch_tip=False, new_tip='never')
            p300.transfer(270, PBS[5], dilution_plate_2[N_to_96(i)], touch_tip=False, new_tip='never')
    p300.drop_tip()
    
for i in range(1, math.ceil(float(oligos)/8)+1):
    p300.pick_up_tip()
    p300.transfer(30, hot_plate[N_to_96(i)], dilution_plate_1[N_to_96(i)], touch_tip = True, trash = False, new_tip = 'never', blow_out = True, mix_after = (3, 150))
    p300.transfer(30, dilution_plate_1[N_to_96(i)], dilution_plate_2[N_to_96(i)], touch_tip = True, trash = True, new_tip = 'never', blow_out = True, mix_after = (3, 150))
    p300.drop_tip()                                 #Only 1 tip used per transfer between plates per well

# Spoting constants:  
spot_vol=10
dead_vol=2
spotting_dispense_rate=0.025
stabbing_depth=2
DISPENSING_HEIGHT = 5
SAFE_HEIGHT = 15  # height avoids collision with agar tray.

# Spot
for i in range(1, math.ceil(float(oligos)/8)+1):
    p20.pick_up_tip()
    p20.aspirate(10 + dead_vol, dilution_plate_2[N_to_96(i)])
    p20.move_to(solid_agar_glucose[N_to_96(i)].top(SAFE_HEIGHT))
    p20.move_to(solid_agar_glucose[N_to_96(i)].top(DISPENSING_HEIGHT))
    p20.dispense(volume=spot_vol, rate=spotting_dispense_rate)

    # Stabbing Gel 
    protocol.max_speeds['Z'] = 125 // 4  # Reduce speed of descent 
    protocol.max_speeds['A'] = 125 // 4  # Reduce speed of descent 
    p20.move_to(solid_agar_glucose[N_to_96(i)].top(-1 * stabbing_depth))
    protocol.max_speeds['Z'] = 125  # Going back to default speed
    protocol.max_speeds['A'] = 125  # Going back to default speed
    p20.move_to(solid_agar_glucose[N_to_96(i)].top(SAFE_HEIGHT))

    # Dispose of dead volume and tip
    # p20.dispense(dead_vol, spotting_waste) 
    # p20.blow_out()
    p20.drop_tip()
    

for i in range(1, math.ceil(float(oligos)/8)+1):
    p20.pick_up_tip()
    p20.aspirate(10 + dead_vol, dilution_plate_2[N_to_96(i)])
    p20.move_to(solid_agar_lupanine[N_to_96(i)].top(SAFE_HEIGHT))
    p20.move_to(solid_agar_lupanine[N_to_96(i)].top(DISPENSING_HEIGHT))
    p20.dispense(volume=spot_vol, rate=spotting_dispense_rate)

    # Stabbing Gel 
    protocol.max_speeds['Z'] = 125 // 4  # Reduce speed of descent 
    protocol.max_speeds['A'] = 125 // 4  # Reduce speed of descent 
    p20.move_to(solid_agar_lupanine[N_to_96(i)].top(-1 * stabbing_depth))
    protocol.max_speeds['Z'] = 125  # Going back to default speed
    protocol.max_speeds['A'] = 125  # Going back to default speed
    p20.move_to(solid_agar_lupanine[N_to_96(i)].top(SAFE_HEIGHT))


    # Dispose of dead volume and tip
    # p20.dispense(dead_vol, spotting_waste) 
    # p20.blow_out()
    p20.drop_tip()

for line in protocol.commands(): 
        print(line)
