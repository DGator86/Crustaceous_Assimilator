"""Setup configuration for moltbot-repo-scout."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="moltbot-repo-scout",
    version="0.1.0",
    author="DGator86",
    description="GitHub repository discovery and analysis tool for Moltbot trading bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DGator86/Crustaceous_Assimilator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyGithub>=2.1.0",
        "PyYAML>=6.0",
        "click>=8.1.0",
        "requests>=2.28.0",
        "gitpython>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "moltbot-scout=moltbot_scout.cli:main",
        ],
    },
)
