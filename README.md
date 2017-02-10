# BlackDragonHunt's Reverse Engineering Dump

## About

A dumping ground for all the miscellaneous reverse engineering I've done. Mostly video game file formats, largely to help [Ehm](https://twitter.com/OtherEhm) with [TCRF](https://tcrf.net/The_Cutting_Room_Floor) research, but sometimes just to satisfy my own curiosity.

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