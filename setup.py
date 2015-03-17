from setuptools import setup

setup(
    name = 'cresbot',
    version = '0.0.1',
    author = 'Matthew Dowdell',
    author_email = 'mdowdell244@gmail.com',
    description = 'description',
    license = 'GPLv3',
    url = 'https://github.com/onei/cresbot',
    packages = ['cresbot', 'cresbot.tasks'],
    install_requires = ['beautifulsoup4', 'ceterach', 'pyyaml', 'requests', 'schedule'],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4'
    ]
)
