from setuptools import setup, find_packages
import os

# Read the contents of README if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="Visual-Programming-Interface",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A visual programming interface for Raspberry Pi with PyQt6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your-repo",  # Optional
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PyQt6==6.7.1",
        "paramiko==3.4.0",
        "cryptography==41.0.7",
    ],
    entry_points={
        "console_scripts": [
            "visual-pi=main_pyqt:main",
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/yourusername/your-repo/issues",
        "Source": "https://github.com/yourusername/your-repo",
    },
)
