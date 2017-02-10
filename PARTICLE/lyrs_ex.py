﻿################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from util import *

LYRS_MAGIC = "GAMEDAT PAC2"

def lyrs_ex(filename, out_dir = None):
  if out_dir == None:
    out_dir = os.path.splitext(filename)[0]
  
  data = BinaryFile(filename, "rb")
  
  if not data.read(12) == LYRS_MAGIC:
    return
  
  num_files = data.get_u32()
  
  filenames = []
  toc = []
  
  for i in xrange(num_files):
    fn = data.read(32).strip("\0")
    filenames.append(fn)
  
  for i in xrange(num_files):
    offset = data.get_u32()
    length = data.get_u32()
    
    toc.append((offset, length))
  
  start = data.tell()
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  for i in xrange(num_files):
    offset, length = toc[i]
    data.seek(start + offset)
    file_data = data.read(length)
    
    out_file = os.path.join(out_dir, filenames[i])
    print out_file
    
    with open(out_file, "wb") as f:
      f.write(file_data)
  
if __name__ == "__main__":
  lyrs_ex("graphic.dat")

### EOF ###