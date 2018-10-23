# -*- coding: utf-8 -*-
from setuptools import setup
version = '0.0.1'
repo = 'WikidataFish'

setup(
    name='WikidataFish',
    packages=['wikidatafish'],
    install_requires=[
        'pywikibot==3.0-dev',
        'mwparserfromhell'
    ],
    dependency_links=[
        'git+https://github.com/lokal-profil/wikidata-stuff/tarball/master#egg=wikidatastuff-0.3.9',
        'git+https://github.com/wikimedia/pywikibot-core.git#egg=pywikibot-3.0-dev'

    ],
    version=version,
    description='A library for importing data to Wikidata.',
    url='https://github.com/Vesihiisi/' + repo,
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ],
    author='André Costa, Alicia Fagerving',
    author_email='alicia.fagerving@wikimedia.se',
    download_url='https://github.com/Vesihiisi/' + repo + '/tarball/' + version,
)
