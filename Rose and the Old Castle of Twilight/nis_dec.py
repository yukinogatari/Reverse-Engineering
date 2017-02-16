################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os

from util import *

DEBUG = False

def nis_dec(data):
  
  magic = data[:8]
  
  if not magic == "YKCMP_V1":
    return
  
  unk      = to_u32(data[8:12])
  cmp_size = to_u32(data[12:16])
  dec_size = to_u32(data[16:20])
  
  res = bytearray()
  p   = 20 # Header
  
  while p < cmp_size:
    
    b = data[p]
    p += 1
    
    bit1 = b & 0b10000000
    bit2 = b & 0b01000000
    bit3 = b & 0b00100000
    
    if DEBUG:
      print "[0x%04X, 0x%06X]" % (p - 1, len(res)),
    
    # Raw data.
    if not bit1:
      if DEBUG:
        print "Raw bytes:", "%02X" % b
        for x in data[p : p + b]: print "%02X" % (x),
        print
        print
        
      count = b
      res += data[p : p + count]
      p += count
    
    else:
      
      if DEBUG:
        print "Copy back:", "%02X" % b,
      
      if b >= 0x80 and b < 0xC0:
        # count = ((b & 0b00110000) >> 4) + 1
        count = (((b - 0x80) & 0b11110000) >> 4) + 1
        offset = (b & 0b00001111) + 1
        
      elif b >= 0xC0 and b < 0xE0:
        b2 = data[p]
        p += 1
        
        if DEBUG:
          print "%02X" % b2,
        
        # count = (b & 0b00011111) + 2
        count = b - 0xC0 + 2
        offset = b2 + 1
        
      elif b >= 0xE0:
        b2 = data[p]
        b3 = data[p + 1]
        p += 2
        
        if DEBUG:
          print "%02X" % b2, "%02X" % b3,
          
        count  = ((b - 0xE0) << 4) + (b2 >> 4) + 3
        offset = ((b2 & 0b00001111) << 8) + b3 + 1
      
      if DEBUG:
        print "|", count, offset
      
      for i in range(count):
        res.append(res[-offset])
        if DEBUG:
          print "%02X" % (res[-1]),
      
      if DEBUG:
        print
        print
  
  # print cmp_size, dec_size, len(res)
  return res

if __name__ == "__main__":
  pass
  def dec_file(filename, out_file = "test.dat", offset = 0):
    with open(filename, "rb") as f:
      out = nis_dec(bytearray(f.read())[offset:])
    
    with open(out_file, "wb") as f:
      f.write(out)
  
  # Database
  base_dir = "data/database"
  for fn in os.listdir(base_dir):
    in_file  = os.path.join(base_dir, fn)
    out_file = os.path.join("data-dec/database", fn)
    print in_file
    dec_file(in_file, out_file, 8)
  
  # Stage
  base_dir = "data/stage"
  for fn in os.listdir(base_dir):
    in_file  = os.path.join(base_dir, fn)
    out_file = os.path.join("data-dec/stage", fn)
    print in_file
    dec_file(in_file, out_file, 8)

### EOF ###