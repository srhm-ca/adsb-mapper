#!/usr/bin/env python3
import urllib.request
import json
import argparse
import curses
import time
import sys
import math


def get_arg():
    """Get args from the CLI"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--lat',
                        type=float,
                        help='current latitude',
                        dest='lat')
    parser.add_argument('--lon',
                        type=float,
                        help='current longitude',
                        dest='lon')
    parser.add_argument('--range',
                        type=float,
                        help='range in degrees',
                        dest='deg')
    args = parser.parse_args()
    return args


def get_state():
    """Get latest data.json from local net-mode Dump1090"""
    try:
        with urllib.request.urlopen("http://localhost:8080/data.json") as path:
            data = json.loads(path.read().decode())
            return data
    except urllib.error.URLError:
        print("Error: source unavailable.")
        exit_gracefully()


def start_window():
    """Initialize curses instance and return window"""
    stdscr = curses.initscr()
    curses.cbreak()
    curses.curs_set(0)
    rows, cols = stdscr.getmaxyx()
    window = curses.newwin(rows, cols, 0, 0)
    return window, stdscr


def update_window(state, window, args):
    """Update the curses window"""
    window.clear()
    if curses.is_term_resized:
        rows, cols = stdscr.getmaxyx()
        window.resize(rows, cols)
    write_map(window, state, args.lat, args.lon, args.deg)
    window.refresh()


def conv_linear(a, b, s):
    """Generic function for scaling coordinates"""
    (a1, a2), (b1, b2) = a, b
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def conv_lat(lat):
    """Convert a given latitude into kilometres"""
    return abs(lat)*110.574


def conv_lon(lat, lon):
    """Convert a given longitude into kilometres"""
    return (abs(lon))*(111.320*math.cos(math.radians(lat)))


def calc_distance(lat, lon, lat1, lon1):
    """Calculate the distance between two points in kilometres"""
    x = abs(conv_lat(lat)-conv_lat(lat1))
    y = abs(conv_lon(lat, lon) - conv_lon(lat1, lon1))
    return ((y**2) + (x**2))**0.5


def calc_viewbox(lat, lon, deg):
    """Return approximate viewing range in kilometres given lat/lon co-ords"""
    viewbox = []
    viewbox.append(abs((conv_lat(lat - deg) - conv_lat(lat + deg))))
    viewbox.append(abs(conv_lon(lat, lon - deg) - conv_lon(lat, lon + deg)))
    return viewbox


def check(x, deg):
    """Verify and return the requested viewing range"""
    return x-deg, x+deg


def exit_gracefully():
    """Revert curses settings before exiting"""
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    curses.curs_set(1)
    sys.exit()


def write_map(window, state, lat, lon, deg):
    """Write to screen an ASCII map based on the latest JSON data"""
    rows, cols = stdscr.getmaxyx()
    viewbox = calc_viewbox(lat, lon, deg)
    window.addstr(int(rows/2), int(cols/2), "o")
    window.addstr(int(rows/2), 2, str(int(viewbox[0])) + " KM")
    window.addstr(int(rows-2), int(cols/2), str(int(viewbox[1])) + " KM")
    for i in range(rows-1):
        window.addstr(i, 0, ".")
    for i in range(cols-1):
        window.addstr(int(rows-1), i, ".")

    for ent in state:
        x = conv_linear((check(lat, deg)), (-abs(rows), 0), float(ent["lat"]))
        y = conv_linear((check(lon, deg)), (0, cols), float(ent["lon"]))
        window.addstr(abs(int(x)),
                      int(y),
                      "x")
        window.addstr(abs(int(x-1)),
                      int(y),
                      str(ent["flight"]))
        window.addstr(abs(int(x-2)),
                      int(y),
                      str(int(calc_distance(float(ent["lat"]),
                                            float(ent["lon"]),
                                            lat, lon))) + " KM")


if __name__ == '__main__':
    window, stdscr = start_window()
    args = get_arg()
    while True:
        try:
            state = (get_state())
            update_window(state, window, args)
            time.sleep(0.05)
        except KeyboardInterrupt:
            exit_gracefully()
