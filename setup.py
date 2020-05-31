#!/usr/bin/env python

from distutils.core import setup

setup(name='spoddit',
      version='0.2',
      description='A reddit scraper for managing spotify playlists',
      long_description='A reddit scraper for managing spotify playlists',
      author='Christoph Spörk',
      author_email='christoph.spoerk@gmail.com',
      maintainer='Christoph Spörk',
      maintainer_email='christoph.spoerk@gmail.com',
      url='https://github.com/DarwinsBuddy/spoddit',
      py_modules=[
          'spoddit',
          'spoddit.util',
          'spoddit.extractor',
          'spoddit.spotify',
          'spoddit.reddit'
      ],
      packages=['spoddit'],
      package_dir={'spoddit': 'src/spoddit'},
      install_requires=[
        'certifi',
        'chardet',
        'configparser',
        'idna',
        'pafy',
        'praw',
        'prawcore',
        'requests',
        'six',
        'spotipy',
        'update-checker',
        'urllib3',
        'websocket-client',
        'youtube-dl'
      ],
      data_files=[
          ('config', [
              'src/config/.secrets-template.conf',
              'src/config/log.conf',
              'src/config/spoddit.conf',
          ]),
          ('assets', [
              'src/assets/spoddit.svg'
          ])
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          # TODO: Choose license
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Operating System :: Unix',
          'Programming Language :: Python :: 3.8',
          'Topic :: Multimedia :: Sound/Audio'
      ],
      platforms=[
        'any'
      ],
      keywords=[
          'reddit',
          'spotify',
          'playlist',
          'scraper'
      ])
