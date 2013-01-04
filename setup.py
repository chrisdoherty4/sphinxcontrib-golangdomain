# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the sphinxcontrib-golangdomain Sphinx extension.

This extension adds Ruby Domain to Sphinx.
It needs Sphinx 1.0 or newer.
'''

requires = ['Sphinx>=1.0']

setup(
    name='sphinxcontrib-golangdomain',
    version='0.1.3',
    url='http://bitbucket.org/ymotongpoo/sphinxcontrib-golangdomain',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-golangdomain',
    license='BSD',
    author='Yoshifumi YAMAGUCHI',
    author_email='ymotongpoo at gmail.com',
    description='Sphinx extension sphinxcontrib-golangdomain',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
