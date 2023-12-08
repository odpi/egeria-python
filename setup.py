# from setuptools import find_packages, setup

setup(
    name='pyegeria',
    extras_require=dict(tests=["pytest"]),
    # packages=find_packages(where="src"),
    package_dir={"": "src"},
    version='0.04',
    packages=['pyegeria'],
    url='https://egeria-project.org',
    license='Apache 2.0',
    author='Dan Wolfson',
    author_email='dan.wolfson@pdr-associates.com',
    description='A python client to the Egeria Open Metadata System'
)
