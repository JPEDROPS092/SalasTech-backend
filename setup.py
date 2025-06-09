from setuptools import setup, find_packages

setup(
    name="salstech",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=14.0.0",
        "rich-toolkit>=0.14.7",
        "PyYAML>=6.0.2",
        "python-dotenv>=1.1.0",
    ],
    entry_points={
        "console_scripts": [
            "salstech=cli.main:app",
        ],
    },
)
