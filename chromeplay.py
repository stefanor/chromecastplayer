#!/usr/bin/env python

# Copyright, 2014 Stefano Rivera.
# Distributed under the ISC license, see LICENSE.rst

import argparse
import curses
import errno
import time
import socket
import ssl

import pychromecast


def main():
    p = argparse.ArgumentParser()
    p.add_argument('URL')
    args = p.parse_args()
    play(args.URL)


def play(url):
    while True:
        try:
            cast = pychromecast.get_chromecast()
            while not cast.is_idle:
                cast.quit_app()
                time.sleep(1)

            cast.play_media(url, "video/mp4")
        except socket.error as e:
            if e.errno != errno.EFAULT:
                raise
        except ssl.SSLError as e:
            pass
        else:
            break

    control_loop(cast.media_controller)
    cast.quit_app()


def control_loop(mc):
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)

    try:
        while True:
            c = stdscr.getch()
            if c == curses.ERR:
                pass
            elif c == ord(' '):
                if mc.status.player_state == 'PAUSED':
                    mc.play()
                else:
                    mc.pause()
            elif c == ord('q'):
                mc.stop()
                break
            elif c == curses.KEY_RIGHT:
                mc.seek(mc.status.current_time + 10)
            elif c == curses.KEY_LEFT:
                mc.seek(max(mc.status.current_time - 10, 0))
            elif c == curses.KEY_UP:
                mc.seek(mc.status.current_time + 60)
            elif c == curses.KEY_DOWN:
                mc.seek(max(mc.status.current_time - 60, 0))
            elif c == curses.KEY_PPAGE:
                mc.seek(mc.status.current_time + 600)
            elif c == curses.KEY_NPAGE:
                mc.seek(max(mc.status.current_time - 600, 0))
            if mc.status:
                stdscr.addstr(0, 0, mc.status.player_state)
                stdscr.clrtoeol()
                minutes, seconds = divmod(mc.status.current_time, 60)
                hours, minutes = divmod(minutes, 60)
                stdscr.addstr(1, 0, "%02i:%02i:%02i"
                                    % (hours, minutes, seconds))
                mc.update_status()
            stdscr.move(2, 0)
            stdscr.refresh()
            time.sleep(1)
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == '__main__':
    main()
