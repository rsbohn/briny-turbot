#remidi.py
#2021-05-16
import math
import random

note = range(21,108)
freq = [2**((i-68)/12)*440 for i in note]
def octave(n):
    if not n in note:
        raise IndexError("invalid note")
    return (n-21)//12

def frequency(n):
    if not n in note:
        raise IndexError("invalid note")
    return freq[n-21]

def major(n):
    return [n,n+2,n+4,n+5, n+7,n+9,n+11,n+12]
def natural(n):
    return [n,n+2,n+3,n+5, n+7,n+8,n+10,n+12]
def harmonic(n):
    return [n,n+2,n+3,n+5, n+7,n+8,n+11,n+12]
