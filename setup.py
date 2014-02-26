import os
from setuptools import setup, find_packages

# get documentation from the README
try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.md')).read()
except (OSError, IOError):
    description = ''

# version number
version = {}
execfile(os.path.join('hlakit', 'version.py'), version)

# dependencies
deps = ['ply==3.4']

setup(name='hlakit',
      version=version['__version__'],
      description="Multi-target High Level Assembler",
      long_description=description,
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='assembler, retro, games',
      author='Dave Huseby',
      author_email='dave@linuxprogrammer.org',
      url='https://wookie.github.io/hlakit',
      license='BSD-2-Clause',
      packages=['hlakit','hlakit.cpus','hlakit.families','hlakit.platforms','hlakit.targets'],
      zip_safe=False,
      entry_points={'console_scripts': [
          'hlakit = hlakit.hlakit:main']},
      install_requires=deps,
      test_suite='tests')
