#!/usr/bin/env python3
"""
Setup script for Professional Invoice Manager
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().strip().split('\n')
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="professional-invoice-manager",
    version="2.1.0",
    author="Professional Invoice Manager Team",
    author_email="contact@example.com",
    description="A comprehensive desktop invoice management system with professional UI and keyboard navigation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/professional-invoice-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-qt>=4.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "isort>=5.0",
            "mypy>=0.800",
        ],
        "build": [
            "pyinstaller>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "invoice-manager=launch_app:main",
        ],
        "gui_scripts": [
            "invoice-manager-gui=launch_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.css", "*.json", "*.md"],
    },
    data_files=[
        ("styles", ["styles/main.css", "styles/dialogs.css"]),
        ("docs", [
            "docs/technical-specification.md",
            "docs/porting-guide.md",
            "docs/vat-summary-implementation.md",
        ]),
    ],
    keywords="invoice, accounting, business, finance, VAT, desktop, PyQt5",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/professional-invoice-manager/issues",
        "Source": "https://github.com/yourusername/professional-invoice-manager",
        "Documentation": "https://github.com/yourusername/professional-invoice-manager/tree/main/docs",
    },
)
