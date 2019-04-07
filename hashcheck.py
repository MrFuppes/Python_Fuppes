# -*- coding: utf-8 -*-
r"""
Created on Mon Jan 14 10:27:28 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import hashlib

file = "C:/Users/va6504/Downloads/openvpn-connect-2.6.0.100_signed.msi"
tgt_hash = "4151ce95d4086afb71d70dbe124111d8352f9d8f4e1fe35be2e51e8bb5fe4995"

h = hashlib.sha256()

with open(file, "rb") as f:
    for byte_block in iter(lambda: f.read(4096), b""):
        h.update(byte_block)
    print("hash is:", h.hexdigest())

if tgt_hash:
    if h.hexdigest() == tgt_hash:
        print("hash equal to target.")
    else:
        print("hashes not equal!")
