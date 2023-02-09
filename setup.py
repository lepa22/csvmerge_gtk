from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="csvmerge_gtk",
    version="1.0",
    entry_points={
        'gui_scripts':
            'csvmerge = csvmerge_gtk.main:main'
    },
    author="Eleftherios Pavlou",
    author_email="e.pavlou@uoi.gr",
    description="An application for previewing and merging CSV files obtained with the ENLIGHTEN Spectroscopy Software.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/your_package_name",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyGObject",
        "matplotlib >= 3.0.0",
    ]
)
