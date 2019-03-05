import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ibm-cos-simple-fs',
    version='0.0.2',
    author="Shengyi Pan",
    author_email="shengyi.pan1@gmail.com",
    description="A package for representing IBM Cloud Object Storage (COS) bucket like a file system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/psyking841/ibm-cos-simple-fs",
    packages=['ibm_cos_bucket'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)