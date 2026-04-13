from setuptools import setup, find_packages

setup(
    name="exp-tracker",
    version="0.1.0",
    description="Python SDK for the ML Experiment Tracker",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "urllib3>=2.0.0",
    ],
    extras_require={
        "cli": ["click>=8.1.0", "rich>=13.0.0"],
        "dev": ["pytest", "pytest-asyncio", "httpx"],
    },
    entry_points={
        "console_scripts": [
            "exp-cli=exp_tracker.cli:cli",
        ]
    },
)
