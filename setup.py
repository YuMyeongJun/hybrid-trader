"""Setup configuration for Hybrid Trader package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
root_dir = Path(__file__).parent
long_description = (root_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="hybrid-trader",
    version="0.1.0",
    author="MJ YU",
    author_email="dev.claude@blumn.ai",
    maintainer="MJ YU",
    maintainer_email="dev.claude@blumn.ai",
    description="Unified Python library for Korean stock (KIS) and crypto (Upbit) automated trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mjyu-louis/hybrid-trader",
    project_urls={
        "Bug Reports": "https://github.com/mjyu-louis/hybrid-trader/issues",
        "Documentation": "https://github.com/mjyu-louis/hybrid-trader/blob/main/README.md",
        "Source Code": "https://github.com/mjyu-louis/hybrid-trader",
        "API Reference": "https://github.com/mjyu-louis/hybrid-trader/blob/main/docs/API.md",
        "Examples": "https://github.com/mjyu-louis/hybrid-trader/tree/main/examples",
        "Contributing": "https://github.com/mjyu-louis/hybrid-trader/blob/main/docs/CONTRIBUTING.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    include_package_data=True,
    keywords=[
        "trading",
        "automated-trading",
        "stock",
        "cryptocurrency",
        "kis",
        "upbit",
        "korea",
        "finance",
        "investing",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Korean",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-kis>=0.3.0",
        "pyupbit>=0.2.35",
        "requests>=2.28.0",
        "pandas>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "pytest-xdist>=2.5.0",
            "pytest-timeout>=2.1.0",
            "pytest-html>=3.1.0",
            "psutil>=5.9.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "mypy>=0.950",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "pytest-xdist>=2.5.0",
            "pytest-timeout>=2.1.0",
            "pytest-html>=3.1.0",
            "psutil>=5.9.0",
        ],
        "lint": [
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add command-line tools here if needed in the future
        ],
    },
    zip_safe=False,
    license="MIT",
)
