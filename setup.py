from setuptools import find_packages, setup

setup(
    name='pyegeria',
    extras_require=dict(tests=["pytest"]),
    include_package_data= True,
    # packages=find_packages(where="src"),
    package_dir={"": "src"},
    scripts=["examples/widgets/server_status.py",
             "examples/widgets/engine_action_status.py",
             "examples/widgets/find_todos.py",
             "examples/widgets/glossary_view.py",
             "examples/widgets/integration_daemon_status.py",
             "examples/widgets/gov_engine_status.py",
             "examples/widgets/list_asset_types.py",
             "examples/widgets/multi-server_status.py",
             "examples/widgets/my_todos.py",
             "examples/widgets/open_todos.py",
             "examples/widgets/server_status_widget.py",
             "examples/widgets/view_my_profile.py",
             ],
    # entry_points = {
    #     'console_scripts': [
    #         'server_status = examples.widgets.server_status:main',
    #         'my_todos = examples.widgets.my_todos:main',
    #     ]
    # },
    # version='0.3.4',
    packages=find_packages(where="src"),
    package_data= {
        'examples': ['*'],
    },
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
