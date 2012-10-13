from distutils.core import setup
import py2exe
import UnRAR2
import os, glob, sys

options = { "py2exe":
            {   "compressed" : 1,
                "optimize" : 2,
                "bundle_files" : 1
            }
          }

setup(console=["extractor.py"], options=options, zipfile=None)

# move UnRAR2's dll to Mac OSX's bundle directory
