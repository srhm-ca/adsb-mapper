#!/usr/bin/env python3
import urllib.request
import json
import argparse
import curses
import time
import sys


def getarg():
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
    parser.add_argument('--url',
                        type=str,
                        help='dump1090 address',
                        dest='url')
    parser.add_argument('--range',
                        type=float,
                        help='range in degrees',
                        dest='degrees')
    args = parser.parse_args()
    return args


def getstate(url):
    """Get latest data.json from net-mode Dump1090"""
    with urllib.request.urlopen("http://localhost:8080/data.json") as source:
        data = json.loads(source.read().decode())
        return data


def start_window():
    """Initialize curses instance and return window"""
    stdscr = curses.initscr()
    curses.cbreak()
    rows, cols = stdscr.getmaxyx()
    window = curses.newwin(rows, cols, 0, 0)
    return window, stdscr


def maprange(a, b, s):
    """Generic function for mapping a range"""
    (a1, a2), (b1, b2) = a, b
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def write_map(window, state, lat, lon, degrees):
    """Write to screen an ASCII map based on the latest JSON data"""
    rows, cols = stdscr.getmaxyx()
    row = maprange((lat-degrees, lat+degrees), (-abs(rows), 0), lat)
    col = maprange((lon-degrees, lon+degrees), (0, cols), lon)
    window.addstr(abs(int(row)), int(col), "o")

    for entry in state:
        row = maprange((lat-degrees, lat+degrees), (-abs(rows), 0), float(entry["lat"]))
        col = maprange((lon-degrees, lon+degrees), (0, cols), float(entry["lon"]))
        window.addstr(abs(int(row)),
                      int(col),
                      "x")


def update_window(state, window, args):
    """Update the curses window"""
    window.clear()
    if curses.is_term_resized:
        rows, cols = stdscr.getmaxyx()
        window.resize(rows, cols)
    write_map(window, state, args.lat, args.lon, args.degrees)
    window.refresh()


if __name__ == '__main__':
    window, stdscr = start_window()
    args = getarg()
    while True:
        try:
            state = (getstate(args.url))
            update_window(state, window, args)
            time.sleep(0.1)
        except KeyboardInterrupt:
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            sys.exit()
