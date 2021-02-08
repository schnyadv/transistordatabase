#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup_requirements = []

test_requirements = []

setup(
    author="LEA - Uni Paderborn",
    author_email='upblea@mail.upb.de',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Environment :: MacOS X'
    ],
    description="Transistor Database",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='Transtor Database',
    name='transistor_database',
    packages=find_packages(include=['transistor_database', 'transistor_database.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    extras_require={},
    url='https://github.com/upb-lea/Transistor_Database',
    project_urls={
        "Documentation": "https://github.com/upb-lea/Transistor_Database",
        "Source Code": "https://github.com/upb-lea/Transistor_Database",
    },
    version='0.1.0',
    zip_safe=False,
)