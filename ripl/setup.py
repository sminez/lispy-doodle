import os
from setuptools import setup, find_packages

from ripl.cli import __version__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ripl',
    version=__version__,
    description="A LISP that runs on the python VM",
    url="https://github.com/sminez/ripl",
    author="Innes Anderson-Morrison",
    author_email='innes.anderson-morrison@york.ac.uk',
    install_requires=[],
    setup_requires=[
        'pytest-cov',
        'pytest-runner',
    ],
    tests_require=['pytest'],
    extras_require={'test': ['pytest']},
    packages=find_packages(),
    package_dir={'ripl': 'ripl'},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta'
    ],
    entry_points={
        'console_scripts': [
            'ripl = ripl.cli:main',
        ]
    },
)
