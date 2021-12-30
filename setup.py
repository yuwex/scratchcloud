from setuptools import setup

def readme():
    with open('README.md') as fin:
        return fin.read()

packages = [
    'ScratchCloud',
    'ScratchCloud.ext',
]

setup(
    name='ScratchCloud',
    version='1.0.0',
    author='yuwex',
    url='https://github.com/yuwex/ScratchCloud',
    description='An event-based asynchronous wrapper for scratch.mit.edu cloud variables',
    long_description=readme(),
    long_description_type='text/markdown',
    install_requires=['aiohttp', 'websockets'],
    keywords=['core', 'package'],
    packages=packages,
)
