from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="atol-client",
    version="1.14.6",
    license='MIT',
    author="Sergei Michenko",
    author_email="mserg@tih.ru",
    description="Client for ATOL POS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sir-go/atol-client",
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.6",
)
