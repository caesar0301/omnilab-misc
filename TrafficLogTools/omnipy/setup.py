from setuptools import setup, find_packages

from omnipy import __version__

setup(
    name = "omnipy",
    version = __version__,
    url = 'https://github.com/caesar0301/omnipy',
    author = 'X. Chen',
    author_email = 'chenxm35@gmail.com',
    packages = find_packages(),
    install_requires = ['treelib', 'tldextract', 'pyyaml'],
    data_files = [('', ['omnipy/db/intds.yaml', 'omnipy/db/ndpi-proto.csv'])],
    description = 'My misc python library in daily data processing.',
    license = "GPLv3",
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
   ]
)
