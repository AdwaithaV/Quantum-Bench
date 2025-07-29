import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import cirq
from qiskit.quantum_info import Operator
import pennylane as qml
import warnings
warnings.filterwarnings("ignore")

def run_qiskit(qasm_code):
    try:
        circuit = QuantumCircuit.from_qasm_str(qasm_code)
        circuit.remove_final_measurements()

        simulator = AerSimulator(method='statevector')
        circuit.save_statevector()

        transpiled = transpile(circuit, simulator)

        start_time = time.time()
        result = simulator.run(transpiled).result()
        exec_time = time.time() - start_time

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
        qc = QuantumCircuit.from_qasm_str(qasm_code)
        qc.remove_final_measurements()

        unitary = Operator(qc).data
        n_qubits = qc.num_qubits

        qubits = [cirq.LineQubit(i) for i in range(n_qubits)]
        gate = cirq.MatrixGate(unitary)
        circuit = cirq.Circuit(gate(*qubits))

        simulator = cirq.Simulator()
        start_time = time.time()
        result = simulator.simulate(circuit)
        exec_time = time.time() - start_time

        statevector = result.final_state_vector.tolist()

        return {
            "backend": "Cirq",
            "time": exec_time,
            "statevector": statevector
        }

    except Exception as e:
        return {"backend": "Cirq", "error": str(e)}

def run_pennylane(qasm_code):
    try:
        qc = QuantumCircuit.from_qasm_str(qasm_code)
        qc.remove_final_measurements()
        n = qc.num_qubits

        pl_qfunc = qml.from_qiskit(qc)

        dev = qml.device("lightning.qubit", wires=n)

        @qml.qnode(dev)
        def circuit():
            pl_qfunc()
            return qml.state()

        start_time = time.time()
        result = circuit()
        exec_time = time.time() - start_time

        return {
            "backend": "PennyLane",
            "time": exec_time,
            "statevector": result.tolist()
        }

    except Exception as e:
        return {"backend": "PennyLane", "error": str(e)}


# Test QASM input
# result = run_qiskit("""
# OPENQASM 2.0;
# include "qelib1.inc";

# qreg q[2];
# creg c[2];

# h q[0];
# cx q[0], q[1];

# measure q[0] -> c[0];
# measure q[1] -> c[1];
# """)
# print(result)
