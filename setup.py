from setuptools import setup

setup(
    name='match-courses',
    version='0.1.0',
    py_modules=['match', 'update'],
    install_requires=[
        'Click', 'python-Levenshtein', 'thefuzz'
    ],
    entry_points={
        'console_scripts': [
            'match = match:match',
            'update = match:update'
        ],
    },
)
