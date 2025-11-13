"""Setup script for schubert-toolbox Python package."""

from setuptools import setup, find_packages

# Leitura do README se existir
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="schubert-toolbox",
    version="0.1.0",
    author="Raphael Schubert",
    author_email="contato@schubert.com.br",
    description="Schubert Toolbox - SDK Python com ferramentas e utilitários padronizados",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/schubert-toolbox",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        # Adicionar dependências conforme necessário
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)

