from setuptools import setup, find_packages

setup(
    name="shine",
    version="4.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "geopy>=2.4.0",
        "numpy>=1.26.0",
    ],
    entry_points={
        "console_scripts": [
            "shine=shine.cli:main",
        ],
    },
    python_requires=">=3.9",
    description="Shine v4 — AI-Powered Moneyline Parlay Engine",
)
