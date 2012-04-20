from setuptools import setup, find_packages

DESCRIPTION = "Python Library for rendering BBCode."

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

VERSION = '0.1.0'

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(name='bbcodepy',
    version=VERSION,
    packages=find_packages(),
    author='Stanislav Vishnevskiy',
    author_email='vishnevskiy@gmail.com',
    url='https://github.com/vishnevskiy/bbcodepy',
    license='MIT',
    include_package_data=True,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    test_suite='tests',
)
