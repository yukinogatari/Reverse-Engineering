# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

def sly_dec(filename, out_file = None):
  
  if not out_file:
    out_file = filename + "-dec"
  
  with open(filename, "rb") as f:
    data = bytearray(f.read())
  
  res    = bytearray()
  marker = 1
  p      = 0
  
  while p < len(data):
    if marker == 1:
      # print "[0x%08X][0x%08X] Marker:" % (p, len(res)), bin(data[p]), hex(data[p])
      marker = 0x100 | data[p]
      p += 1
    
    if p >= len(data):
      break
    
    if marker & 1:
      # print "[0x%08X][0x%08X]   Byte: 0x%02X" % (p, len(res), data[p])
      res.append(data[p])
      p += 1
    
    else:
      # print "[0x%08X][0x%08X]      V:" % (p, len(res)), hex(data[p]), bin(data[p + 1])#bin((data[p] << 8) | data[p + 1])
      b1 = data[p]
      b2 = data[p + 1]
      p += 2
      
      offset = ((b2 & 0b00011111) << 8) | b1
      count  = (b2 >> 5) + 3
      # print "                          Count:", count
      # print "                         Offset:", offset
      
      # In practice, this probably reads from a circular buffer of the last 8192
      # bytes, but rather than bothering to keep a second copy of the data, I'm
      # just simulating it using the actual output stream.
      chunk = int(len(res) / 8192) * 8192
      
      if chunk + offset >= len(res):
        offset = chunk + offset - 8192
      else:
        offset = chunk + offset
      
      for i in range(count):
        res.append(res[offset + i])
    
    marker >>= 1
  
  with open(out_file, "wb") as f:
    f.write(res)

if __name__ == "__main__":
  sly_dec("samples/jb_intro")
  sly_dec("samples/ms_approach")
  sly_dec("samples/ms_exterior")
  sly_dec("samples/s_approach")
  sly_dec("samples/s_inspector")
  sly_dec("samples/s_security")
  sly_dec("samples/v_hub")

### EOF ###