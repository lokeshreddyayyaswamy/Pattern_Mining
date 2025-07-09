from setuptools import setup, find_packages

setup(
    name="pattern_mining_frequent_patterns_lokesh",  # unique on PyPI
    version="1.0.0.0",
    author="Lokesh A",
    author_email="lokeshreddy2680@gmail.com",
    description="Apriori Frequent Pattern Mining Algorithm",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lokeshreddyayyaswamy/Pattern_Mining",
    packages=find_packages(),
    install_requires=[
        "numpy",
        'urllib3',
        'sphinx',
        'sphinx-rtd-theme',
        "pandas",
        "validators",
        "psutil",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
