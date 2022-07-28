A basic ADS-B visualizer written in Python3. Needs a live [dump1090](https://github.com/antirez/dump1090) server serving a .json over the local network (or internet), and your current position in latitude and longitude.

How to run:

1. Run `dump1090 --net --aggressive`
2. Run `python src/adsb-cmap.py --lat 45 --lon -80` or use pypy3
