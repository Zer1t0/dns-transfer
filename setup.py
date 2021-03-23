import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


name = "dns-transfer"

setuptools.setup(
    name=name,
    version="0.0.1",
    author="Eloy Pérez",
    author_email="zer1t0ps@protonmail.com",
    description="Check if DNS zone transfer is allowed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    url="https://github.com/zer1t0/{}".format(name),
    entry_points={
        "console_scripts": [
            "{} = {}.main:main".format(name, name.replace("-", "_")),
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
