# BlackDragonHunt's Reverse Engineering Dump

## About

A dumping ground for all the miscellaneous reverse engineering I've done. Mostly video game file formats, in large part to help [Ehm](https://twitter.com/OtherEhm) with [TCRF](https://tcrf.net/The_Cutting_Room_Floor) research, but sometimes just to satisfy my own curiosity.

There's undoubtedly stuff here (like the HyPack extractor) that other people have already reverse-engineered independently of (and more thoroughly than) me. About half of my work is driven by curiosity, so I'm not particularly concerned with whether I'm reinventing the wheel. I just wanna break stuff apart and see how it works.

Danganronpa-related scripts can be found in their own repository [here](https://github.com/BlackDragonHunt/Danganronpa-Tools).

## Disclaimer

**These are NOT tools.**

The scripts are provided as-is, for research purposes, in the interest of publicly documenting file formats used in games. (And mostly because I'm too lazy to make everything into user-friendly tools.)

Most scripts will not function without being modified to point to appropriate files. Some algorithms are incomplete or broken (I'll try to make note of where this is the case). There is very little error handling.

## Dependencies

Pretty much everything depends on some combination of the below items:

* Python 2.7 (x86)
    * <http://www.python.org/download/>
* Pillow
    * <https://python-pillow.org/>
* PyQt4
    * <http://www.riverbankcomputing.co.uk/software/pyqt/download>
* bitstring
    * <https://github.com/scott-griffiths/bitstring>