# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from platforms import *

def guess_ext(data, platform = None):
  # magic, offset, extension
  exts = [
    # fib v1 audio
    (b"\x01\x00\x00\x00\x2C\x00\x00\x00\x2C\x00\x00\x00", 0, ".bwav"),
    # fib v2 audio
    (b"\xF2\xFF\xFF\xFF\x2C\x00\x00\x00", 8, ".bwav"),
    
    # fib v1 3DS graphics / overlaps with fib v1 PSP audio
    (b"\x01\x00\x00\x00\x20\x00\x00\x00\x20\x00\x00\x00", 0, ".bwav" if platform == PLATFORM_PSP else ".btga"),
    # fib v2, LEGO Batman 3 3DS graphics
    (b"\x00\x04\x00\x00\x10\x00\x00\x00\xF2\xFF\xFF\xFF\x20\x00\x00\x00", 0, ".btga"),
    # fib v2, LEGO Movie Vita graphics
    (b"\x00\x04\x00\x00\x10\x00\x00\x00\xF2\xFF\xFF\xFF\x1C\x00\x00\x00", 0, ".btga"),
    
    # fib v1 PSP graphics
    (b"\x50\x00\x00\x00", 8, ".btga"),
    
    # Mostly guesses based on games w/ csv files
    (b"\x04\x00\x00\x00", 8, ".bxaml"),
    (b"\x08\x00\x00\x00", 8, ".bxls"), # converted xls files
    (b"\x10\x00\x00\x00", 8, ".fnskl"),
    (b"\x1C\x00\x00\x00", 8, ".fnanm"), # Used in both, overlaps w/ fnmdl
    # (b"\x1C\x00\x00\x00", 8, ".fnmdl"), # LEGO Pirates 3DS
    (b"\x24\x00\x00\x00", 8, ".fnmdl"), # LEGO HP 5-7 3DS
    (b"\x28\x00\x00\x00", 8, ".fnmdl"),
    (b"\x3C\x00\x00\x00", 8, ".lvl"),   # LEGO Pirates 3DS
    (b"\x44\x00\x00\x00", 8, ".lvl"),   # LEGO HP 5-7 3DS
    
    (b"CameraFollow", 0, ".cam"),
    (b"leCameraFollow", 0, ".cam"),
    (b"NCSC", 0, ".ncsc"),
    
    # More guesses, this time for fib v2 stuff.
    # Not sure it's safe to just use the first four bytes are enough, but w/e.
    (b"\xF0\xFF\xFF\xFF", 8, ".fnanm"),
    (b"\xF1\xFF\xFF\xFF\x38\x00\x00\x00", 8, ".lvl"),
    (b"\xF1\xFF\xFF\xFF\x3C\x00\x00\x00", 8, ".lvl"),
    (b"\xF2\xFF\xFF\xFF\x04\x00\x00\x00", 8, ".bxaml"),
    (b"\xF2\xFF\xFF\xFF\x08\x00\x00\x00", 8, ".bxls"),
    (b"\xF2\xFF\xFF\xFF\x10\x00\x00\x00", 8, ".fnskl"),
    (b"\xF2\xFF\xFF\xFF\x24\x00\x00\x00", 8, ".fnmdl"),
    (b"\xF2\xFF\xFF\xFF\x28\x00\x00\x00", 8, ".fnmdl"),
    
    (b"LOCA", 0, ".loc"),
    (b"\x31\x0D\x0A\x30\x30\x3A", 0, ".srt"),
    
    # PS Vita compiled shaders
    (b"GXP\x00\x01\x05\x50\x02", 0, ".gxp"),
    
    # Common image formats.
    (b"TRUEVISION-XFILE.", -18, ".tga"),
    (b"\x89\x50\x4E\x47", 0, ".png"),
    (b"\xFF\xD8\xFF\xDB", 0, ".jpg"),
    (b"\xFF\xD8\xFF\xE0", 0, ".jpg"),
    (b"\xFF\xD8\xFF\xE1", 0, ".jpg"),
    (b"\x42\x4D", 0, ".bmp"),
    
    # Common audio formats.
    (b"WAVE", 8, ".wav"),
    (b"OggS", 0, ".ogg"),
  ]
  
  for magic, offset, ext in exts:
    if len(data) >= offset + len(magic) and data[offset : offset + len(magic)] == magic:
      return ext
  
  return None

### EOF ###