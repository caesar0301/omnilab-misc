import os
import sys
from setuptools import setup, find_packages

from PyOmniMisc import __version__

setup(
    name = "PyOmniMisc",
    version = __version__,
    url = 'https://github.com/caesar0301/PyOmniMisc',
    author = 'X. Chen',
    author_email = 'chenxm35@gmail.com',
    description = 'Misc utilities written to facillitate daily data processing in OMNI-Lab, SJTU.',
    long_description=
'''
Misc utilities written to facillitate daily data processing.
''',
    license = "LICENSE",
    packages = find_packages(),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: Freely Distributable',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
   ],
)