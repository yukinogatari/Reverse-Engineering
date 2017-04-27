# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from PIL import Image

from util import *
from swizzle import PostProcessMortonUnswizzle

from nis_dec import nis_dec

def fad_ex(filename, out_dir):
  with open(filename, "rb") as f:
    data = bytearray(f.read())
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  num_anims1 = to_u32(data[0:4])
  num_anims2 = to_u32(data[4:8])
  num_imgs   = to_u32(data[8:12])
  unk2       = to_u32(data[12:16])
  unk3       = to_u32(data[16:20])
  unk4       = to_u32(data[20:24])
  header_len = to_u32(data[24:28])
  unk5       = to_u32(data[28:32])
  
  num_anims = num_anims1 + num_anims2
  
  print num_anims1, num_anims2, num_imgs, unk2, unk3, unk4, header_len, unk5
  
  anims = []
  imgs  = []
  
  for i in range(num_anims):
    p = (i + 1) * 0x20
    entry = data[p : p + 0x20]
    
    name      = entry[0:8].decode("UTF-8").strip("\0")
    length    = to_u32(entry[8:12])
    anim_type = to_u32(entry[12:16])
    offset    = to_u32(entry[16:20])
    
    anims.append((name, length, anim_type, offset))
  
  for i in range(num_imgs):
    p = (i + num_anims + 1) * 0x20
    entry = data[p : p + 0x20]
    
    name      = entry[0:8].decode("UTF-8").strip("\0")
    length    = to_u32(entry[8:12])
    unk6      = to_u32(entry[12:16])
    offset    = to_u32(entry[16:20])
    
    imgs.append((name, length, offset))
  
  for i, (name, length, anim_type, offset) in enumerate(anims):
    entry = data[offset : offset + length]
    
    # Who doesn't love a little redundancy.
    name2      = entry[0:8].decode("UTF-8").strip("\0")
    length2    = to_u32(entry[8:12])
    anim_type2 = to_u32(entry[12:16])
    
    # Only seems to have actual text if anim_type == 1
    name3      = entry[16:24].decode("UTF-8").strip("\0")
    
    # print "  ", name, length, anim_type
    # print "  ", name2, length2, anim_type2
    # print "  ", name3
    # print
    out_file = "anim_%04d_%s.dat" % (i, name)
    out_file = os.path.join(out_dir, out_file)
    
    with open(out_file, "wb") as f:
      f.write(entry)
  
  for i, (name, length, offset) in enumerate(imgs):
    
    entry = data[offset : offset + length]
    
    # Who doesn't love a little redundancy.
    name2       = entry[0:8].decode("UTF-8").strip("\0")
    length2     = to_u32(entry[8:12])
    anim_type2  = to_u32(entry[12:16])
    
    cmp_size    = to_u32(entry[16:20])
    dec_size    = to_u32(entry[20:24])
    width       = to_u16(entry[24:26])
    height      = to_u16(entry[26:28])
    pal_entries = to_u16(entry[28:30])
    bpp         = entry[30]
    swizzled    = entry[31]
    
    if width == 0 or height == 0:
      continue
    
    img_data = nis_dec(entry[0x30:])
    
    out_file = ("img_%04d_%s" % (i, name)) if name else ("img_%04d" % i)
    out_file = os.path.join(out_dir, out_file)
    
    print out_file
    
    palette = []
    mode    = "RGBA"
    decoder = None
    arg     = None
    
    if pal_entries:
      for k in range(pal_entries):
        p = k * 4
        palette.append([img_data[p], img_data[p + 1], img_data[p + 2], img_data[p + 3]])
      img_data = img_data[pal_entries * 4:]
    
    if bpp == 32:
      decoder = "raw"
      arg     = "BGRA"
      
      if swizzled:
        img_data = PostProcessMortonUnswizzle(img_data, width, height, 4)
    
    elif palette:
      # PIL doesn't like palettes with alpha channels, so apply the palette here.
      decoder = "raw"
      arg     = "BGRA"
      
      old_img_data = img_data
      img_data = bytearray()
      
      if bpp == 4:
        for p in old_img_data:
          img_data.extend(palette[p >> 4])
          img_data.extend(palette[p & 0x0F])
      
      else:
        for p in old_img_data:
          img_data.extend(palette[p])
      
      if swizzled:
        img_data = PostProcessMortonUnswizzle(img_data, width, height, 4)
    
    elif bpp == 4 or bpp == 8:
      
      if bpp == 4:
        decoder = "bcn"
        arg     = 1
        bytespp = 8
      
      elif bpp == 8:
        decoder = "bcn"
        arg     = 3
        bytespp = 16
      
      if swizzled and width >= 4 and height >= 4:
        img_data = PostProcessMortonUnswizzle(img_data, width / 4, height / 4, bytespp)
    
    img = Image.frombytes(mode, (width, height), bytes(img_data), decoder, arg)
    img.save(out_file + ".png")

if __name__ == "__main__":
  
  base_dir = "data/anime"
  for i, fn in enumerate(os.listdir(base_dir)):
    if not i == 9:
      continue
    in_file  = os.path.join(base_dir, fn)
    out_file = os.path.join("data-dec/anime", fn)
    fad_ex(in_file, out_file)

### EOF ###