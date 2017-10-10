#coding:utf8
from setuptools import setup, find_packages

setup(name='icewarp',
      version='1.0',
      description='IceWarp api',
      author='apuyuseng',
      author_email='1173372284@qq.com',
      url='https://github.com/Apuyuseng/icewarp',
      packages=find_packages(),
      install_requires=[
            "python-wordpress-xmlrpc==2.3"
      ]
      )
