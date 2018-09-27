#!/usr/bin/env python3

from sys import exit
from pathlib import Path
from socket import gethostname

def calculate_pi(places):
    # Adapted from user Juan Lopes' code on
    # https://stackoverflow.com/questions/28284996/python-pi-calculation
    from decimal import Decimal, getcontext

    getcontext().prec=int(places)
    pi =  sum(1/Decimal(16)**k *
             (Decimal(4)/(8*k+1) -
              Decimal(2)/(8*k+4) -
              Decimal(1)/(8*k+5) -
              Decimal(1)/(8*k+6)) for k in range(100))

    return pi


def working_at_the_coal_mine(csv):
    from random import randint
    from time import time

    places = randint(1,10**7)

    start = time()
    pi = calculate_pi(places)
    end = time()

    duration = (end - start)

    data = "{},{},{}\n".format(gethostname(),places,duration)

    with open(csv, 'a') as file:
        file.write(data)

    print(data)

    
def elect(elector):

    if elector.exists():
        # Not the first one here
        return False
    else:
        # Seize power!
        # This doesn't really mean anything at the moment
        # It's totally a figurehead status
        print("I'm assuming command")
        message = "Look at me...I'm the captain now!\n\n\t-sincerely, {}".format(gethostname())
        with open(elector, 'w') as file:
            file.write(message)

    return True
        

def main():
  # Check prereqs
  datadir = Path('/data')
  if not datadir.exists():
      print('[CRIT] - {} does not exist!'.format(datadir))
      exit(1)

  # Elect a leader (first come first served)
  elector = datadir / 'elector.txt'
  if not elect(elector):
      # Do the job
      print("I got here late - peon it is...")
      working_at_the_coal_mine(datadir / 'output.csv')

if __name__ == "__main__":
    main()
