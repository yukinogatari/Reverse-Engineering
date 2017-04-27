# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import numpy
import math

from erogos_keys import *
from util import *

PACK_MAGIC = "pack"

################################################################################

def erogos_dat_ex(filename, out_dir = None, xor_key = None):
  f = BinaryFile(filename, "rb")
  
  if out_dir is None:
    out_dir = os.path.splitext(filename)[0]
  
  if not f.read(4) == PACK_MAGIC:
    print "Not a valid pack file."
    return
  
  count = f.get_u16()
  files = []
  
  for i in range(count):
    filename = f.read(0x10).strip("\x00").decode("CP932")
    offset   = f.get_u32()
    length   = f.get_u32()
    
    files.append((filename, offset, length))
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  for filename, offset, length in files:
    print filename
    filename = os.path.join(out_dir, filename)
    
    f.seek(offset)
    data = f.read(length)
    
    if xor_key:
      data = xor_data(data, xor_key)
    
    with open(filename, "wb") as out:
      out.write(data)
  
  f.close()

################################################################################

def xor_data(data, xor_key):
  key = xor_key * (len(data) / len(xor_key) + 1)
  key = key[:len(data)]
  data = numpy.bitwise_xor(bytearray(data), key)
  return data

################################################################################

if __name__ == "__main__":
  erogos_dat_ex("!maho1/mov.dat", "maho1-ex/mov", xor_key = M1_MOV_KEY)
  # erogos_dat_ex("!maho2/mov.dat", "maho2-ex/mov", xor_key = M2_MOV_KEY)
  # erogos_dat_ex("!maho3/mov.dat", "maho3-ex/mov", xor_key = M3_MOV_KEY)
  # erogos_dat_ex("!maho4/mov.dat", "maho4-ex/mov", xor_key = M4_MOV_KEY)
  # erogos_dat_ex("!maho5/mov.dat", "maho5-ex/mov", xor_key = M5_MOV_KEY)
  # erogos_dat_ex("!maho6/mov.dat", "maho6-ex/mov", xor_key = M6_MOV_KEY)
  # erogos_dat_ex("!maho6/af.dat", "maho6-ex/af", xor_key = M6_MOV_XOR)
  # erogos_dat_ex("!lf1/mov.dat", "lf1-ex/mov", xor_key = None)
  # erogos_dat_ex("!lf2/mov.dat", "lf2-ex/mov", xor_key = None)
  # erogos_dat_ex("!lf3/mov.dat", "lf3-ex/mov", xor_key = None)
  # erogos_dat_ex("!lf4/mov.dat", "lf4-ex/mov", xor_key = None)
  # erogos_dat_ex("!lf5/mov.dat", "lf5-ex/mov", xor_key = None)
  # erogos_dat_ex("!lf6/mov.dat", "lf6-ex/mov", xor_key = None)
  # erogos_dat_ex("!lf7-1/mov.dat",-1 "lf7/mov", xor_key = None)
  # erogos_dat_ex("!lf7-2/mov.dat",-2 "lf7/mov", xor_key = None)
  # erogos_dat_ex("!lf7-3/mov.dat",-3 "lf7/mov", xor_key = None)
  # erogos_dat_ex("!lf7-4/mov.dat",-4 "lf7/mov", xor_key = None)
  # erogos_dat_ex("!lf7-5/mov.dat",-5 "lf7/mov", xor_key = None)
  # erogos_dat_ex("!lf7-6/mov.dat",-6 "lf7/mov", xor_key = None)
  # erogos_dat_ex("!lf8/mov.dat", "lf8-ex/mov", xor_key = None)
  # erogos_dat_ex("!lf9/mov.dat", "lf9-ex/mov", xor_key = LF9_MOV_KEY)
  # erogos_dat_ex("!lf10/mov.dat", "lf10-ex/mov", xor_key = LF10_MOV_KEY)
  
  erogos_dat_ex("!maho1/bg.dat", "maho1-ex/bg", xor_key = M1_BG_KEY)
  # erogos_dat_ex("!maho2/bg.dat", "maho2-ex/bg", xor_key = M2_BG_KEY)
  # erogos_dat_ex("!maho3/bg.dat", "maho3-ex/bg", xor_key = M3_BG_KEY)
  # erogos_dat_ex("!maho4/bg.dat", "maho4-ex/bg", xor_key = M4_BG_KEY)
  # erogos_dat_ex("!maho5/bg.dat", "maho5-ex/bg", xor_key = M5_BG_KEY)
  # erogos_dat_ex("!maho6/bg.dat", "maho6-ex/bg", xor_key = M6_BG_KEY)
  # erogos_dat_ex("!lf1/bg.dat", "lf1-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf2/bg.dat", "lf2-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf3/bg.dat", "lf3-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf4/bg.dat", "lf4-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf5/bg.dat", "lf5-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf6/bg.dat", "lf6-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf7-1/bg.dat", "lf7-1-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf7-2/bg.dat", "lf7-2-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf7-3/bg.dat", "lf7-3-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf7-4/bg.dat", "lf7-4-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf7-5/bg.dat", "lf7-5-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf7-6/bg.dat", "lf7-6-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf8/bg.dat", "lf8-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf9/bg.dat", "lf9-ex/bg", xor_key = None)
  # erogos_dat_ex("!lf10/bg.dat", "lf10-ex/bg", xor_key = LF10_BG_KEY)
  
  erogos_dat_ex("!maho1/bgm.dat", "maho1-ex/bgm", xor_key = None)
  # erogos_dat_ex("!maho2/bgm.dat", "maho2-ex/bgm", xor_key = None)
  # erogos_dat_ex("!maho3/bgm.dat", "maho3-ex/bgm", xor_key = None)
  # erogos_dat_ex("!maho4/bgm.dat", "maho4-ex/bgm", xor_key = None)
  # erogos_dat_ex("!maho5/bgm.dat", "maho5-ex/bgm", xor_key = None)
  # erogos_dat_ex("!maho6/bgm.dat", "maho6-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf1/bgm.dat", "lf1-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf2/bgm.dat", "lf2-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf3/bgm.dat", "lf3-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf4/bgm.dat", "lf4-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf5/bgm.dat", "lf5-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf6/bgm.dat", "lf6-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf7-1/bgm.dat", "lf7-1-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf7-2/bgm.dat", "lf7-2-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf7-3/bgm.dat", "lf7-3-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf7-4/bgm.dat", "lf7-4-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf7-5/bgm.dat", "lf7-5-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf7-6/bgm.dat", "lf7-6-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf8/bgm.dat", "lf8-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf9/bgm.dat", "lf9-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf9/bgm.dat", "lf9-ex/bgm", xor_key = None)
  # erogos_dat_ex("!lf10/bgm.dat", "lf10-ex/bgm", xor_key = None)
  
  erogos_dat_ex("!maho1/script.dat", "maho1-ex/script", xor_key = M1_SCR_KEY)
  # erogos_dat_ex("!maho2/script.dat", "maho2-ex/script", xor_key = M2_SCR_KEY)
  # erogos_dat_ex("!maho3/script.dat", "maho3-ex/script", xor_key = M3_SCR_KEY)
  # erogos_dat_ex("!maho4/script.dat", "maho4-ex/script", xor_key = M4_SCR_KEY)
  # erogos_dat_ex("!maho5/script.dat", "maho5-ex/script", xor_key = M5_SCR_KEY)
  # erogos_dat_ex("!maho6/script.dat", "maho6-ex/script", xor_key = M1_SCR_KEY)
  # erogos_dat_ex("!lf1/script.dat", "lf1-ex/script", xor_key = None)
  # erogos_dat_ex("!lf2/script.dat", "lf2-ex/script", xor_key = None)
  # erogos_dat_ex("!lf3/script.dat", "lf3-ex/script", xor_key = None)
  # erogos_dat_ex("!lf4/script.dat", "lf4-ex/script", xor_key = None)
  # erogos_dat_ex("!lf5/script.dat", "lf5-ex/script", xor_key = None)
  # erogos_dat_ex("!lf6/script.dat", "lf6-ex/script", xor_key = None)
  # erogos_dat_ex("!lf7-1/script.dat", "lf7-1-ex/script", xor_key = None)
  # erogos_dat_ex("!lf7-2/script.dat", "lf7-2-ex/script", xor_key = None)
  # erogos_dat_ex("!lf7-3/script.dat", "lf7-3-ex/script", xor_key = None)
  # erogos_dat_ex("!lf7-4/script.dat", "lf7-4-ex/script", xor_key = None)
  # erogos_dat_ex("!lf7-5/script.dat", "lf7-5-ex/script", xor_key = None)
  # erogos_dat_ex("!lf7-6/script.dat", "lf7-6-ex/script", xor_key = None)
  # erogos_dat_ex("!lf8/script.dat", "lf8-ex/script", xor_key = None)
  # erogos_dat_ex("!lf9/script.dat", "lf9-ex/script", xor_key = LF9_MOV_KEY)
  # erogos_dat_ex("!lf9/script.dat", "lf9-ex/script", xor_key = LF9_SCR_KEY)
  # erogos_dat_ex("!lf10/script.dat", "lf10-ex/script", xor_key = LF10_SCR_KEY)
  
  erogos_dat_ex("!maho1/voice.dat", "maho1-ex/voice", xor_key = None)
  # erogos_dat_ex("!maho2/voice.dat", "maho2-ex/voice", xor_key = None)
  # erogos_dat_ex("!maho3/voice.dat", "maho3-ex/voice", xor_key = None)
  # erogos_dat_ex("!maho4/voice.dat", "maho4-ex/voice", xor_key = None)
  # erogos_dat_ex("!maho5/voice.dat", "maho5-ex/voice", xor_key = None)
  # erogos_dat_ex("!maho6/voice.dat", "maho6-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf1/voice.dat", "lf1-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf2/voice.dat", "lf2-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf3/voice.dat", "lf3-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf4/voice.dat", "lf4-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf5/voice.dat", "lf5-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf6/voice.dat", "lf6-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf7-1/voice.dat", "lf7-1-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf7-2/voice.dat", "lf7-2-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf7-3/voice.dat", "lf7-3-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf7-4/voice.dat", "lf7-4-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf7-5/voice.dat", "lf7-5-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf7-6/voice.dat", "lf7-6-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf8/voice.dat", "lf8-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf9/voice.dat", "lf9-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf9/voice.dat", "lf9-ex/voice", xor_key = None)
  # erogos_dat_ex("!lf10/voice.dat", "lf10-ex/voice", xor_key = None)

### EOF ###