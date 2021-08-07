#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 2020

@author: TheDrDOS

    Shows a progress bar in the console.

    Use the function progress_bar.progress_bar

    See demo with progress_bar.demo

"""

import sys

def progress_bar(n,N,decimals=1,newline_last=True,show_percentage=True,clear_bar=False):
    """
    Shows a progress bar in the console.

    Parameters
    ----------
    n : number
        progress is n/N*100%.
    N : number
        progress is n/N*100%.
    decimals : int, optional
        number of decimals. The default is 1.
    newline_last : bool, optional
        When n>=N, make a newline after the bar. The default is True.
    show_percentage : bool, optional
        Show progress in percentage also. The default is True.
    clear_bar : bool, optional
        When n>=N, clear the progress bar away. The default is False.

    Returns
    -------
    None.

    """

    done = int(50*n/N)

    if show_percentage:
        if decimals<1:
            donep =str(int(100*n/N))
        else:
            donep =("{:"+str(int(decimals+3))+"."+str(int(decimals))+"f}").format(100*n/N)
        sys.stdout.write('\r[{}{}]={}% '.format('█' * done, '.' * (50-done),donep))
    else:
        sys.stdout.write('\r[{}{}] '.format('█' * done, '.' * (50-done)))

    if done<50:
        sys.stdout.flush()
    elif clear_bar:
        sys.stdout.write('\r{} '.format( ' ' * (50+3+4+decimals+1)))
        sys.stdout.flush()
        sys.stdout.write('\r')
    elif newline_last:
        sys.stdout.write(str('\n'))


def demo():
    import time
    N = 123
    print("Start Progress Bar Demo with %")
    for k in range(0,N+1):
        progress_bar(k,N)
        time.sleep(2/N)
    print("End Progresss Bar Demo with %")

    print("Start Progress Bar Demo without %")
    for k in range(0,N+1):
        progress_bar(k,N,show_percentage=False)
        time.sleep(2/N)
    print("End Progresss Bar Demo without %")

    print("Start Progress Bar Demo with clear")
    for k in range(0,N+1):
        progress_bar(k,N,clear_bar=True)
        time.sleep(2/N)
    print("End Progresss Bar Demo with clear")

    print("Demo Complete!")

def simple_progress_bar(n,N):
    done = int(50*n/N)
    donep =int(100*n/N)
    sys.stdout.write('\r[{}{}]={}%'.format('█' * done, '.' * (50-done),donep))
    sys.stdout.flush()
