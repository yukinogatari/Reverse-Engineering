# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import os
import math

from util import *
from l7c_dec import l7c_dec, l7c_dec_file_data

DEBUG = False

################################################################################

def get_name(table, offset):
  length = table[offset]
  return unicode(table[offset + 1 : offset + length + 1])

def l7c_ex(filename, out_dir = None):
  if not out_dir:
    out_dir = os.path.splitext(filename)[0]
  
  f = BinaryFile(filename, "rb")
  
  magic = f.read(4)
  if not magic == "L7CA":
    return
  
  unk1        = f.get_u32()
  filesize    = f.get_u32()
  toc_off     = f.get_u32()
  toc_len     = f.get_u32()
  unk2        = f.get_u32()
  toc_entr    = f.get_u32()
  dir_count   = f.get_u32()
  file_count  = f.get_u32()
  chunk_count = f.get_u32()
  names_len   = f.get_u32()
  unk7        = f.get_u32()
  
  if DEBUG:
    print unk1, filesize, toc_off, toc_len, unk2, toc_entr, dir_count, file_count, chunk_count, names_len, unk7
  
  f.seek(toc_off)
  
  file_data = []
  dir_data  = []
  
  for i in range(toc_entr):
    file_id = f.get_s32()
    unk1    = f.get_u32()
    dir_off = f.get_u32()
    fn_off  = f.get_u32()
    unk2    = f.get_u32()
    unk3    = f.get_u32()
    
    # Directory.
    if file_id == -1:
      dir_data.append(dir_off)
    
    # File.
    else:
      file_data.append([file_id, dir_off, fn_off])
    
    if DEBUG:
      print "%10d | %10d | %10d | %10d | %10d | %10d" % (file_id, unk1, dir_off, fn_off, unk2, unk3)
    # print file_id, unk1, unk2, unk3
  
  if not len(dir_data) == dir_count:
    print "Warning: Expected", dir_count, "directories, found", len(dir_data)
  
  if not len(file_data) == file_count:
    print "Warning: Expected", file_count, "files, found", len(file_data)
  
  if DEBUG:
    print
    print "*" * 80
    print
  
  # This might not work if file IDs aren't sequential?
  for i in range(file_count):
    cmp_size    = f.get_u32()
    dec_size    = f.get_u32()
    first_chunk = f.get_u32()
    num_chunks  = f.get_u32()
    offset      = f.get_u32()
    unk3        = f.get_u32()
    
    file_data[i].extend([cmp_size, dec_size, offset, first_chunk, num_chunks, unk3])
    
    if DEBUG:
      print "%10d | %10d | %10d | %10d | %10d | %10d" % (cmp_size, dec_size, unk1, unk2, offset, unk3)
  
  chunk_list = [(f.get_u32(), f.get_u32()) for i in range(chunk_count)]
  name_table = bytearray(f.read(names_len))
  
  # Create our directory structure.
  for dir_off in dir_data:
    dir_name = get_name(name_table, dir_off)
    try:
      os.makedirs(os.path.join(out_dir, dir_name))
    except:
      pass
  
  for file_id, dir_off, fn_off, cmp_size, dec_size, offset, first_chunk, num_chunks, unk3 in file_data:
    dir_name  = get_name(name_table, dir_off)
    file_name = get_name(name_table, fn_off)
    
    out_file = os.path.join(out_dir, dir_name, file_name)
    print out_file
    
    f.seek(offset)
    dec = bytearray()
    
    for chunk_num, (chunk_size, total_size) in enumerate(chunk_list[first_chunk : first_chunk + num_chunks]):
      
      # Compressed chunk.
      compressed = False
      if 0x80000000 & chunk_size:
        chunk_size ^= 0x80000000
        compressed = True
      
      data = f.read(chunk_size)
      if compressed:
        data = l7c_dec(bytearray(data))
      dec += data
    
    # Compressed file.
    if dec[0] == 0x19 or dec[0] == 0x18:
      dec = l7c_dec_file_data(dec)
    
    with open(out_file, "wb") as out:
      out.write(dec)

################################################################################

if __name__ == "__main__":
  
  l7c_ex("data_release.l7c", "test")

### EOF ###