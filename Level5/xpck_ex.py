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
from level5_dec import *

XPCK_MAGIC = "XPCK"

def xpck_ex(filename, out_dir = None):
  out_dir = out_dir or os.path.splitext(filename)[0]
  
  f = BinaryFile(filename, "rb")
  
  if not f.read(4) == XPCK_MAGIC:
    print "Invalid XPCK file."
    f.close()
    return
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  file_count    = f.get_u8()
  flags         = f.get_u8()
  file_tbl_off  = f.get_u16() * 4
  fn_table_off  = f.get_u16() * 4
  data_off      = f.get_u16() * 4
  file_tbl_size = f.get_u16() * 4
  fn_table_size = f.get_u16() * 4
  data_size     = f.get_u32() * 4
  
  # print bin(flags)
  # print hex(file_tbl_off), file_tbl_size
  # print hex(fn_table_off), fn_table_size
  # print hex(data_off), data_size
  
  # Parse the filename table.
  f.seek(fn_table_off)
  
  fn_table = f.read(fn_table_size)
  fn_table = level5_dec(fn_table)
  fn_table = BinaryString(fn_table)
  
  # Now parse the file table.
  f.seek(file_tbl_off)
  file_tbl = f.read(file_tbl_size)
  file_tbl = BinaryString(file_tbl)
  
  for i in range(file_tbl_size / 12):
    fn_crc = file_tbl.get_u32()
    fn_off = file_tbl.get_u16()
    offset = file_tbl.get_u16()
    size   = file_tbl.get_u16()
    # These are actually three-byte values, just... packed weirdly.
    offset += file_tbl.get_u8() << 16
    size   += file_tbl.get_u8() << 16
    
    fn_table.seek(fn_off)
    fn = fn_table.get_str()
    fn = os.path.join(out_dir, fn)
    
    print " ->", fn
    # print "{:<80}".format(fn), "0x%04X  " % (f.tell() - 12), "0x%08X  " % fn_crc, "0x%08X  " % fn_off, "0x%08X  " % offset, "0x%08X" % size
    
    # Get our data.
    f.seek(data_off + offset * 4)
    data = f.read(size)
    
    # Sometimes it's compressed, so see if we can decompress it. If not, w/e.
    try:
      data = lzss_dec(data[4:])
    except:
      pass
    
    with open(fn, "wb") as f2:
      f2.write(data)
    
    # Check for nesting.
    if data[:4] == XPCK_MAGIC:
      xpck_ex(fn)
  
  f.close()

if __name__ == "__main__":
  # xpck_ex("d03_01a.xc")
  # xpck_ex("t106d43.xc")
  # for fn in list_all_files("3DSLevel5XI"):
  for fn in list_all_files("fa"):
    ext = os.path.splitext(fn)[1].lower()
    
    if not ext.startswith(".x"):
      continue
    
    print fn
    xpck_ex(fn)
    print

### EOF ###