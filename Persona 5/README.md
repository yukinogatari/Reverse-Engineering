# Persona 5

Extracts and decompresses miscellaneous data used in Persona 5.

## p5_unpack.py

### p5_cutin_unpack

Function to extract packs of GLH-formatted data containing cutin images.
(Data found in the `cutin` directory, with the extensions `.000` and `.001`.)

### p5_eboot_ex

Function to find and extract GLH-formatted data within the decrypted P5 EBOOT.

## p5_text.py

A bunch of miscellaneous functions for parsing, extracting, and decoding text
stored in `.bf`, `.bmd`, `.pak`, and `.pac` files.

The translation table used to decode two-byte CP932-encoded text is located in
`p5_table.py`. The table is currently incomplete, missing mappings for ~100
byte-pairs used in the script (accounting for approximately 0.01% of the text),
and some mappings may be incorrect.