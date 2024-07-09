from setuptools import find_packages, setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyegeria',
    extras_require=dict(tests=["pytest"]),
    include_package_data= True,
    # packages=find_packages(where="src"),
    package_dir={"": "src"},
    scripts=["examples/widgets/operational/view_server_status.py",
             "examples/widgets/operational/view_eng_action_status.py",
             "examples/widgets/operational/view_platform_status.py",
             "examples/widgets/operational/view_coco_status.py",
             "examples/widgets/operational/view_integ_daemon_status.py",
             "examples/widgets/operational/view_gov_eng_status.py",
             "examples/widgets/operational/view_server_list.py",
             "examples/widgets/operational/get_tech_type_elements.py",
             "examples/widgets/operational/get_tech_type_template.py",

             "examples/widgets/catalog_user/list_assets.py",
             "examples/widgets/catalog_user/view_asset_graph.py",
             "examples/widgets/catalog_user/view_collection.py",
             "examples/widgets/catalog_user/view_glossary.py",

             "examples/widgets/personal_organizer/list_todos.py",
             "examples/widgets/personal_organizer/view_my_todos.py",
             "examples/widgets/personal_organizer/view_open_todos.py",
             "examples/widgets//personal_organizer/list_projects.py",
             "examples/widgets/personal_organizer/get_my_profile.py",

             "examples/widgets/developer/list_asset_types.py",
             "examples/widgets/developer/list_relationship_types.py",
             "examples/widgets/developer/get_tech_details.py",
             "examples/widgets/developer/list_tech_types.py",
             "examples/widgets/developer/list_registered_services.py",
             "examples/widgets/developer/get_guid_info.py",
             "examples/widgets/developer/list_valid_metadata_values.py",
             "examples/widgets/developer/list_tech_templates.py",


             "examples/Doc_Samples/Create_Collection_Sample.py",
             "examples/Doc_Samples/Create_Sustainability_Collection_Sample.py",

             ],
    # entry_points = {
    #     'console_scripts': [
    #         'server_status = examples.widgets.server_status:main',
    #         'my_todos = examples.widgets.my_todos:main',
    #     ]
    # },

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
    # long_description=open('README.md').read(),
    long_description= long_description,
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
        "rich~=13.7.1",
        "httpx~=0.26.0"
    ]
)
