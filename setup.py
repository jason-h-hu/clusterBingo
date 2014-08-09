classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
"""

import sys
try:
    from setuptools import setup,find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

# extra_opts = {"test_suite": "tests"}

# if sys.version_info[:2] == (2, 6):
#     # Need unittest2 to run unittests in Python 2.6
#     extra_opts["tests_require"] = "unittest2"
#     extra_opts["test_suite"] = "unittest2.collector"

# try:
#     with open("README.rst", "r") as fd:
#         extra_opts['long_description'] = fd.read()
# except IOError:
#     pass        # Install without README.rst

setup(name='cluster-bingo',
      version="1.0",
      author="Jason Hu",
      author_email='jason_hu@brown.edu',
      description='A tool to automatically provision machines using puppet',
      keywords=['cluster-bingo', 'mongo', 'mongodb', 'puppet'],
      url='https://github.com/jason-h-hu/clusterBingo',
      license="http://www.apache.org/licenses/LICENSE-2.0.html",
      platforms=["any"],
      classifiers=filter(None, classifiers.split("\n")),
      install_requires=['paramiko >= 1.14.0'],
      packages= find_packages(),
      package_data={
          'bingo': ['modules', 'manifests']
      },
      entry_points={
          'console_scripts': [
              'bingo = bingo.app:main',
          ],
      },
)
