#!/usr/bin/python3

import os

def clear_term():
    os.system('cls' if os.name == 'nt' else 'clear')
