# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
import re
import cPickle as pickle

from collections import defaultdict

from util import *
from p5_table import TRANSLATION_TABLE

################################################################################

BF_MAGIC   = "FLW0"
BMD_MAGIC1 = "\x07\x00"
BMD_MAGIC2 = "1GSM"
FTD_MAGIC  = "FTD0"

INCLUDE_COMMANDS = True

DUMP = {}

################################################################################

def dump_messages(msgs, out_file):
  if not msgs:
    return
  
  try:
    os.makedirs(os.path.dirname(out_file))
  except:
    pass
  
  DUMP[out_file] = msgs
  
  with open(out_file, "wb") as f:
    for i, (msg_type, name, strs) in enumerate(msgs):
      f.write("------------------------------------------------------------------------\n")
      f.write("ID:%d(%s)\n\n" % (i, name))
      
      if not INCLUDE_COMMANDS:
        strs = [re.sub(r"\{.*?\}", "", string) for string in strs]
      
      strs = [str(string.strip("\n")) for string in strs]
      string = "\n\n".join(strs)
      string = string.decode("CP932", errors = "replace")
      string = string.encode("UTF-8")
      
      f.write(string)
      f.write("\n")

################################################################################

def pak_dump_file(filename, out_dir = None):
  out_dir = out_dir or os.path.splitext(filename)[0]
  
  f = BinaryFile(filename, "rb")
  pak_dump(f, out_dir)
  f.close()

def bf_dump_file(filename, out_file = None):
  out_file = out_file or os.path.splitext(filename)[0] + ".txt"
  
  f = BinaryFile(filename, "rb")
  msgs = bf_dump(f)
  f.close()
  
  dump_messages(msgs, out_file)

def bmd_dump_file(filename, out_file = None):
  out_file = out_file or os.path.splitext(filename)[0] + ".txt"
  
  f = BinaryFile(filename, "rb")
  msgs = bmd_dump(f)
  f.close()
  
  dump_messages(msgs, out_file)

################################################################################

def pak_dump(f, out_dir):
  
  # Store our data size for sanity checking.
  pos = f.tell()
  f.seek(0, 2)
  data_size = f.tell()
  f.seek(pos)
  
  # Do some header checks since we have multiple different data types that use
  # the same extensions.
  peek = f.read(4)
  f.seek(-4, 1)
  
  # Camera data, don't care.
  if peek == "ECM\x01":
    return
  
  # If it looks like a little-endian value, it's probably something else.
  elif peek[3] == "\x00":
    return
  
  # This is hacky as fuck, but take care of some annoying bin files...
  elif peek[:2] == "\x21\x03" or peek[:2] == "\x22\x03":
    return
  
  # We have two types pak data in use, which are intermingled seemingly at
  # random. What I'm calling the "compact" format has a file count at the start,
  # filenames have a limit of 0x20 bytes, and stores data size useing big endian.
  # The other type has no file count, uses 0xFC bytes for filenames, stores the
  # data size in little endian, and aligns entries to multiples of 0x40.
  # Because why the fuck not.
  # 
  # Assuming there are no paks with > 16777215 files in them, a pak with a null
  # byte at the start can be safely considered compact.
  compact = peek[0] == "\x00"
  
  if compact:
    file_count = f.get_u32be()
  
  # Ignore the file count because only non-compact paks have it.
  while True:
    
    fn_len = 0x20 if compact else 0xFC
    filename = f.read(fn_len).strip("\x00")
    
    if not filename:# or f.tell() + 4 > data_size:
      break
    
    # wtf
    filesize = f.get_u32be() if compact else f.get_u32()
    
    if f.tell() + filesize > data_size or filesize == 0:
      break
    
    data = f.get_bin(filesize)
    
    # Align to nearest multiple of 0x40, but only if not compact.
    if not compact:
      pos = f.tell()
      if pos % 0x40:
        pos = pos + 0x40 - (pos % 0x40)
      f.seek(pos)
    
    out_file = os.path.join(out_dir, filename)
    out_file = os.path.normpath(out_file)
    ext = os.path.splitext(out_file)[1].lower()
    
    if ext == ".bf":
      msgs = bf_dump(data)
    elif ext == ".bmd":
      msgs = bmd_dump(data)
    elif ext == ".ftd":
      msgs = ftd_dump(data)
    elif ext in [".pak", ".pac", ".bin"]:
      print out_file
      subdir = os.path.splitext(out_file)[0]
      pak_dump(data, subdir)
      continue
    else:
      continue
    
    print " ->", out_file
    dump_messages(msgs, out_file + ".txt")

