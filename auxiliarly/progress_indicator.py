#!/usr/bin/python3

import sys


class ProgressIndicator():
    symbols = ['-', '\\', '|', '/']

    def __init__(self, after='', lajust=1):
        self.symbol = 0
        self.after = after
        self.lajust = lajust

    def call(self):
        sys.stdout.flush()
        sys.stdout.write(self.after + ' ' * self.lajust + self.symbols[self.symbol%len(self.symbols)])
        sys.stdout.write('\r')

        self.symbol += 1

    def end(self):
        sys.stdout.write('\n')

    def reset(self):
        self.symbol = 0
