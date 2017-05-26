# -*- coding: utf-8 -*-
import math

def dot(p1, p2):
    return p1.real*p2.real + p1.imag*p2.imag

def cross(p1, p2):
    return p1.real*p2.imag - p1.imag*p2.real

def dotLineDist(p, line):
    "line: (p1, p2)"
    a, b = line
    if dot(b-a, p-a) <= 0.0:
        return (a, abs(p-a))
        # return abs(p-a)
    if dot(a-b, p-b) <= 0.0:
        return (b, abs(p-b))
        # return abs(p-b)
    vec = (b-a) / abs(b-a)
    norm_vec = vec.imag - vec.real * 1j
    distance_h = cross(b-a, p-a)/abs(b-a)
    p_vec = norm_vec * distance_h
    return (p + p_vec, distance_h)
    # return abs(cross(b-a, p-a))/abs(b-a)

"""
点から線分への距離を算出する
"""
if __name__ == "__main__":
    line = (10+10j, 25+40j)
    print (dotLineDist(55+0j, line))