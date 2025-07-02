import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity

def run_qiskit(qasm_code):
    try:
        # Parse the QASM code into a QuantumCircuit
        circuit = QuantumCircuit.from_qasm_str(qasm_code)

        # Initialize AerSimulator with statevector method
        simulator = AerSimulator(method='statevector')

        # Add instruction to save statevector
        circuit.save_statevector()

        # Transpile for the simulator backend
        transpiled = transpile(circuit, simulator)

        # Start timing
        start_time = time.time()

        # Run the transpiled circuit
        result = simulator.run(transpiled).result()

        # Extract statevector
        statevector = result.get_statevector()

        exec_time = time.time() - start_time

        # Compute fidelity (against ideal state if needed, here assumed perfect)
        fidelity = 1.0  # Default to 1.0 as in your original code

        return {
            "backend": "Qiskit",
            "time": exec_time,
            "fidelity": fidelity,
            "statevector": statevector.data.tolist()  # Optional: for analysis
        }

    except Exception as e:
        return {"backend": "Qiskit", "error": str(e)}

# Test QASM input
result = run_qiskit("""
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
""")
print(result)
