from setuptools import setup, find_packages

setup(
    name="schachtmeister3",
    version="0.0.1",
    author="Paweł Redman",
    author_email="pawel.redman@gmail.com",
    description="Detect ban evasion by checking WHOIS and reverse DNS records",
    url="https://github.com/enneract/schachtmeister3",
    packages=find_packages(),
    install_requires=[
    ],
    extras_requires={
        'test': [
            'pytest',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
