from setuptools import setup

# As dependências são gerenciadas pelo pyproject.toml
setup(
    entry_points={
        "console_scripts": [
            "SalasTech=SalasTech.cli.main:app",
        ],
    },
)
