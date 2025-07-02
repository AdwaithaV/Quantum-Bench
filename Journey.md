## STAGE 1 -- 02-07-2025
# 🧠 QuantumBench Development Log & Learning Journal

This document is a **complete record of my development journey** building the QuantumBench MVP — a benchmarking tool for quantum simulators. It includes my decisions, challenges, learning outcomes, and detailed code explanations.

---

## 📌 Project Objective

**QuantumBench** is designed to help users — especially beginners — compare quantum circuit simulators like Qiskit, Cirq, and PennyLane. It provides an easy-to-use Streamlit web interface where users can upload `.qasm` files, select simulators, and visualize performance metrics like execution time and fidelity.

---

## 🚀 Initial Setup

### ✅ Goals for MVP:

* Upload `.qasm` quantum circuits
* Benchmark using Qiskit's AerSimulator
* Show execution time, fidelity, and statevector
* Display results in Streamlit UI

### 🛠️ Initial Repository Structure

```
quantum-bench/
├── app/               # Contains core logic (runner.py)
├── main.py            # Streamlit UI logic
├── requirements.txt   # Dependencies
├── README.md
```

---

## 📦 Step-by-Step Development Journey

### 1. ✅ Creating the Virtual Environment

```bash
python -m venv env
.\env\Scripts\activate  # on Windows
pip install -r requirements.txt
```

**Issue I faced:** Accidentally used `source` on Windows — learned that PowerShell requires `.\env\Scripts\Activate.ps1`

---

### 2. ✅ Building the Backend (`runner.py`)

This file is located inside `app/runner.py` and is responsible for running the quantum circuit simulation.

### 🔍 `run_qiskit(qasm_code)` - Line-by-Line Explanation

```python
import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity
```

**🔎 Learned:** `AerSimulator` must be imported from `qiskit_aer`, not base `qiskit`.

```python
def run_qiskit(qasm_code):
    try:
        circuit = QuantumCircuit.from_qasm_str(qasm_code)
```

✅ Converts raw QASM string into a `QuantumCircuit` object.

```python
        simulator = AerSimulator(method='statevector')
        circuit.save_statevector()
        transpiled = transpile(circuit, simulator)
```

✅ Set up simulator and prepare the circuit for execution on it.

```python
        start_time = time.time()
        result = simulator.run(transpiled).result()
        statevector = result.get_statevector()
        exec_time = time.time() - start_time
```

✅ Measures execution time and retrieves final statevector.

```python
        fidelity = 1.0  # Assumes ideal simulator for now

        return {
            "backend": "Qiskit",
            "time": exec_time,
            "fidelity": fidelity,
            "statevector": statevector.data.tolist()
        }
```

✅ Returns all benchmark metrics.

```python
    except Exception as e:
        return {"backend": "Qiskit", "error": str(e)}
```

✅ Adds basic error handling.

---

### 3. ✅ Building the Frontend (`main.py`)

This is the UI logic using Streamlit. It runs the app and connects user input to the backend.

### 🔍 `main.py` - Line-by-Line Explanation

```python
import streamlit as st
from app.runner import run_qiskit
```

✅ Imports UI framework and backend simulation function.

```python
def main():
    st.set_page_config(page_title="QuantumBench", layout="wide")
    st.title("🧪 QuantumBench: Quantum Circuit Benchmarking Tool")
```

✅ Sets up Streamlit UI page title and layout.

```python
    uploaded_file = st.file_uploader("Upload your QASM circuit", type=["qasm"])
    qasm_code = None
    if uploaded_file:
        qasm_code = uploaded_file.read().decode("utf-8")
        st.code(qasm_code, language="qasm")
```

✅ Handles file upload and shows raw QASM code.

```python
    simulators = st.multiselect("Select simulators", ["Qiskit", "PennyLane", "Cirq"])
```

✅ Dropdown menu to select which simulators to use.

```python
    if st.button("Run Benchmark"):
        if not qasm_code:
            st.warning("Please upload a QASM circuit.")
        elif not simulators:
            st.warning("Select at least one simulator.")
```

✅ Basic input validation.

```python
        else:
            st.info("Benchmarking in progress...")
            results = []
            if "Qiskit" in simulators:
                result = run_qiskit(qasm_code)
                results.append(result)
```

✅ Runs benchmark with Qiskit if selected.

```python
            st.subheader("🔍 Benchmark Results")
            for res in results:
                if "error" in res:
                    st.error(f"{res['backend']} error: {res['error']}")
                else:
                    st.markdown(f"**Backend:** {res['backend']}")
                    st.markdown(f"- ⏱ Execution Time: `{res['time']:.4f}` seconds")
                    st.markdown(f"- 🎯 Fidelity: `{res['fidelity']:.4f}`")
                    st.markdown("📦 Statevector (truncated):")
                    st.code(res['statevector'][:4], language="json")
```

✅ Displays execution results — clean and human-readable.

```python
if __name__ == "__main__":
    main()
```

✅ Entry point for the app.

---

## 🧠 What I Learned

### ✅ Technical

* Qiskit Aer requires separate install (`qiskit-aer`)
* Streamlit is great for fast prototyping of ML/QC apps
* `.qasm` files can be read and parsed directly by Qiskit
* Importance of modular code (`runner.py` handles logic, `main.py` handles UI)

### ✅ Debugging Lessons

* PowerShell has a different way to activate venvs
* `NameError: AerSimulator` taught me to import explicitly
* Streamlit app crashes if `streamlit` isn't installed globally or venv isn’t activated

---

## 🧱 Next Plans

* Implement PennyLane and cirq backends
* Add a bar chart to compare time and fidelity 
* Enable to export .csv file of the results 

---

## 🔚 Final Words

This journey was more than just building a project — it was about learning how to:

* Manage dependencies
* Understand quantum circuit execution
* Write clean, modular code
* Build beginner-friendly UIs

I hope this log becomes helpful for anyone looking to get started with quantum tools.
