import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'pyserial',
    'watchdog',
    'pyramid_scheduler',
    'sqlalchemy',
    'pyramid_tm',
    'zope.sqlalchemy'
    ]

setup(name='HallLed',
      version='0.0',
      description='HallLed',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="hallled",
      entry_points="""\
      [paste.app_factory]
      main = hallled:main
      [console_scripts]
      init_hallled_db = hallled.initialize_db:main
      """,
      )
