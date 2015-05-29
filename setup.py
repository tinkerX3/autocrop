from setuptools import setup
from os import path

setup(
    name='autocrop',
    version='0.1.0',
    description='Image auto-cropper',
    long_description=open(path.join(path.abspath(path.dirname(__file__)), 'README.md')).read(),
    url='https://github.com/tinkerX3/autocrop',
    author='Tomi Pozderec',
    author_email='tomi.pozderec@gmail.com',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='content-aware image cropping',
    install_requires=[
        'Pillow',
        'numpy',
        'scikit-image'
    ],
    entry_points={
        'console_scripts': [
            'autocrop=autocrop:main',
        ],
    },
)
