import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity
import cirq
import numpy as np
from qiskit.quantum_info import Operator
import pennylane as qml
import pennylane.numpy as np
import warnings
warnings.filterwarnings("ignore")


def run_qiskit(qasm_code):
    try:
        # Parse the QASM code into a QuantumCircuit
        circuit = QuantumCircuit.from_qasm_str(qasm_code)

        # Remove measurements (optional: clean version)
        circuit.data = [gate for gate in circuit.data if gate[0].name != 'measure']

        # Use AerSimulator with statevector method
        simulator = AerSimulator(method='statevector')

        # Save statevector for retrieval
        circuit.save_statevector()

        # Transpile circuit for simulator
        transpiled = transpile(circuit, simulator)

        # Start timing
        start_time = time.time()

        # Run simulation
        result = simulator.run(transpiled).result()
        exec_time = time.time() - start_time

        # Extract statevector
        statevector = result.get_statevector()

        # Ideal Bell state for fidelity comparison: (|00> + |11>) / sqrt(2)
        ideal = Statevector([1/2**0.5, 0, 0, 1/2**0.5])
        fidelity = state_fidelity(statevector, ideal)

        return {
            "backend": "Qiskit",
            "time": exec_time,
            "fidelity": fidelity,
            "statevector": statevector.data.tolist()
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
