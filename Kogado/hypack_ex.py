################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from util import BinaryFile

HYPACK_MAGIC = "HyPack\0"

def hypack_ex(in_file, out_dir = None):
  
  if not out_dir:
    out_dir = os.path.splitext(in_file)[0]
  
  f = BinaryFile(in_file, "rb")
  
  if not f.read(7) == HYPACK_MAGIC:
    print "Invalid HyPack file."
    return
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  unk     = f.read(1)
  tbl_off = f.get_u32() + 0x10
  entries = f.get_u32()
  
  for i in range(entries):
    entry_off = tbl_off + (i * 0x30)
    f.seek(entry_off)
    
    filename = f.read(0x15).strip(u"\0")
    ext = f.read(3)
    
    filename = filename + "." + ext
    out_file = os.path.join(out_dir, filename)
    
    print filename
    
    data_off = f.get_u32() + 0x10
    dec_size = f.get_u32()
    cmp_size = f.get_u32()
    
    f.seek(data_off)
    data = f.read(cmp_size)
    
    if not cmp_size == dec_size:
      # I've got a bunch of compressed/decompressed samples, but I have no idea
      # how on earth it gets from point A to point B, so just leaving this alone.
      out_file += ".cmp"
    
    with open(out_file, "wb") as f2:
      f2.write(data)

if __name__ == "__main__":
  hypack_ex(u"Shirokoi/EvBG.pak")
  hypack_ex(u"Shirokoi/EvCG.pak")
  hypack_ex(u"Shirokoi/EvSE.pak")
  hypack_ex(u"Shirokoi/Script.pak")
  hypack_ex(u"Shirokoi/Game.pak")

### EOF ###