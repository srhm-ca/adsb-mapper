#!/usr/bin/env python3
import urllib.request
import json
import argparse
import curses
import time
import sys


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
    rows, cols = stdscr.getmaxyx()
    window = curses.newwin(rows, cols, 0, 0)
    return window, stdscr


def scale_pos(a, b, s):
    """Generic function for scaling coordinates"""
    (a1, a2), (b1, b2) = a, b
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def check(x, deg):
    """Verify and return the requested viewing range"""
    return x-deg, x+deg


def exit_gracefully():
    """Revert curses settings before exiting"""
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    sys.exit()


def write_map(window, state, lat, lon, deg):
    """Write to screen an ASCII map based on the latest JSON data"""
    rows, cols = stdscr.getmaxyx()
    window.addstr(int(rows/2), int(cols/2), "o")
    for ent in state:
        x = scale_pos((check(lat, deg)), (-abs(rows), 0), float(ent["lat"]))
        y = scale_pos((check(lon, deg)), (0, cols), float(ent["lon"]))
        window.addstr(abs(int(x)),
                      int(y),
                      "x")


def update_window(state, window, args):
    """Update the curses window"""
    window.clear()
    if curses.is_term_resized:
        rows, cols = stdscr.getmaxyx()
        window.resize(rows, cols)
    write_map(window, state, args.lat, args.lon, args.deg)
    window.refresh()


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
