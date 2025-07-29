# QuantumBench

QuantumBench is a cross-platform benchmarking and visualization tool for quantum circuit simulators.  
It enables researchers and developers to compare performance and fidelity of quantum simulations across popular frameworks like Qiskit, PennyLane, and Cirq — all from a simple and interactive web interface built using Flask and React.

---

## Features

- Run benchmark tests on quantum circuits across multiple simulators  
- Visualize execution time and fidelity comparisons via intuitive bar charts  
- Upload custom `.qasm` files or use built-in examples  
- Export benchmark results  
- Lightweight and modular codebase (Python + React)  

---

```
quantumbench/
├── app/                       ← Main benchmarking logic
│   └── runner.py             ← Runs circuits on different simulators
├── flask-server.py           ← Flask API server
├── react-app/                ← React frontend app
│   ├── basic_bell_state.qasm
│   ├── public/
│   ├── src/
│   │   ├── components/       ← UI components (charts, selectors)
│   │   ├── Dashboard.js      ← Core frontend logic
│   │   └── App.css / index.js / ...
├── requirements.txt          ← Python dependencies
├── package.json              ← Root package.json if needed
├── LICENSE                   ← MIT License
├── README.md
└── CONTRIBUTING.md           ← Guide for contributors
```

## Getting Started

### Prerequisites
- Python 3.9 or above  
- Node.js + npm  
- pip (Python package manager)

### Installation

1. Clone the repository and go into the directory:

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate   # Linux/macOS
   .\env\Scripts\activate    # Windows
   ```

3. Install backend requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Flask backend:
   ```bash
   python flask-server.py
   ```

5. Install frontend dependencies and start React app:
   ```bash
   cd react-app
   npm install
   npm start
   ```
   Open http://localhost:3000 to view the frontend.

---

## Usage

1. Upload your `.qasm` file (e.g., Bell state circuit)  
2. Select one or more simulator backends: Qiskit, PennyLane, Cirq  
3. Click **Run Benchmark**

You’ll see:
- Execution time per backend
- Output statevectors

A bar chart will display execution times for visual clarity.

---

## Project Structure

### Backend: `flask-server.py`, `app/runner.py`
- Parses QASM
- Removes measurements
- Simulates with Qiskit, PennyLane, Cirq
- Returns execution time and statevector for each backend
- Calculates fidelity between output statevectors

### Frontend: `react-app/`
- `Dashboard.js` handles UI logic and API communication
- `BarChart.jsx` shows performance results
- `simSelector.jsx` handles simulator selection
- Upload QASM, run benchmark, display results

## Contact
Created by Adwaitha V — feel free to reach out!  
GitHub: [@AdwaithaV](https://github.com/AdwaithaV)  
Email: adwaithav063@gmail.com

---

## License

This project is licensed under the [MIT License](LICENSE).
