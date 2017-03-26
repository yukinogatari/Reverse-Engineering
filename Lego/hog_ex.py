################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os

from util import *
from hog_dec import hog_dec

HOG_MAGIC = "WART3.00"

def hog_ex(filename, out_dir = None):
  out_dir = out_dir or os.path.splitext(filename)[0]
  
  print
  print "*" * 10, filename, "*" * 10
  print 
  
  f = BinaryFile(filename, "rb")
  hog_ex_data(f, out_dir)
  f.close()

def hog_ex_data(f, out_dir):
  
  if not f.read(8) == HOG_MAGIC:
    f.close()
    print "Invalid HOG file."
    return
  
  file_count = f.get_u32be()
  name_table = f.get_u32be()
  fn_size    = f.get_u32be()
  dirn_size  = f.get_u32be()
  
  f.seek(name_table)
  dirn_table = f.get_bin(dirn_size)
  fn_table   = f.get_bin(fn_size)
  
  f.seek(0x18)
  
  file_info = []
  
  # Read the file table.
  for i in range(file_count):
    offset      = f.get_u32be()
    cmp_size    = f.get_u32be()
    dec_size    = f.get_u32be()
    hash        = f.get_u32be()
    fn_offset   = f.get_u32be()
    dirn_offset = f.get_u32be()
    
    fn_table.seek(fn_offset)
    fn = fn_table.get_str()
    
    dirn_table.seek(dirn_offset)
    dirn = dirn_table.get_str()
    
    fn = os.path.join(dirn, fn)
    
    file_info.append((offset, cmp_size, dec_size, fn))
  
  # Get our files.
  for offset, cmp_size, dec_size, fn in file_info:
    print fn
    
    f.seek(offset)
    
    if cmp_size == 0:
      data = f.read(dec_size)
    
    else:
      data = f.read(cmp_size)
      # First four bytes are size.
      data = hog_dec(data[4:])
    
    out_file = os.path.join(out_dir, fn)
    
    try:
      os.makedirs(os.path.dirname(out_file))
    except:
      pass
    
    with open(out_file, "wb") as f2:
      f2.write(data)

if __name__ == "__main__":
  
  in_dir = "HP1GChogSamples"
  for fn in list_all_files(in_dir):
    if not os.path.splitext(fn)[1].lower() == ".hog":
      continue
    
    hog_ex(fn)

### EOF ###