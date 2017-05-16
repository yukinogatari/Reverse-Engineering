# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import os
from util import *

SCENARIO_MAGIC = "PJADV_SF0001"
TEXTDATA_MAGIC = "PJADV_TF0001"
XOR_KEY        = 0xC5
XOR_KEY_SHIFT  = 0x5C

def pjadv_dump(scenario, textdata, out_file = None):
  
  out_file = out_file or os.path.splitext(scenario)[0] + ".txt"
  out = open(out_file, "wb")
  
  with open(textdata, "rb") as f:
    text = f.read()
    text = pjadv_dec(text)
    text = BinaryString(text)
  
  with BinaryFile(scenario, "rb") as scn:
    if not scn.read(12) == SCENARIO_MAGIC:
      return
    if not text.read(12) == TEXTDATA_MAGIC:
      return
    
    cmd_count = scn.get_u32() # ???
    
    scn.seek(0, 2)
    scn_size = scn.tell()
    scn.seek(0x20)
    
    str_count = text.get_u32()
    
    while scn.tell() < scn_size:
      size = scn.get_u8() - 1
      cmd  = scn.get_u16() | (scn.get_u8() << 16)
      
      data = scn.read(size * 4)
      
      name   = ""
      string = ""
      
      # Regular text?
      if cmd == 0x800003:
        name_off = to_u32(data[4:8])
        str_off  = to_u32(data[8:12])
        
        name   = get_str(text, name_off) if name_off else ""
        string = get_str(text, str_off)
      
      # Options
      elif cmd == 0x010108:
        str_off = to_u32(data[:4])
        string  = get_str(text, str_off)
      
      # Option prompt
      elif cmd == 0x030003:
        name    = "Option"
        str_off = to_u32(data[4:8])
        string  = get_str(text, str_off)
      
      if name:
        out.write("[%s]\n" % name.encode("UTF-8"))
      
      if string:
        out.write(string.encode("UTF-8"))
        out.write("\n\n")
  
  out.close()

def pjadv_dec(data):
  
  data = bytearray(data)
  key  = XOR_KEY
  
  for i in range(len(data)):
    data[i] ^= key
    key += XOR_KEY_SHIFT
    key &= 0xFF
  
  return data

def get_str(data, offset):
  
  data.seek(offset)
  
  string = ""
  while True:
    ch = data.read(1)
    if len(ch) == 0:
      break
    
    string += ch
    if string[-2:] == "\x00\x00":
      string = string[:-2]
      break
  
  return string.decode("CP932")
  
if __name__ == "__main__":
  pjadv_dump("archive-trial/scenario.dat", "archive-trial/textdata.bin")
  pjadv_dump("archive-lilycle/scenario.dat", "archive-lilycle/textdata.bin")
  pjadv_dump("archive-taisho/scenarioeng.dat", "archive-taisho/textdataeng.bin")

### EOF ###