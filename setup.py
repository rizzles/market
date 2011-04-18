#!/usr/local/bin

import os, sys, shutil
from distutils.core import setup
import py2exe
from distutils.filelist import findall
import matplotlib

mydata_files = matplotlib.get_py2exe_datafiles()
mydata_files.append('market.ico')

print 'Deleting build dirs...'
try:
    shutil.rmtree('./build')
except:
    pass
try:
    shutil.rmtree('./dist')
except:
    pass
print 'Building app...'

    
setup(
    name="Market",
    description='Market Binary',
    author="Mike Reilly",
    author_email="mike@itchycats.com",
    url="www.",
    platforms=['posix'],
    windows=[
        {
            "script": "market.py",
            "icon_resources": [(0, "market.ico")]
        }
        ],
    data_files=mydata_files,
    
    options={
        "py2exe": {
            "includes": ['PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'sip', 'matplotlib.backends', 'matplotlib.backends.backend_qt4agg', 'matplotlib.figure', 'matplotlib.backends.backend_tkagg',
                         'pylab', 'numpy',
                         "matplotlib.numerix.linear_algebra", "matplotlib.numerix.random_array",
                         "matplotlib.backends.backend_tkagg"],                         
#            "packages": ['matplotlib', 'pytz'],
#            "optimize": 2,
            "excludes": ["pywin", "pywin.debugger", "pywin.debugger.dbgcon", "pywin.dialogs",
                        '_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg',
                         '_fltkagg', '_gtk', '_gtkcairo', ],
            'dll_excludes': ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll']           
            }
        }
    )
    
