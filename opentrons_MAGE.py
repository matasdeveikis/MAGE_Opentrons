# Define reservoirs

# Step: Amplification of SEVA CRISPR plasmid (Optional)
# Modules: 
# Inputs: Number of samples
# Outputs: 

# Step: Restriction digestion of SEVA CRISPR plasmids (Optional)
# Modules:
# Inputs: Number of samples, lysed and resuspended SEVA CRISPR E. coli
# Outputs:    
# Comments: Use magnetic bead purification instead of gel electrophoresis

# Step: Annealing of spacer oligonucleotides
# Modules: Thermocycler
# Inputs: Number of samples, unique spacers
# Outputs:
# Comments: Ignore Step 1

# Step: Insertion of spacers into the SEVA CRISPR plasmid
# Modules: 
# Inputs: Number of samples, annealed spacers
# Outputs: 
    
# Step: ssDNA and CRISPR plasmid HEAT SHOCK (instead of electroporations)
# Modules: Temperature
# Inputs: electrocompetent cells with Ssr, stock solutions of the ssDNA mutagenic oligo, target temperature/other conditions as a user input
# Outputs:

#Import opentrons and run
import sys
!{sys.executable} -m pip install opentrons

from opentrons import simulate
metadata = {'apiLevel': '2.8'}
protocol = simulate.get_protocol_api('2.8')

#Labware
# Assume that we start with a P. putida strain that has edd deleted and posseses both Cas9 and recombinase plasmids
dilution_plate_1 = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)   #1:10 Dilution from Heatshock Output
tiprack_20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 2)
tiprack_200 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 3)
temp_hot = protocol.load_module('temperature module', 4)                #For Heatshock
bacteria_media = protocol.load_labware('nest_12_reservoir_15ml', 5)      #Bacterial Culture(A1) + LB_Media(A6)
temp_cold = protocol.load_module('temperature module', 6)               #For Heatshock
storage_oligos = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', 7)  #Stores Oligos
solid_agar_glucose = protocol.load_labware('axygen_1_reservoir_90ml', 8)       #Solid Agar pre-made on the reservoir
solid_agar_lupanine = protocol.load_labware('axygen_1_reservoir_90ml', 9)      #Solid Agar pre-made on the reservoir
CRISPR_plasmid = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 10)
dilution_plate_2 = protocol.load_labware('corning_96_wellplate_360ul_flat', 11)   #1:100 Dilution from Heatshock Output

#pipettes
p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20])
p300 = protocol.load_instrument('p300_multi', 'right', tip_racks=[tiprack_200])
protocol.max_speeds['Z'] = 10
Bacteria= bacteria_media.wells ('A1')
Media= bacteria_media.wells ('A6')

#Add CRISPR plasmid to each of the PCR strip containing different oligos
p20.distribute(5, CRISPR_plasmid.wells ('A1'), storage_oligos.columns()[0:12], touch_tip=True, new_tip='always') # A1 is where the CRISPR plasmids are located on the tuberack
    # Need to find a way to drop tip with every addition of CRISPR plasmid
#Add cells to each strip
p300.distribute(100, bacteria_media.wells ('A1'), storage_oligos.columns()[0:12])
    # Need to find a way to drop tip with every addition of CRISPR plasmid
#Heat shock protocol

#Insert 180ul of LB_Media(H1) from bacteria_media into each well of dilution_plate_1

#Take 20ul from PCR_STRIP that has undergone heat shock and place in dilution_plate_1 + MIX

#Insert 180ul of LB_Media(H1) from bacteria_media into each well of dilution_plate_2

#Take 20ul from dilution_plate_1 that is now in 1:10 dilution and place in dilution_plate_2 + MIX to get 1:100 dilution

##OUTPUT: in dilution_plate_2 in each well, we have bacterial cells in 1:100 dilution with different oligos

#PLATING: Spot 15ul from dilution_plate_2 into solid_agar_glucose

#PLATING: Spot 15ul from dilution_plate_2 into solid_agar_lupanine

for line in protocol.commands(): 
        print(line)