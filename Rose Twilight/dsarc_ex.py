# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *

def dsarc_ex(filename, out_dir):
  with open(filename, "rb") as f:
    data = bytearray(f.read())
  
  magic = data[:8]
  
  if not magic == "DSARC FL":
    return
  
  num_files = to_u32(data[8:12])
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  for i in range(num_files):
    p = 0x10 + (i * 0x30)
    filename = data[p : p + 0x20].decode("UTF-8").strip("\0")
    file_len = to_u32(data[p + 0x28 : p + 0x2C])
    file_off = to_u32(data[p + 0x2C : p + 0x30])
    
    print filename
    
    file_data = data[file_off : file_off + file_len]
    with open(os.path.join(out_dir, filename), "wb") as f:
      f.write(file_data)

if __name__ == "__main__":
  
  # Textures
  dsarc_ex("data/texture/00000_Resident.dat", "data-dec/texture/00000_Resident")
  dsarc_ex("data/texture/99999_System.dat", "data-dec/texture/99999_System")

### EOF ###