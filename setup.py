
import os
from setuptools import find_packages, setup
from django_api_tester import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='django_api_tester',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Django rest framework API testing utilities.',
    long_description=README,
    url='https://github.com/hile/django-api-tester',
    author='Ilkka Tuohela',
    author_email='ilkka.tuohela@codento.com',
    install_requires=(
        'Django>=2.2.3',
        'djangorestframework>=3.9.0',
    ),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