################################################################################

def ftd_dump(f):
  unk = f.read(4)
  if not f.read(4) == FTD_MAGIC:
    print "Invalid FTD data."
    return []
  
  data_size = f.get_u32be()
  ftd_type  = f.get_u16be()
  msg_count = f.get_u16be()
  msgs = []
  
  if ftd_type == 0x00:
    header_off = f.get_u32be()
    f.seek(header_off)
    
    unk       = f.get_u32be()
    data_size = f.get_u32be()
    msg_count = f.get_u32be()
    unk2      = f.get_u32be()
    
    if msg_count == 0:
      return []
    
    length = data_size / msg_count
    
    for i in range(msg_count):
      msg = parse_str(f.read(length), has_cmd = False)
      if msg:
        msgs.append((None, str(i), [msg]))
  
  elif ftd_type == 0x01:
    msg_offs = []
    for i in range(msg_count):
      msg_offs.append(f.get_u32be())
    
    for i, off in enumerate(msg_offs):
      f.seek(off)
      length = f.get_u8()
      unk    = f.get_u8() # Always 1?
      unk2   = f.get_u16() # Always 0?
      msg    = parse_str(f.read(length), has_cmd = False)
      if msg:
        msgs.append((None, str(i), [msg]))
  
  return msgs

################################################################################

def bf_dump(f):
  unk = f.read(4)
  data_size = f.get_u32be()
  
  if not f.read(4) == BF_MAGIC:
    print "Invalid BF data."
    return []
  
  unk2 = f.get_u32be()
  tbl_count = f.get_u32be()
  unk3 = f.get_u32be()
  unk4 = f.get_u32be()
  unk4 = f.get_u32be()
  
  bmd_data = None
  
  for i in range(tbl_count):
    tbl = f.get_u32be()
    unk = f.get_u32be()
    length = f.get_u32be()
    offset = f.get_u32be()
    
    # 3 is the BMD data, which is all we care about.
    if not tbl == 3:
      continue
    
    if length == 0:
      continue
    
    f.seek(offset)
    bmd_data = f.get_bin(length)
    break
  
  if bmd_data:
    return bmd_dump(bmd_data)
  else:
    return []

################################################################################

def bmd_dump(f):
  
  if not f.read(2) == BMD_MAGIC1:
    print "Invalid BMD data."
    return []
  
  unk = f.get_u16be()
  data_size = f.get_u32be()
  
  if not f.read(4) == BMD_MAGIC2:
    print "Invalid BMD magic."
    return []
  
  unk2 = f.get_u32be()
  unk3 = f.get_u32be()
  unk4 = f.get_u32be()
  msg_count = f.get_u32be()
  unk5 = f.get_u32be()
  
  msg_tbl = []
  for i in range(msg_count):
    msg_type = f.get_u32be()
    msg_off  = f.get_u32be() + 0x20
    msg_tbl.append((msg_type, msg_off))
  
  msgs = []
  for msg_type, msg_off in msg_tbl:
    f.seek(msg_off)
    name = f.read(24).strip("\x00")
    
    # Regular dialogue
    if msg_type == 0:
      count   = f.get_u16be()
      msg_unk = f.get_u16be()
    
    # Choices
    elif msg_type == 1:
      msg_unk  = f.get_u16be()
      count    = f.get_u16be()
      msg_unk2 = f.get_u32be()
    
    else:
      print "Unknown message type!", msg_type
      continue
    
    if count == 0:
      continue
    
    str_offs = []
    for i in range(count):
      str_offs.append(f.get_u32be() + 0x20)
    
    length = f.get_u32be()
    data_end = f.tell() + length
    
    for i in range(count):
      if i == count - 1:
        end = data_end
      else:
        end = str_offs[i + 1]
      
      off = str_offs[i]
      str_offs[i] = (off, end - off)
    
    strs = []
    for off, str_len in str_offs:
      f.seek(off)
      parsed = parse_str(f.read(str_len))
      if parsed:
        strs.append(parsed)
    
    if strs:
      msgs.append((msg_type, name, strs))
  
  return msgs

