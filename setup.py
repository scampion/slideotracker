from distutils.core import setup
import sys

sys.path.append('slideo')
import slideo

setup(name='slideo',
      version='1.0',
      author='Sebastien Campion',
      author_email='seb@scamp.fr',
      url='http://slideotracker.gforge.inria.fr/',
      #download_url='',
      description='Synchronize slides with the corresponding video recording',
      long_description=slideo.SlideoTracker.__doc__,
      packages = ['slideo'],
      scripts = ['scripts/slideo'],
      keywords='synchronise slides videos',
      license='Lesser Affero General Public License v3',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Topic :: Multimedia'
                  ],
     )
