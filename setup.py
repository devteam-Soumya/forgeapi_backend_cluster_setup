from setuptools import setup, find_packages

setup(
    name="forgeapi",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "pytest",
        "httpx",
        "requests",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "forgeapi=mini_agent.cli:main",
        ],
    },
)