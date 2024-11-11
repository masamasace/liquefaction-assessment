import os
from pathlib import Path
import lxml.etree as ET

file_path = r"misc/example.xml"

parser = ET.XMLParser(encoding="shift-jis")

tree = ET.parse(file_path, parser=parser)
