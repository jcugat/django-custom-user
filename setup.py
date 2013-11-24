import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-custom-user',
    version='0.2',
    packages=['custom_user'],
    include_package_data=True,
    license='BSD License',
    description="Custom user model for Django >= 1.5 with the same behaviour as Django's default User but with email instead of username.",
    long_description=README,
    keywords='django custom user auth model email without username',
    url='https://github.com/recreatic/django-custom-user',
    author='Recreatic',
    author_email='info@recreatic.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "Django >= 1.5",
    ],
)
