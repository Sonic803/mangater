from setuptools import find_packages, setup

setup(
    name='mangater',
    packages=find_packages(include=['mangater']),
    version='1.0.0',
    install_requires=[],
        setup_requires=['pytest-runner'],
    test_suite='tests',
)