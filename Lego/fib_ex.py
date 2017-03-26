################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
import csv

from util import *
from fib_dec import fib_dec
from guess_ext import guess_ext
from platforms import *

FIB_MAGIC = "FUSE1.00"
DEFAULT_EXT = ".bin"
DEBUG = False

def fib_ex(filename, out_dir = None, platform = None):
  out_dir = out_dir or os.path.splitext(filename)[0]
  csv_file = os.path.splitext(filename)[0] + ".csv"
  
  print
  print "*" * 10, filename, "*" * 10
  print 
  
  file_names = {}
  if os.path.isfile(csv_file):
    with open(csv_file, "rb") as f:
      reader = csv.reader(f)
      
      # Not all csv files are structured the same, so handle what we know how to.
      for row in reader:
        
        # LEGO City Undercover (3DS)
        if len(row) == 5:
          hash, fn, cmp_size, dec_size, offset = row
          
        # LEGO Pirates of the Caribbean (3DS)
        # LEGO Harry Potter: Years 5-7 (3DS)
        elif len(row) == 4:
          hash, fn, dec_size, offset = row
        
        else:
          raise Exception("Unsupported CSV file.")
        
        # Some csv files have column names in the first row, some don't.
        # If we can convert the offset from base 16, it's probably legit.
        try:
          offset = int(offset, 16)
        except ValueError:
          continue
        
        file_names[offset] = fn
  
  f = BinaryFile(filename, "rb")
  fib_ex_data(f, out_dir, file_names)
  f.close()

def fib_ex_data(f, out_dir, file_names = {}, platform = None):
  
  if not f.read(8) == FIB_MAGIC:
    f.close()
    print "Invalid FIB file."
    return
  
  file_count = f.get_u32()
  unk1       = f.read(4)
  toc_offset = f.get_u32()
  
  # We have (at least) two different versions of this archive format in use.
  # Assigning arbitrary numbers based on release order, since there's
  # no way to distinguish them based on the header that I can find.
  # These are the numbers I'm using based on the games I have on hand:
  # 
  # Version 1:
  #   LEGO Harry Potter: Years 1-4 (PSP)
  #   LEGO Star Wars III: The Clone Wars (3DS/PSP)
  #   LEGO Pirates of the Caribbean (3DS)
  #   LEGO Harry Potter: Years 5-7 (3DS/PSP)
  # Version 2:
  #   The LEGO Movie Videogame (Vita)
  #   LEGO Batman 3: Beyond Gotham (3DS)
  fib_ver = 2
  
  # Table of contents, three entries each: hash, file offset, decompressed size.
  toc = []
  f.seek(toc_offset)
  for i in range(file_count):
    toc.append([f.get_u32(), f.get_u32(), f.get_u32()])
  
  # Sort by offset, rather than hash, because it's easier to debug.
  toc.sort(key = lambda x: x[1])
  
  # The PSP games are ~95% duplicated data for some bizarre reason.
  # Since we don't have filenames for them anyway, save time by
  # only taking one instance of each unique hash.
  hashes = set()
  file_list = []
  
  for i, (hash, offset, dec_size) in enumerate(toc):
    
    # Version 1 uses 0x40 as the top byte of the size for compressed files.
    # Version 2 uses the bottom five bits of the size as flags.
    # Version 1 is more distinctive, so we assume version 2 until we see 0x40.
    if dec_size >> 24 == 0x40:
      fib_ver = 1
    
    if hash in hashes:
      continue
    hashes.add(hash)
    
    # If we have a list of filenames, take the filename from there,
    # otherwise, we just give it a generic name.
    file_list.append([hash, file_names.get(offset, "%06d%s" % (i, DEFAULT_EXT)), dec_size, offset])
  
  # Little heuristic to guess the platform, since PSP games have so much duplication.
  if platform == None and file_count / len(file_list) >= 5:
    platform = PLATFORM_PSP
  
  if DEBUG:
    print file_count, len(file_list)
    f.seek(0x14)
  
  for hash, fn, dec_size, offset in file_list:
    
    if DEBUG:
      print fn
      if not offset == f.tell():
        print "    ##########"
    
    f.seek(offset)
    dec = bytearray()
    
    # Have we read all the chunks in this file?
    done = False
    
    # I'm pretty sure it's just the very bottom bit of the dec_size that says
    # whether it's compressed or not. I'm not sure what the other four do.
    if fib_ver == 2:
      cmp_flag = dec_size & 0b11111
      dec_size >>= 5
      chunk_size = 0x40000
    
    while not done:
      cmp_size = f.get_u32()
      
      # The decompressed size in the TOC is unreliable for fib v1 data,
      # so we have to rely on the compressed size, which means checking this
      # inside the loop. But v2 has to be done outside. This code is such a mess.
      if fib_ver == 1:
        cmp_flag = cmp_size >> 24
        cmp_size &= 0x00FFFFFF
        dec_size &= 0x00FFFFFF
        chunk_size = 0x8000
      
      # Compressed
      if (fib_ver == 1 and cmp_flag == 0x40) or (fib_ver == 2 and cmp_flag & 1):
        if DEBUG:
          print "    Chunk: 0x%02X 0x%08X 0x%08X 0x%08X" % (cmp_flag, f.tell() - 4, f.tell() + cmp_size, cmp_size),
        
        chunk = fib_dec(f.read(cmp_size))
        dec += chunk
        
        # Very occasionally, we'll get a file that decompresses to exactly
        # the chunk size, however, there are also files without decompressed
        # sizes listed, so we have to check both possibilities to be sure
        # we're not accidentally sticking part of the next file onto this one.
        if len(chunk) < chunk_size or len(dec) == dec_size:
          done = True
        
        if DEBUG:
          print "0x%08X" % len(chunk)
      
      # Uncompressed.
      else:
        if DEBUG:
          print "    Uncompressed: 0x%02X 0x%08X 0x%08X 0x%08X 0x%08X" % (cmp_flag, f.tell() - 4, f.tell() + dec_size, cmp_size, dec_size)
        
        # We need those first four bytes back.
        f.seek(-4, 1)
        dec = f.read(dec_size)
        done = True
    
    if DEBUG:
      if not dec_size == 0 and not dec_size == len(dec):
        print "    Size mismatch!"
      print "   ", dec_size, len(dec), len(dec) - dec_size
    
    # Keep our existing extension if we have one,
    # except images/audio, which don't use useful extensions.
    if os.path.splitext(fn)[1].lower() in [DEFAULT_EXT, ".btga", ".bpng", ".bdds", ".png", ".tga", ".wav"]:
      ext = guess_ext(dec, platform)
      if ext:
        fn = os.path.splitext(fn)[0] + ext
    
    if not DEBUG:
      print fn
    
    out_file = os.path.join(out_dir, fn)
    
    try:
      os.makedirs(os.path.dirname(out_file))
    except:
      pass
    
    with open(out_file, "wb") as out:
      out.write(dec)

