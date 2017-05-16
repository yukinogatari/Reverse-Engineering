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

PAC2_MAGIC = "GAMEDAT PAC2"

def pac2_ex(filename, out_dir = None):
  
  out_dir = out_dir or os.path.splitext(filename)[0]
  
  with BinaryFile(filename, "rb") as data:
    if not data.read(12) == PAC2_MAGIC:
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
  pac2_ex("archive-lilycle.dat")
  pac2_ex("graphic-lilycle.dat")
  pac2_ex("archive-taisho.dat")
  pac2_ex("graphic-taisho.dat")

### EOF ###