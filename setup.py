#!/usr/bin/env python

from setuptools import setup

setup(
    name='simbashlog-notify-helper',
    version='1.5.0',
    description='Helper for simbashlog notifiers',
    long_description='Import this Python package into your simbashlog notifier so that you only have to worry about the actual logic and no longer have to accept the arguments and co.',
    author='Fabian Fuchs',
    license='GPL-3.0-or-later',
    url='https://github.com/fuchs-fabian/simbashlog-notify-helper-py',
    keywords=['simbashlog', 'notify', 'helper', 'log'],
    platforms=['Linux'],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'simbashlog-notify-helper=simbashlog_notify_helper:process_arguments',
        ],
    },
)