if __name__ == "__main__":
  # fib_ex("LEGO Pirates of the Caribbean (3DS)/legopirates3ds.fib", "ex/legopirates3ds", platform = PLATFORM_3DS)
  # fib_ex("LEGO Harry Potter - Years 5-7 (3DS)/lego_hp2_3ds.fib", "ex/lego_hp2_3ds", platform = PLATFORM_3DS)
  fib_ex("LEGO Harry Potter - Years 1-4 (PSP)/USRDIR/legoharrypotterpsp.fib", "ex/legoharrypotterpsp")
  # fib_ex("LEGO Harry Potter - Years 5-7 (PSP)/USRDIR/lego_hp2_psp.fib", "ex/lego_hp2_psp")
  # fib_ex("LEGO Star Wars III - The Clone Wars (3DS)/legostarwarsclonewars3ds.fib", "ex/legostarwarsclonewars3ds", platform = PLATFORM_3DS)
  # fib_ex("LEGO Star Wars III - The Clone Wars (PSP)/USRDIR/legostarwarsclonewarspsp.fib", "ex/legostarwarsclonewarspsp")
  
  # fib_ex("LEGO Batman 3 - Beyond Gotham (3DS)/lego_black_hh_3ds.fib", "ex/lego_black_hh_3ds", platform = PLATFORM_3DS)
  # fib_ex("LEGO Batman 3 - Beyond Gotham (3DS)/dialogue_uk.fib", "ex/dialogue_uk", platform = PLATFORM_3DS)
  # fib_ex("LEGO Movie (Vita)/lego_emmet_psp2.fib", "ex/lego_emmet_psp2", platform = PLATFORM_VITA)
  # fib_ex("LEGO Movie (Vita)/prebuiltshaders_psp2.fib", "ex/prebuiltshaders_psp2", platform = PLATFORM_VITA)
  # fib_ex("test.fib")

### EOF ###