from setuptools import setup, find_packages

setup(
    name='scraping_packages',
    version='0.1.0',
    author='Firasath Ali',
    author_email='fmohamm1@mail.yu.edu',
    description='A package for project 2',
    long_description='Working With Web Data',
    url='https://github.com/Firasathalimohammed/Project-2',
    packages=find_packages(),  # automatically discover and include all packages
    install_requires=[
        "requests>2.25.1",
        "pandas>=1.2.1",
        "beautifulsoup4>=4.9.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS independent"
    ],
    python_requires=">=3.6"
)
