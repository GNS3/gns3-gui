#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Provide a pretty logging on console"""


import logging
import sys
import os


class ColouredFormatter(logging.Formatter):
    RESET = '\x1B[0m'
    RED = '\x1B[31m'
    YELLOW = '\x1B[33m'
    GREEN = '\x1B[32m'
    PINK = '\x1b[35m'

    def format(self, record, colour=False):

        message = super().format(record)

        if not colour or sys.platform.startswith("win"):
            return message.replace("#RESET#", "")

        level_no = record.levelno
        if level_no >= logging.CRITICAL:
            colour = self.RED
        elif level_no >= logging.ERROR:
            colour = self.RED
        elif level_no >= logging.WARNING:
            colour = self.YELLOW
        elif level_no >= logging.INFO:
            colour = self.GREEN
        elif level_no >= logging.DEBUG:
            colour = self.PINK
        else:
            colour = self.RESET

        message = message.replace("#RESET#", self.RESET)
        message = '{colour}{message}{reset}'.format(colour=colour, message=message, reset=self.RESET)

        return message


class ColouredStreamHandler(logging.StreamHandler):

    def format(self, record, colour=False):

        if not isinstance(self.formatter, ColouredFormatter):
            self.formatter = ColouredFormatter()

        return self.formatter.format(record, colour)

    def emit(self, record):

        stream = self.stream
        try:
            msg = self.format(record, stream.isatty())
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        # On OSX when frozen flush raise a BrokenPipeError
        except BrokenPipeError:
            pass
        except Exception:
            self.handleError(record)


def init_logger(level, logfile, quiet=False):
    if sys.platform.startswith("win"):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.formatter = ColouredFormatter("{asctime} {levelname} {filename}:{lineno} {message}", "%Y-%m-%d %H:%M:%S", "{")
    else:
        stream_handler = ColouredStreamHandler(sys.stdout)
        stream_handler.formatter = ColouredFormatter("{asctime} {levelname} {filename}:{lineno}#RESET# {message}", "%Y-%m-%d %H:%M:%S", "{")
    logging.basicConfig(level=level, handlers=[stream_handler])
    log = logging.getLogger()
    log.addHandler(stream_handler)

    try:
        try:
            os.makedirs(os.path.dirname(logfile))
        except FileExistsError:
            pass
        handler = logging.FileHandler(logfile, "w")
        handler.formatter = logging.Formatter("{asctime} {levelname} {filename}:{lineno} {message}", "%Y-%m-%d %H:%M:%S", "{")
        log.addHandler(handler)
    except OSError as e:
        log.warn("could not log to {}: {}".format(logfile, e))

    log.info('Log level: {}'.format(logging.getLevelName(level)))

    return logging.getLogger()
