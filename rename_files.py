# -*- coding: utf-8 -*-
r"""
Created on Tue Feb  6 15:23:56 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu

Purpose:
    for all files found in "files_loc":
        replace part of file name "remv_str" with "repl_str".

Special Requirements:
    none.
"""
import os
import sys
from pathlib import Path as makePath



files_loc = makePath("D:/PROGRAMMING/debugging/py_rename")
remv_str = "GHG"
repl_str = "WTF"



if not os.path.exists(files_loc):
    sys.exit("directory not found.")

allfiles = os.listdir(files_loc)

for file in allfiles:
    if file.find(remv_str) is not -1:
        print("renaming: "+os.path.basename(file))
        os.rename(files_loc / file,
                  files_loc / file.replace(remv_str, repl_str))
    else:
        print("skipped: "+os.path.basename(file))
