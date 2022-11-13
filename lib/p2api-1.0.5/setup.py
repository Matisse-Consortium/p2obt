from setuptools import setup

#
# HOWTO
# Set version in setup.py (this file)
# Set P2_API_VERSION in p2api.py
# python3 setup.py sdist
# twine upload dist/*
# rm -fr dist

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
try:
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except:
    ## For Python-2.7...
    with open(path.join(this_directory, 'README.md')) as f:
        long_description = f.read()

setup(
    name='p2api',
    version='1.0.5',
    description='Binding for the ESO phase 2 programmatic API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.eso.org/copdemo/apidoc/index.html',
    author='Thomas Bierwirth',
    author_email='thomas.bierwirth@eso.org',

    packages=['p2api', 'p2api/generate_finding_charts',],
    entry_points={
        'console_scripts' : [
            'p2api_generate_finding_charts = p2api.generate_finding_charts.generate_finding_charts:main',
        ],
    },

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='ESO Phase2 Observation Preparation Programmatic API',

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    py_modules=["p2api"],

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'requests',
        'keyring',
    ],
    license='MIT'
)