################################################################################

UNMAPPED = defaultdict(int)
CHAR_COUNT = 0

def parse_str(bytes, has_cmd = True):
  global CHAR_COUNT
  
  bytes = bytearray(bytes)
  out = bytearray()
  
  p = 0
  while p < len(bytes):
    b = bytes[p]
    p += 1
    
    # Command.
    if b >= 0xF0 and has_cmd:
      num_params = ((b & 0x0F) - 1) << 1
      params = bytes[p + 1 : p + num_params + 1]
      p += num_params + 1
      
      if INCLUDE_COMMANDS:
        cmd = "{func 0x%02X" % b
        if params:
          params = ["0x%02X" % param for param in params]
          params = ", ".join(params)
          params = ": " + params
        cmd = cmd + params + "}"
        out.extend(cmd)
    
    # If it's a control character (excluding line breaks and shit)
    # it's probably data instead of text, so get out.
    elif b in range(0x09) + range(0x0E, 0x20):
      break
    
    else:
      if b >= 0x80 and p < len(bytes):
        b2 = bytes[p]
        p += 1
        char = (b, b2)
        
        if char in TRANSLATION_TABLE:
          char = TRANSLATION_TABLE[char]
        else:
          UNMAPPED[char] += 1
          # print " * Unmapped: 0x%02X, 0x%02X" % char
        
        out.extend(char)
      
      else:
        out.append(b)
      
      CHAR_COUNT += 1
  
  return out

################################################################################

def merge_scripts():
  
  with open("p5jp.dat", "rb") as f:
    jp_data = pickle.load(f)
  
  with open("p5us.dat", "rb") as f:
    en_data = pickle.load(f)
  
  merged = {}
  out_dir = "p5merged/bare"
  
  for jp_fn in jp_data:
    en_fn = jp_fn.replace("p5jp", "p5us")
    base  = jp_fn[9:]
    
    print base
    
    jp = jp_data.get(jp_fn, [])
    en = en_data.get(en_fn, [])
    
    msgs = []
    
    for i, (msg_type, name, strs) in enumerate(jp):
      for j, (en_type, en_name, en_strs) in enumerate(en):
        if en_name == name:
          del en[j]
          break
        else:
          en_name = None
          en_strs = []
      
      msgs.append([msg_type, name, ["[JP]"] + strs])
      if name == en_name:
        msgs[-1][-1].append("[EN]")
        msgs[-1][-1].extend(en_strs)
    
    # Get any leftover English text.
    for msg_type, name, strs in en:
      msgs.append([msg_type, name, ["[EN]"] + strs])
    
    out_file = os.path.join(out_dir, base)
    
    dump_messages(msgs, out_file)

################################################################################

import operator

if __name__ == "__main__":
  INCLUDE_COMMANDS = False
  
  # merge_scripts()
  # exit()
  
  # in_dir = "p5us"
  # out_dir = "p5us-out"
  in_dir = "p5jp"
  out_dir = "p5jp-out"
  
  for fn in list_all_files(in_dir):
    out_file = fn[len(in_dir) + 1:]
    out_file = os.path.join(out_dir, out_file)
    out_file = os.path.splitext(out_file)[0]
    
    ext = os.path.splitext(fn)[1].lower()
    
    if not ext in [".bf", ".bmd", ".pak", ".pac", ".bin"]:
      continue
    
    print fn
    
    if ext == ".bf":
      bf_dump_file(fn, out_file + ext + ".txt")
    if ext == ".bmd":
      bmd_dump_file(fn, out_file + ext + ".txt")
    if ext in [".pak", ".pac", ".bin"]:
      pak_dump_file(fn, out_file)
  
  # unmapped = 0
  # with open("unmapped.txt", "wb") as f:
  #   for char, count in sorted(UNMAPPED.items(), key = operator.itemgetter(1), reverse = True):
  #     f.write("%d: 0x%02X, 0x%02X" % (count, char[0], char[1]))
  #     f.write("\n")
  #     unmapped += count
  
  # print "Total character count:", CHAR_COUNT
  # print "Total unmapped characters:", unmapped
  
  # with open(in_dir + ".dat", "wb") as f:
  #   pickle.dump(DUMP, f, pickle.HIGHEST_PROTOCOL)

### EOF ###