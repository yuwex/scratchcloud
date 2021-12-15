from setuptools import setup

def readme():
    with open('README.md') as fin:
        return fin.read()

packages = [
    'scratchcloud',
    'scratchcloud.ext',
]

setup(
    name='scratchcloudpy',
    version='1.0.0',
    author='yuwex',
    url='https://github.com/yuwex/scratchcloud',
    description='An asynchronous wrapper for scratch.mit.edu cloud variables',
    long_description=readme(),
    long_description_type='text/markdown',
    install_requires=['aiohttp', 'requests', 'websockets'],
    keywords=['core', 'package'],
    packages=packages,
)