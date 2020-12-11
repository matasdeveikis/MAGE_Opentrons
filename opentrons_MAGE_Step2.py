#Import opentrons and run
#import sys
#!{sys.executable} -m pip install opentrons

from opentrons import simulate
metadata = {'apiLevel': '2.8'}
protocol = simulate.get_protocol_api('2.8')

# Step 2
protocol.pause('Replace tips and add agarose plates')
#change modules 
dilution_plate_1 = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)   #1:10 Dilution from Heatshock Output
temp_hot = protocol.load_module('tempdeck', 4)                #For Heatshock
hot_plate = temp_hot.load_labware('corning_96_wellplate_360ul_flat')
solid_agar_glucose = protocol.load_labware('axygen_1_reservoir_90ml', 8)       #Solid Agar pre-made on the reservoir
solid_agar_lupanine = protocol.load_labware('axygen_1_reservoir_90ml', 9)      #Solid Agar pre-made on the reservoir
reagents = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 10)
dilution_plate_2 = protocol.load_labware('corning_96_wellplate_360ul_flat', 11)   #1:100 Dilution from Heatshock Output
#also hot_plate from step 1 in module 4 remains unchanged

#Reagents
CRISPR_plasmid = reagents.wells ('A1') 
CaCL_1M = reagents.wells ('A2') 
PBS = reagents.wells ('A3')

#new pipette tips
tiprack_300 = [
        protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(s), '300ul Tips')
        for s in [2, 5]]

#pipettes
p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=tiprack_300)
protocol.max_speeds['Z'] = 10

protocol.resume()

#Add 270ul to dilution_plate_1 and dilution_plate_2 
p300.distribute(270, PBS, dilution_plate_1.columns()[0:12], touch_tip=False, new_tip='always') 
p300.distribute(270, PBS, dilution_plate_2.columns()[0:12], touch_tip=False, new_tip='always')

for i in range(0, 96):
    p300.pick_up_tip()   
    p300.aspirate(30, hot_plate.wells()[i])           #Take heatshock cells
    p300.dispense(30, dilution_plate_1.wells()[i])    #Put into dilution_plate_1
    p300.mix(3,50, dilution_plate_1.wells()[i])       #Mix
    p300.aspirate(30, dilution_plate_1.wells()[i])    #Take dilution_plate_1 cells
    p300.dispense(30, dilution_plate_2.wells()[i])    #Put into dilution_plate_2
    p300.mix(3,50, dilution_plate_2.wells()[i])       #Mix
    p300.return_tip()                                 #Only 1 tip used per transfer between plates per well

##OUTPUT: in dilution_plate_2 in each well, we have bacterial cells in 1:100 dilution with different oligos

#PLATING: Spot 10ul from dilution_plate_2 into solid_agar_glucose

#PLATING: Spot 10ul from dilution_plate_2 into solid_agar_lupanine

for line in protocol.commands(): 
        print(line)