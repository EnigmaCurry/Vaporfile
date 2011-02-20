from setuptools import setup, find_packages
import os
import glob

import vaporfile
            
setup(name='Vaporfile',
      version=vaporfile.__version__,
      description='A tool to upload static websites to the Amazon S3 cloud',
      author='Ryan McGuire',
      author_email='ryan@enigmacurry.com',
      url='http://www.enigmacurry.com',
      license='MIT',
      packages=["vaporfile"],
      install_requires =["boto>=2.0b4"],
      entry_points="""
      [console_scripts]
      vaporfile = vaporfile.main:main
      """
      )
