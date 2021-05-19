from setuptools import setup, find_packages

setup(
    name="AlignR",
    version="2.0.5",
    packages=find_packages(),
    license="GPlv3",
    author="Julien Alardot",
    author_email='"Julien Alardot" <cschultz@example.com>',
    description="Simple Tool to track the alignments of your players",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    python_requires=">=3.8",
    url="https://github.com/JulienAlardot/AlignmentReporter",
    project_urls={
        "Bug Tracker": "https://github.com/JulienAlardot/AlignmentReporter/issues",
    },
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Games/Entertainment :: Role-Playing"
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "AlignR-Launch = AlignmentReporter.UI.py:launch",
        ],
    },
    install_requires=[
        "setuptools>=40.8.0",
        "PySide2>=5.14",
        "matplotlib<=3.3",
        "numpy<=1.20",
        "pyparsing",
        "Cython>=0.29",
        "pandas>=1.2",
        "scipy>=1.6",
    ],
)
