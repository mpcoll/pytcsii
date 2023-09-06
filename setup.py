from setuptools import setup

setup(
    name='pyexample',
    version='0.1.0',    
    description='A Python package for the QST TCS II stimulator',
    url='https://github.com/mpcoll/pytcsii',
    author='Michel-Pierre Coll',
    author_email='michel-pierre.coll@psy.ulaval.ca',
    license='BSD 2-clause',
    packages=['pytcsii'],
    install_requires=[
                      'numpy',
                      'pyserial',
                      'matplotlib'

                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        

    ],
)