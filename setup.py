from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='pychecktext',
   version='0.0.1',
   description='Check gettext tokens',
   license="MIT",
   long_description=long_description,
   author='Doug Addy',
   author_email='da1910@protonmail.com',
   url="https://github.com/da1910/pyCheckText",
   packages=['pychecktext'],  #same as name
   install_requires=[], #external packages as dependencies
   scripts=[
            'scripts/checktext.py',
           ]
)