# -*- coding:utf-8 -*-
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup

VERSION = '1.0.6'

AUTHOR = "cn"

AUTHOR_EMAIL = "308299269@qq.com"

URL = "https://github.com/ShichaoMa/translate_html"

NAME = "translate-html"

DESCRIPTION = "translate html to chinese without tag. "
try:
    LONG_DESCRIPTION = open("README.rst").read()
except UnicodeDecodeError:
    LONG_DESCRIPTION = open("README.rst", encoding="utf-8").read()

KEYWORDS = "translate html chinese tag"

LICENSE = "MIT"

MODULES = ["translate"]

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'translate = translate:main',
        ],
    },
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    py_modules = MODULES,
    install_requires=["requests"],
    include_package_data=True,
    zip_safe=True,
)