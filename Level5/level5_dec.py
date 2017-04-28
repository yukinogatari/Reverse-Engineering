# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *

DEBUG = False

################################################################################

# Via https://graphics.stanford.edu/~seander/bithacks.html#ReverseByteWith64BitsDiv
def bit_reverse(b):
  return (b * 0x0202020202 & 0x010884422010) % 1023

# Chain the above for a 32-bit little-endian value.
def bit_reverse32(b):
  return (bit_reverse(b[0]) << 24) | (bit_reverse(b[1]) << 16) | (bit_reverse(b[2]) << 8) | bit_reverse(b[3])

################################################################################

# Level-5 uses a handful of different compression algorithms interchangeably,
# so this figures out which one we need to use to decompress the data.
def level5_dec(data):
  
  data = bytearray(data)
  
  header   = to_u32(data[:4])
  fmt      = header & 0b111
  dec_size = header >> 3
  
  # Raw data.
  if fmt == 0:
    if DEBUG:
      print "Raw data:"
    dec = data[4 : 4 + dec_size]
  
  # RLE.
  elif fmt & 0b100:
    if DEBUG:
      print "RLE:"
    dec = rle_dec(data[4:])
  
  # Huffman.
  elif fmt & 0b010:
    if DEBUG:
      print "Huffman:"
    dec = huffman_dec(data[4:], 4 if fmt == 0b010 else 8, dec_size)
  
  # LZSS.
  elif fmt & 0b001:
    if DEBUG:
      print "LZSS:"
    dec = lzss_dec(data[4:])
  
  else:
    print "Unknown compression:", bin(fmt)
    dec = data
  
  if DEBUG:
    print "Expected size:", dec_size
    print "Actual size:  ", len(dec)
  
  return dec
  
################################################################################

def rle_dec(data):
  
  data = bytearray(data)
  res = bytearray()
  
  p = 0
  while p < len(data):
    b = data[p]
    p += 1
    
    if b < 0x80:
      count = b + 1
      res.extend(data[p : p + count])
      p += count
    
    else:
      count = b - 0x80 + 3
      res.extend([data[p]] * count)
      p += 1
  
  return res
  
################################################################################

# Standard GBA/NDS Huffman-compressed data, minus the header.
def huffman_dec(data, bits, dec_size):
    
  data = bytearray(data)
  res = bytearray()
  
  table_size = data[0] * 2 + 1
  table = data[1 : 1 + table_size]
  
  p = 1 + table_size
  off  = 0
  next = 0
  flag = 1
  bits_used = 0
  
  while len(res) < dec_size:
    if flag == 1:
      if p >= len(data):
        break
      flag = 0x100000000 | bit_reverse32(data[p : p + 4])
      p += 4
    
    next += ((table[off] & 0x3F) + 1) * 2
    
    if DEBUG:
      print flag & 1, hex(table[off]), next,
    
    ch = table[off] & (0x40 if flag & 1 else 0x80)
    off = next - 1 + (flag & 1)
    
    if DEBUG:
      print ch
    
    if ch:
      if bits_used == 0:
        res.append(0)
      
      res[-1] |= table[off] << bits_used
      
      bits_used += bits
      if bits_used >= 8:
        bits_used = 0
      
      off = next = 0
    
    flag >>= 1
  
  return res

################################################################################

# Standard GBA/NDS LZSS compressed data, minus the header.
def lzss_dec(data):
    
  data = bytearray(data)
  res = bytearray()
  
  flag = 1
  p = 0
  
  while p < len(data):
    if flag == 1:
      flag = 0x100 | bit_reverse(data[p])
      p += 1
    
    if DEBUG:
      print "[0x%08X][0x%08X]" % (p - 1, len(res)),
    
    if p >= len(data):
      break
    
    # Read from the buffer.
    # xxxxyyyy yyyyyyyy
    # Count  -> x + 3
    # Offset -> y
    if flag & 1:
      if DEBUG:
        print "Read back: 0x%02X 0x%02X" % (data[p], data[p + 1]),
      
      count  = (data[p] >> 4) + 3
      offset = ((data[p] & 0b1111) << 8) | data[p + 1]
      p += 2
      
      if DEBUG:
        print "-> Count:", count, "| Offset:", offset
      
      for i in range(count):
        res.append(res[-offset - 1])
    
    # Raw byte.
    else:
      if DEBUG:
        print "Raw: 0x%02X" % data[p]
        
      res.append(data[p])
      p += 1
    
    flag >>= 1
  
  return res

### EOF ###