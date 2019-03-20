from setuptools import find_packages, setup


def get_long_description():
    with open('README.rst') as fp:
        long_description = fp.read()
    return long_description


setup(
    name='set-tracker',
    version='1.0.dev0',
    description='Track sets of excercises',
    long_description=get_long_description(),
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'SQLAlchemy>=1.3.1',
    ],
    entry_points="""
    [console_scripts]
    set-tracker = settracker.__main__:main

    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
