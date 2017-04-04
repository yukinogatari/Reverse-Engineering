################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from util import *

GLH_MAGIC = "0HLG"
GLZ_MAGIC = "0ZLG"
GHM_MAGIC = "0MHG"

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
  
  # So basically, this is an LZ77-esque algorithm where all bytes are literals by
  # default, unless that byte is the "marker" byte (which varies between files--
  # presumably the value that occurs least frequently in the data), in which
  # case the subsequent byte is the offset to read back, followed by the count.
  # 
  # To allow the marker byte to actually be used as part of the data, two
  # consecutive occurrences become one literal. And to allow the marker value
  # to be used as an offset, values above it are shifted down by 1, effectively
  # limiting the read-back range to 0xFE.
  while p < len(data):
    b = data[p]
    p += 1
    
    if b == marker:
      offset = data[p]
      p += 1
      
      if offset == marker:
        res.append(marker)
        continue
      
      count = data[p]
      p += 1
      
      # print "[0x%08X][0x%08X] Read: 0x%02X %s 0x%02X" % (p, len(res), offset, bin(offset), count)
      
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
  
  glh_data = data[0x20:cmp_size]
  
  if dec and glh_data[:0x04] == GLZ_MAGIC:
    return glz_dec(glh_data)
  else:
    return glh_data

def p5_cutin_unpack(filename, dec = True):
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

def p5_eboot_ex(filename, out_dir = None):
  out_dir = out_dir or os.path.splitext(filename)[0]
  
  with open(filename, "rb") as f:
    data = f.read()
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  pos = 0
  while True:
    pos = data.find(GLH_MAGIC, pos)
    
    if pos == -1:
      break
    
    # Peek at the data size.
    glh_size = to_u32(data[pos + 0x10 : pos + 0x14])
    glh_data = data[pos : pos + glh_size]
    glh_data = glh_unpack(glh_data)
    
    if glh_data[:4] == "DDS\x20":
      ext = ".dds"
    else:
      ext = ".dat"
    
    out_file = os.path.join(out_dir, "GLH_%08X%s" % (pos, ext))
    
    with open(out_file, "wb") as f:
      f.write(glh_data)
    
    pos += 1

if __name__ == "__main__":
  
  # dirname = u"cutin"
  # for fn in list_all_files(dirname):
  #   if not os.path.splitext(fn)[1] in [u".000", u".001"]:
  #     continue
    
  #   print fn
  #   p5_cutin_unpack(fn)
  #   # print
  p5_eboot_ex("EBOOT.BIN")

### EOF ###