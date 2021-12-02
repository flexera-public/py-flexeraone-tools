from setuptools import setup

test_deps = [
    'coverage',
    'pytest',
    'pylint',
    'flake8',
    'autopep8',
    'pytest-flake8',
    'pytest-mypy'
]

dev_deps = [

]

extras = {
    'test': test_deps,
    'dev': dev_deps
}
readme = open('README.md', 'r+')

setup(
    name="py_flexeraone_tools",
    version="0.0.1",
    author="Flexera",
    author_email="support@flexera.com",
    description=("A collection of tools to work with the FlexeraOne APIs"),
    license_files=('LICENSE'),
    keywords="",
    url="https://github.com/flexera/py-flexeraone-tools",
    long_description=readme.read(),
    classifiers=[],
    # Other metadata...
    tests_require=test_deps,
    extras_require=extras,
)
