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

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import time

def run_qiskit(qasm_code):
    try:
        # Parse QASM and remove measurement ops
        circuit = QuantumCircuit.from_qasm_str(qasm_code)
        circuit.remove_final_measurements()  #  remove all measure ops

        # Initialize simulator
        simulator = AerSimulator(method='statevector')
        circuit.save_statevector()

        # Transpile for backend
        transpiled = transpile(circuit, simulator)

        # Run and time it
        start_time = time.time()
        result = simulator.run(transpiled).result()
        exec_time = time.time() - start_time

        # Get statevector
        statevector = result.get_statevector()

        return {
            "backend": "Qiskit",
            "time": exec_time,
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
