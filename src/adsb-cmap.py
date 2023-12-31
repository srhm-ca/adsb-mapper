#!/usr/bin/env python3
import os
import sys
import json
import time
import math
import curses
import argparse
import subprocess
import urllib.request


def get_arg():
    """Get args from the CLI"""
    parser = argparse.ArgumentParser(description="Track planes with net-mode" +
                                     " dump1090. Increase and decrease range" +
                                     " with - and +. Quit with q. adsb-cmap" +
                                     " can start dump109 by passing" +
                                     " the dump1090 executable"
                                     " path with -d, otherwise pass the" +
                                     " .json url with --url.")
    parser.add_argument("-x", "--lat",
                        type=float,
                        help="latitude",
                        dest="lat")
    parser.add_argument("-y", "--lon",
                        type=float,
                        help="longitude",
                        dest="lon")
    parser.add_argument("-r", "--range",
                        type=float,
                        help="range in degrees, default = 0.2",
                        default=0.2,
                        dest="deg")
    parser.add_argument("-u", "--url",
                        type=str,
                        help="server-hosted dump1090 .json",
                        default="http://localhost:8080/data.json",
                        dest="url")
    parser.add_argument("-d", "--dump1090",
                        type=str,
                        help="path to dump1090 binary",
                        dest="dumpbin")
    parser.add_argument("-n", "--nolog",
                        help="delete log file",
                        action='store_false',
                        dest='log')
    parser.add_argument("-s", "--square",
                        help="force square aspect ratio",
                        action="store_true",
                        dest='square')
    args = parser.parse_args()
    return args


def get_state():
    """Get latest data.json from net-mode dump1090"""
    try:
        with urllib.request.urlopen(args.url) as path:
            data = json.loads(path.read().decode())
            return data
    except urllib.error.URLError:
        print("Error: source unavailable.")
        exit_gracefully()


def start_window():
    """Initialize curses and return window object"""
    stdscr = curses.initscr()
    curses.cbreak()
    curses.curs_set(0)
    curses.echo(False)
    rows, cols = stdscr.getmaxyx()
    window = curses.newwin(rows, cols, 0, 0)
    window.nodelay(True)
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
    return abs(lat) * 110.574


def conv_lon(lat, lon):
    """Convert a given longitude into kilometres"""
    return (abs(lon)) * (111.320 * math.cos(math.radians(lat)))


def calc_distance(lat, lon, lat1, lon1):
    """Calculate the distance between two points in kilometres"""
    x = abs(conv_lat(lat) - conv_lat(lat1))
    y = abs(conv_lon(lat, lon) - conv_lon(lat1, lon1))
    return ((y ** 2) + (x ** 2)) ** 0.5


def calc_viewbox(lat, lon, deg):
    """Return approximate viewing range in kilometres given lat/lon co-ords"""
    viewbox = []
    viewbox.append(abs((conv_lat(lat - deg) - conv_lat(lat + deg))))
    viewbox.append(abs(conv_lon(lat, lon - deg) - conv_lon(lat, lon + deg)))
    return viewbox


def check(x, deg):
    """Verify and return viewing range"""
    return x - deg, x + deg


def exit_gracefully():
    """Revert curses settings before exiting"""
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    curses.curs_set(1)
    if args.dumpbin:
        print("Killing dump1090")
        process.kill()
        if not args.log:
            subprocess.run(f"rm {t}.log", shell=True)
    sys.exit()


def write_map(window, state, lat, lon, deg):
    """Write map to screen given latest dump1090 data"""
    rows, cols = stdscr.getmaxyx()
    if args.square:
        if cols > rows:
            cols = rows
        else:
            rows = cols
    viewbox = calc_viewbox(lat, lon, deg)
    planes = "plane" if len(state) == 1 else "planes"
    try:
        window.addstr(int(rows / 2),
                      int(cols / 2), "o")
        window.addstr(int(rows / 2), 2,
                      str(int(viewbox[0])) + " KM")
        window.addstr(int(rows - 2), int(cols / 2),
                      str(int(viewbox[1])) + " KM")
        window.addstr(int(rows - 2), int(cols-20),
                      str(len(state)) + f" {planes} detected")
        for i in range(rows - 1):
            window.addstr(i, 0, ".")
        for i in range(cols - 1):
            window.addstr(int(rows - 1), i, ".")
    except curses.error:
        pass

    for ent in state:
        try:
            x = conv_linear((check(lat, deg)),
                            (-abs(rows), 0), float(ent["lat"]))
            y = conv_linear((check(lon, deg)),
                            (0, cols), float(ent["lon"]))
            window.addstr(abs(int(x)), int(y),
                          "x")
            window.addstr(abs(int(x - 1)), int(y),
                          str(ent["flight"]))
            window.addstr(abs(int(x - 2)), int(y),
                          str(int(calc_distance(float(ent["lat"]),
                                                float(ent["lon"]),
                                                lat, lon)))
                          + " KM")
        except curses.error:
            pass


if __name__ == "__main__":
    args = get_arg()
    if args.dumpbin:
        print("Starting dump1090")
        t = time.time()
        process = subprocess.Popen(f"{args.dumpbin} --net --aggressive",
                                   shell=True,
                                   stdout=open(f"{t}.log", "w"),
                                   close_fds=True)
        print("Waiting for dump1090")
        while True:
            if os.stat(f"{t}.log").st_size > 10:
                break
    window, stdscr = start_window()
    while True:
        try:
            if (ch := window.getch()) != -1:
                if ch in [113, 81]:
                    exit_gracefully()
                elif ch == 45:
                    args.deg += 0.1
                elif ch == 43 and args.deg > 0.2:
                    args.deg -= 0.1
            state = get_state()
            update_window(state, window, args)
            time.sleep(0.05)
        except KeyboardInterrupt:
            exit_gracefully()
