#!/home/linmiancheng/workplace/hue/build/env/bin/python2.7
# EASY-INSTALL-ENTRY-SCRIPT: 'desktop==3.7.0','console_scripts','hue'
__requires__ = 'desktop==3.7.0'
import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('desktop==3.7.0', 'console_scripts', 'hue')()
)
