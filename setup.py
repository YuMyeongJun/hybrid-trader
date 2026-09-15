"""Setup configuration for Hybrid Trader package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hybrid-trader",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Unified Python library for Korean stock (KIS) and crypto (Upbit) automated trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hybrid-trader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
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
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "mypy>=0.950",
        ]
    },
    entry_points={
        "console_scripts": [
            # Add command-line tools here if needed
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/hybrid-trader/issues",
        "Source": "https://github.com/yourusername/hybrid-trader",
        "Documentation": "https://github.com/yourusername/hybrid-trader#readme",
    },
)
