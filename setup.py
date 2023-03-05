import os
import sys
import shutil
from setuptools import setup, find_packages
from goodgame import __version__ as version


def read_file(fn: str) -> str:
    f = open(os.path.join(cwd, fn), 'r', encoding=encoding)
    result = f.read()
    f.close()
    return result


encoding = 'utf-8'
cwd = os.path.dirname(__file__) or os.getcwd()

readme_content = read_file('README.md')
license_content = read_file('LICENSE.md')
requirements_content = read_file('requirements.txt')

if 'sdist' in sys.argv or 'bdist_wheel' in sys.argv:
    dist_path = os.path.join(cwd, 'dist')
    if os.path.isdir(dist_path):
        shutil.rmtree(dist_path)

setup(
    name='goodgame',
    author='Pixelsuft',
    url='https://github.com/Pyxelsuft/goodgame',
    project_urls={
        'Readme': 'https://github.com/Pyxelsuft/goodgame/blob/main/README.md',
        'Documentation': 'https://github.com/Pyxelsuft/goodgame/tree/main/docs',
        'Issue tracker': 'https://github.com/Pyxelsuft/goodgame/issues'
    },
    version=version,
    packages=find_packages(),
    license='MIT',
    description='A simple and nice pysdl2 wrapper.',
    long_description=readme_content,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=tuple(x for x in requirements_content.split('\n') if x.strip()),
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia',
        'Topic :: Software Development',
        'Operating System :: Android',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: iOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    zip_safe=True,
    py_modules=['goodgame'],
    package_dir={'': '.'},
    keywords='goodgame'
)
