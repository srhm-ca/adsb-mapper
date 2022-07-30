# adsb-cmap

A basic ADS-B visualizer written in Python3. Needs a live [dump1090](https://github.com/antirez/dump1090) server serving a .json over the local network (or internet), and your current position in latitude and longitude.

## How to run:

1. Run `dump1090 --net --aggressive` (or run `adsb-cmap` with `-d` pointed towards the `dump1090` bin)
2. Run `python src/adsb-cmap.py --lat 45 --lon -80`
3. Wait for the map to appear - the program waits for data from `dump1090` before displaying
4. Zoom in and out with `+` and `-`, quit with `q`
