
import glob
from setuptools import setup

url = 'https://github.com/hile/django-api-tester'

setup(
    name='example',
    keywords='django example project',
    description='Example django project with api tests',
    author='Ilkka Tuohela',
    author_email='hike@iki.fi',
    url=url,
    version='0.1',
    license='PSF',
    scripts=glob.glob('bin/*'),
    install_requires=(
    ),
    setup_requires=(
        'pytest-runner',
    ),
    tests_require=(
        'pytest',
        'pytest-datafiles',
    ),
)
