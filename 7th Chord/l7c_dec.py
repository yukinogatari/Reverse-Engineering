################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

from util import *

DEBUG = False

################################################################################

# Full files with compression have a small header indicating their size.
def l7c_dec_file(filename):
  with open(filename, "rb") as f:
    data = bytearray(f.read())
  return l7c_dec_file_data(data)

def l7c_dec_file_data(data):
  
  # Compressed.
  if data[0] == 0x19:
    dec_size = to_u32(data[1:4] + bytearray(1))
    ret = data[4:]
    
    # If it throws an error trying to decompress, it's probably not compressed,
    # so we'll ignore the error and send it back as we got it.
    try:
      ret = l7c_dec(ret)
      
      # If the dec size doesn't match what we expected, it's also probably not
      # compressed data, so again, send it back as we got it.
      if not len(ret) == dec_size:
        ret = data
        
    except:
      ret = data
  
  # Uncompressed. idk either
  elif data[0] == 0x18:
    data_size = to_u32(data[1:4] + bytearray(1))
    ret = data[4 : 4 + data_size]
  
  else:
    ret = data
  
  return ret

################################################################################

def l7c_dec(data):
  
  res = bytearray()
  p = 0
  
  while p < len(data):
    
    b = data[p]
    p += 1
  
    bit1 = b & 0b10000000
    bit2 = b & 0b01000000
    
    # Raw bytes from input.
    # 00xxxxxx
    # 00000000 1xxxxxxx
    # 00000000 0xxxxxxx xxxxxxxx
    # Read below for details...
    if not bit1 and not bit2:
      
      if DEBUG:
        print "[0x%04X, 0x%06X]" % (p - 1, len(res)), "Raw bytes:", "%02X" % b,
      
      # If we're zero, we want MORE.
      if b == 0x00:
        b2 = data[p]
        p += 1
        
        if DEBUG:
          print "%02X" % b2,
        
        # If bit1 isn't set, we want EVEN MORE.
        if not b2 & 0b10000000:
          b3 = data[p]
          p += 1
          
          # Three zeroes in a row (probably?) means we're out of data.
          if b2 == 0x00 and b3 == 0x00:
            break
          
          if DEBUG:
            print "%02X" % b3,
          
          # What the fuck even is this compression scheme.
          count = (b2 << 8) + b3 + 191
        
        # If bit2 IS set, we un-set it and leave bit1 set.
        elif b2 & 0b01000000:
          count = b2 & 0b10111111
        
        # And if bit2 ISN'T set, we set it and un-set bit1.
        else:
          count = b2 ^ 0b11000000
      
      else:
        count = b
        
      if count == 0:
        break
      
      if DEBUG:
        print
        for x in data[p : p + count]: print "%02X" % (x),
        print
        print
      
      res += data[p : p + count]
      p += count
    
    # Copy data from the output.
    # 01xxyyyy
    # Count  -> x + 2
    # Offset -> y + 1
    elif not bit1 and bit2:
      count = ((b & 0b00110000) >> 4) + 2
      offset = (b & 0b00001111) + 1
      
      if DEBUG:
        print "[0x%04X, 0x%06X]" % (p - 1, len(res)), "Copy back:", "%02X" % b, "|", count, offset
      
      for i in range(count):
        res.append(res[-offset])
        
        if DEBUG:
          print "%02X" % (res[-1]),
          
      if DEBUG:
        print
        print
    
    # Copy more data from the output.
    # 10xxxxyy yyyyyyyy
    # Count  -> x + 3
    # Offset -> y + 1
    elif bit1 and not bit2:
      b2 = data[p]
      p += 1
      
      count  = ((b & 0b00111100) >> 2) + 3
      offset = ((b & 0b00000011) << 8) + b2 + 1
      
      if DEBUG:
        print "[0x%04X, 0x%06X]" % (p - 1, len(res)), "Copy more back:", "%02X" % b, "%02X" % b2, "|", count, offset
      
      for i in range(count):
        res.append(res[-offset])
        
        if DEBUG:
          print "%02X" % (res[-1]),
          
      if DEBUG:
        print
        print
    
    # Copy EVEN MORE data from the output.
    # 11xxxxxx xyyyyyyy yyyyyyy
    # Count  -> x + 4
    # Offset -> y + 1
    elif bit1 and bit2:
      b2 = data[p]
      b3 = data[p + 1]
      p += 2
      
      count  = ((b & 0b00111111) << 1) + (b2 >> 7) + 4
      offset = ((b2 & 0b01111111) << 8) + b3 + 1
      
      if DEBUG:
        print "[0x%04X, 0x%06X]" % (p - 1, len(res)), "Copy lots back:", "%02X" % b, "%02X" % b2, "%02X" % b3, "|", count, offset
      
      for i in range(count):
        res.append(res[-offset])
        
        if DEBUG:
          print "%02X" % (res[-1]),
          
      if DEBUG:
        print
        print
  
  return res

### EOF ###