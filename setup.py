from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f_:
    long_description = f_.read()

setup(
    name='shiny',
    version="0.0.1",
    author="Jan-Oliver Joswig",
    author_email="jan.joswig@fu-berlin.de",
    description="Collection of scripts and recipes for MD analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/janjoswig/shiny-md-collection",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    zip_safe=False
)
