# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 14:16:33 2018

@author: ARIR
"""
import os

def findFile(location = None, key_word = "Completed"):
    
    file_names = os.listdir(location)
    
    matches = [s for s in file_names if key_word in s]
    return matches


if __name__ == "__main__":
    
    key_file = os.listdir()[0]
    print("Looking for: '" + key_file + "'")
    
    print("Found file is: '" + findFile(key_word=key_file)[0] + "'")
