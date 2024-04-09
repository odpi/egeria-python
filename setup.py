from setuptools import find_packages, setup

setup(
    name='pyegeria',
    extras_require=dict(tests=["pytest"]),
    # packages=find_packages(where="src"),
    package_dir={"": "src"},
    version='0.3.1',
    packages=find_packages(where="src"),
    url="https://egeria-project.org/egeria-python",
    project_urls={
        "Issues": "https://github.com/odpi/egeria-python/issues",
    },
    #license='Apache 2.0',
    author='Dan Wolfson',
    author_email='dan.wolfson@pdr-associates.com',
    description='A python client to the Egeria Open Metadata System',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=["egeria", "metadata", "governance"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.10',
    install_requires=[
        "requests~=2.31.0",
        "validators~=0.22.0",
        "pytest~=7.4.2",
        "urllib3~=1.26.15",
        "tabulate~=0.9.0",
        "pandas~=2.2.0",
        "rich~=13.7.1",
        "httpx~=0.26.0"
    ]
)
