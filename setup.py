#!/usr/bin/env python
""" Setup file for Magritte
Reference:
https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
"""
import os
import re
import sys
from setuptools import setup, find_packages
from pip.req import parse_requirements

__version__ = "1.3.1"
README_FILENAME = "README.rst"
REQUIREMENTS = {
    'prod': "requirements.txt",
    'dev': "requirements-dev.txt"
}


def get_version(package):
    """ Return package version as listed in `__version__` in `init.py`. """
    with open(os.path.join(package, '__init__.py'), 'rb') as init_py:
        src = init_py.read().decode('utf-8')
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", src).group(1)


def parse_reqs(filename):
    """ parse setup requirements from a requirements.txt file """
    install_reqs = parse_requirements(filename, session=False)
    return [str(ir.req) for ir in install_reqs]

req_list = parse_reqs(REQUIREMENTS['prod'])
if len(sys.argv) > 2 and sys.argv[2] == ('develop'):
    req_list += parse_reqs(REQUIREMENTS['dev'])


with open(README_FILENAME, 'r') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

setup(
    name='magritte',
    version=get_version('magritte'),
    description='Optimize image files and comic archives with external tools',
    author='AJ Slater',
    author_email='aj@slater.net',
    url='https://github.com/ajslater/magritte/',
    py_modules=['magritte'],
    install_requires=req_list,
    entry_points={
        'console_scripts': [
            'magritte=magritte.cli:main'
        ]
    },
    long_description=LONG_DESCRIPTION,
    license="GPLv2",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Archiving :: Mirroring',
        'Topic :: Utilities'
    ],
    packages=find_packages(),
    test_suite='magritte.tests',
)
