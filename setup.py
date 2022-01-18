from setuptools import setup

def readme():
    with open('README.md') as fin:
        return fin.read()

install_requires = [
    'aiohttp>=3.8.0',
    'websockets>=10.1'
]

packages = [
    'scratchcloud',
    'scratchcloud.ext',
]

extras_require = {
    'docs': [
        'sphinx==4.3.2',
        'sphinx-rtd-theme==1.0.0',
    ]
}

setup(
    name='scratchcloud',
    version='0.0.1',
    author='yuwex',
    url='https://github.com/yuwex/scratchcloud',
    description='An event-based asynchronous wrapper for scratch.mit.edu cloud variables.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires='>=3.8.0',
    packages=packages,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Education',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries'
    ]
)
