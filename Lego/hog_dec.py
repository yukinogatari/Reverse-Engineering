# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

DEBUG = False

# Slightly modified from fib_dec
# .fib decompression algorithm reverse-engineered by FireyFly:
# https://github.com/FireyFly | https://twitter.com/FireyFly

def hog_dec(data):
  
  data = bytearray(data)
  res = bytearray()
  
  p = 0
  
  while p < len(data):
    b = data[p]
    p += 1
    
    if DEBUG:
      print "[0x%08X][0x%08X]" % (p - 1, len(res)),
    
    # End of data marker.
    if b >= 0xFC:
      if DEBUG:
        print "End marker: 0x%02X" % b
      count = b - 0xFC
      res += data[p : p + count]
      p += count
      break
    
    # Raw data.
    # 111xxxxx
    # Count -> (x + 1) * 4
    if b >= 0xE0:
      
      count = ((b & 0b11111) + 1) * 4
      
      if DEBUG:
        print "Raw: 0x%02X" % b, "->", count
      
      res += data[p : p + count]
      p += count
    
    # Raw data, then copy from the output buffer.
    else:
      
      if DEBUG:
        print "Read back: 0x%02X" % b,
      
      # 110zyyxx zzzzzzzz zzzzzzzz yyyyyyyy
      # Raw count  -> x
      # Read count -> y + 5
      # Offset     -> z + 1
      if b >= 0xC0:
        b2, b3, b4 = data[p : p + 3]
        p += 3
        
        raw    =  (b & 0b00000011)
        count  = ((b & 0b00001100) << 6) + b4 + 5
        offset = ((b & 0b00010000) << 12) + (b2 << 8) + b3 + 1
        
        if DEBUG:
          print "0x%02X 0x%02X 0x%02X" % (b2, b3, b4),
      
      # 10yyyyyy xxzzzzzz zzzzzzzz
      # Raw count  -> x
      # Read count -> y + 4
      # Offset     -> z + 1
      elif b >= 0x80:
        b2, b3 = data[p : p + 2]
        p += 2
        
        raw    = b2 >> 6
        count  = (b & 0b00111111) + 4
        offset = ((b2 & 0b00111111) << 8) + b3 + 1
        
        if DEBUG:
          print "0x%02X 0x%02X" % (b2, b3),
      
      # 0zzyyyxx zzzzzzzz
      # Raw count  -> x
      # Read count -> y + 3
      # Offset     -> z + 1
      else:
        b2 = data[p]
        p += 1
        
        raw    =  (b & 0b00000011)
        count  = ((b & 0b00011100) >> 2) + 3
        offset = ((b & 0b01100000) << 3) + b2 + 1
        
        if DEBUG:
          print "0x%02X" % (b2),
      
      if DEBUG:
        print "->", raw, count, offset
      
      res += data[p : p + raw]
      p += raw
      
      for i in range(count):
        res.append(res[-offset])
  
  return res

if __name__ == "__main__":
  import os
  DEBUG = True
  files = [
    # "008217.dat-0000",
    # "008217.dat-0001",
    # "008217.dat-0002",
    "test.bin",
  ]
  
  for fn in files:
    print
    print "#" * 20, fn, "#" * 20
    print
    with open(fn, "rb") as f:
      data = f.read()
    data = hog_dec(data)
    with open(fn + ".dec", "wb") as f:
      f.write(data)

### EOF ###