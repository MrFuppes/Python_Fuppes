# -*- coding: utf-8 -*-
r"""
Created on Thu Dec 20 11:18:46 2018

@author:
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    access: 2018-12-20
"""

# Print iterations progress
def printProgressBar(iteration, total,
                     prefix='', suffix='',
                     decimals=1, length=100,
                     fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    progBar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, progBar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print('\n')
##
## Sample Usage
##
#
#from time import sleep
#
## A List of Items
#items = list(range(0, 57))
#l = len(items)
#
## Initial call to print 0% progress
#printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
#for i, item in enumerate(items):
#    # Do stuff...
#    sleep(0.1)
#    # Update Progress Bar
#    printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
