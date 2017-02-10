# Erogos

Extracts and converts data used in animated eroge developed by [Erogos](https://vndb.org/p351).

`erogos_dat.py` handles extracting the games' dat files, with the relevant decryption keys (where known) available in `erogos_keys.py`.

`erogos_img.py` handles conversion of the games' graphic data (.cg and .ani files).

## Games Tested

* Love Fetish 1-10
* Mahotama 1-6

## Notes

The .ani conversion code naively assumes frames are presented linearly, which isn't always the case, so a small percentage of exported frame data will be incorrect if frames are composed. I could never be bothered to figure out how to properly determine the correct frame order.

Exporting all the data will take a VERY long time.