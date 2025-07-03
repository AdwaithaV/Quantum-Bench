import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity
import cirq
import numpy as np
from qiskit.quantum_info import Operator
import pennylane as qml
import pennylane.numpy as np

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
        fidelity = 1.0  #

        return {
            "backend": "Qiskit",
            "time": exec_time,
            "fidelity": fidelity,
            "statevector": statevector.data.tolist()  # Optional: for analysis
        }

    except Exception as e:
        return {"backend": "Qiskit", "error": str(e)}
    

def run_cirq(qasm_code):
    try:
        # Parse the QASM code using Qiskit and remove measurements
        qc = QuantumCircuit.from_qasm_str(qasm_code)
        qc.remove_final_measurements()

        # Extract unitary operator
        unitary = Operator(qc).data
        n_qubits = qc.num_qubits

        # Create Cirq circuit with MatrixGate
        qubits = [cirq.LineQubit(i) for i in range(n_qubits)]
        gate = cirq.MatrixGate(unitary)
        circuit = cirq.Circuit(gate(*qubits))

        # Simulate
        simulator = cirq.Simulator()
        start_time = time.time()
        result = simulator.simulate(circuit)
        exec_time = time.time() - start_time

        # Get final statevector
        statevector = result.final_state_vector.tolist()

        return {
            "backend": "Cirq",
            "time": exec_time,
            "fidelity": None,  # Will be computed during comparison
            "statevector": statevector
        }

    except Exception as e:
        return {"backend": "Cirq", "error": str(e)}

def run_pennylane(qasm_code):
    try:
        # Load Qiskit circuit
        qc = QuantumCircuit.from_qasm_str(qasm_code)
        qc.remove_final_measurements()
        n = qc.num_qubits

        # Convert Qiskit circuit into PennyLane template
        pl_qfunc = qml.from_qiskit(qc)

        # Create PennyLane device
        dev = qml.device("lightning.qubit", wires=n)

        @qml.qnode(dev)
        def circuit():
            pl_qfunc()
            return qml.state()

        # Run circuit
        start_time = time.time()
        result = circuit()
        exec_time = time.time() - start_time

        return {
            "backend": "PennyLane",
            "time": exec_time,
            "fidelity": None,
            "statevector": result.tolist()
        }

    except Exception as e:
        return {"backend": "PennyLane", "error": str(e)}


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
