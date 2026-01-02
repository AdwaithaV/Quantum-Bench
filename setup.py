from setuptools import setup, find_packages

setup(
    name="quantumbench",
    version="2.0.0",
    description="Professional Benchmarking for Quantum Simulators & Hardware",
    author="Adwaitha V",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "qiskit",
        "qiskit-aer",
        "qiskit-ibm-runtime",
        "pennylane",
        "pennylane-qiskit",
        "cirq",
        "streamlit",
        "matplotlib",
        "seaborn",
        "pandas",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "quantumbench=streamlit.web.cli:main_run_cl"
        ]
    },
)