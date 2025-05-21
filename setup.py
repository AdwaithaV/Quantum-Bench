from setuptools import setup, find_packages

setup(
    name="quantumbench",
    version="0.1.0",
    description="Benchmarking and visualization for quantum circuit simulators",
    author="Adwaitha V",
    packages=find_packages(),
    install_requires=[
        "qiskit",
        "pennylane",
        "cirq",
        "streamlit",
        "matplotlib",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "quantumbench=quantumbench.cli:main"
        ]
    },
)
