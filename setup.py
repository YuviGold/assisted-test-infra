#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name='discovery_infra',
    packages=['discovery_infra'],
    entry_points = {
        'console_scripts': [
            'test_infra=discovery_infra.start_discovery:main'
        ],
    }
)

