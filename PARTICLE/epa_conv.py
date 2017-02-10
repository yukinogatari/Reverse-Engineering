################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from PIL import Image

from util import *

EPA_MAGIC = "EP\x01\x01"

def epa_conv(filename, out_file = None):
  
  if out_file == None:
    out_file = os.path.splitext(filename)[0] + ".png"
  
  data = None
  
  with open(filename, "rb") as f:
    
    if not f.read(4) == EPA_MAGIC:
      return False
    
    f.seek(0)
    data = bytearray(f.read())
    
  img = epa_conv_data(data)
  
  if not img:
    return False
    
  try:
    os.makedirs(os.path.dirname(out_file))
  except:
    pass
  
  img.save(out_file)
  
  return True

################################################################################
  
def epa_conv_data(data):
  
  if not data[:4] == EPA_MAGIC:
    return
  
  epa_type = to_u32(data[4:8])
  width    = to_u32(data[8:12])
  height   = to_u32(data[12:16])
  
  offsets = {
    0x01: 1,
    0x04: 2,
    0x07: 3,
    0x0F: 4,
    
    0x0D: width - 2,
    0x05: width - 1,
    0x02: width,
    0x03: width + 1,
    0x09: width + 2,
    
    0x0C: width * 2 - 2,
    0x0B: width * 2 - 1,
    0x06: width * 2,
    0x0A: width * 2 + 1,
    0x08: width * 2 + 2,
    
    0x0E: width * 3,
  }
  
  res = bytearray()
  p   = 16 # Header
  
  while p < len(data):
    
    b = data[p]
    p += 1
    
    # Read back.
    if b >= 0x10:
      offset = offsets[b >> 4]
      
      count = b & 0b00000111
      if b & 0b00001000:
        b2 = data[p]
        p += 1
        count = (count << 8) | b2
      
      for i in range(count):
        res.append(res[-offset])
    
    # Raw data
    else:
      res += data[p : p + b]
      p += b
  
  pixels = width * height
  
  b = Image.frombytes("L", (width, height), bytes(res[:pixels]), "raw", "L")
  g = Image.frombytes("L", (width, height), bytes(res[pixels : pixels * 2]), "raw", "L")
  r = Image.frombytes("L", (width, height), bytes(res[pixels * 2 : pixels * 3]), "raw", "L")
  
  if epa_type == 1:
    img = Image.merge("RGB", (r, g, b))
  else:
    a = Image.frombytes("L", (width, height), bytes(res[pixels * 3 : pixels * 4]), "raw", "L")
    img = Image.merge("RGBA", (r, g, b, a))
  
  return img

if __name__ == "__main__":
  
  for filename in os.listdir("graphic"):
    print filename
    epa_conv(os.path.join("graphic", filename))

### EOF ###