# Cornering_Inhibition ON/OFF

$addr = 27

can500  # init can macro

delay 1

# open session

session 10C0

# configuration

xor_bits 0425 4 4 80 80
