"""
Main ETL Class for the entire ETL process for converting EDSM and Spansh data into custom binary format for C++ routing engine

"""


import os
import io
import ijson
import json
import requests
import pprint
import struct
import gzip
import psutil
import resource
from datetime import datetime
from pathlib import Path

from ..common.utils import here

class ETLProcessor:
    def __init__(self):
        print(f"Beginning ETL Process...\n")