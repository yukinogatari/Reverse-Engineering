################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from util import *

GLH_MAGIC = "\x30\x48\x4C\x47" # "0HLG"
GLZ_MAGIC = "\x30\x5A\x4C\x47" # "0ZLG"

def glz_dec(data):
  data = bytearray(data)
  
  glz_magic = data[:0x04]
  if not glz_magic == GLZ_MAGIC:
    print "Invalid GLZ data."
    return data
  
  unk      = to_u32(data[0x04:0x08]) # 0x01105030
  dec_size = to_u32(data[0x08:0x0C])
  cmp_size = to_u32(data[0x0C:0x10])
  marker   = data[0x10]
  # 0x11-0x20 = padding?
  
  res = bytearray()
  p   = 0x20
  
  # print "Marker: 0x%02X" % marker
  
  while p < len(data):
    b = data[p]
    p += 1
    
    # This is the dumbest compression algorithm I've ever seen.
    if b == marker:
      offset = data[p]
      p += 1
      
      # Because we need some way to use the marker as part of the data...
      if offset == marker:
        res.append(marker)
        continue
      
      count = data[p]
      p += 1
      
      # print "[0x%08X][0x%08X] Read: 0x%02X %s 0x%02X" % (p, len(res), offset, bin(offset), count)
      
      # And because we need a way to to use the marker value as an offset...
      if offset > marker:
        offset -= 1
      
      for i in range(count):
        res.append(res[-offset])
    
    else:
      # print "[0x%08X][0x%08X] Byte: 0x%02X" % (p, len(res), b)
      res.append(b)
  
  return res

def glh_unpack(data, dec = True):
  data = bytearray(data)
  glh_magic = data[:0x04]
  
  if not glh_magic == GLH_MAGIC:
    print "Invalid GLH data."
    return
  
  unk1     = to_u32(data[0x04:0x08]) # 0x01105030
  unk2     = to_u32(data[0x08:0x0C]) # Always 1? Maybe GLZ count?
  dec_size = to_u32(data[0x0C:0x10])
  cmp_size = to_u32(data[0x10:0x14]) # Includes 0x20 header.
  # 0x14-0x20 = padding?
  
  glz_data = data[0x20:]
  
  if dec:
    return glz_dec(glz_data)
  else:
    return glz_data

def p5_unpack(filename, dec = True):
  f = BinaryFile(filename, "rb")
  
  file_count = f.get_u32be()
  
  for i in range(file_count):
    file_id   = f.get_u32be()
    file_size = f.get_u32be()
    file_data = f.read(file_size)
    
    # print file_id, file_size
    file_data = glh_unpack(file_data, dec = dec)
    # print
    
    if dec:
      out_file = filename + "-%d.dds" % i
    else:
      out_file = filename + "-%d.dat" % i
    
    with open(out_file, "wb") as f2:
      f2.write(file_data)
  
  f.close()

if __name__ == "__main__":
  
  dirname = u"cutin"
  for fn in list_all_files(dirname):
    if not os.path.splitext(fn)[1] in [u".000", u".001"]:
      continue
    
    print fn
    p5_unpack(fn)
    # print

### EOF ###