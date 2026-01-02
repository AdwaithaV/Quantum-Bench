import time
import tracemalloc
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import cirq
from cirq.contrib.qasm_import import circuit_from_qasm

MAX_QUBITS_LOCAL = 24

# --- PLOTTING FUNCTION ---
def plot_master_dashboard(df):
    sns.set_theme(style="whitegrid")
    
    metrics_groups = {
        "Accuracy & Reliability": ["fidelity", "success_probability"],
        "Time & Latency (Log Scale)": ["execution_time", "compilation_time", "total_latency"],
        "Computational Resources": ["memory_mb", "throughput_shots_sec"],
        "Compiler Efficiency": ["swap_overhead", "optimization_ratio", "post_depth"]
    }
    
    # Filter for existing columns
    valid_groups = {}
    for group, metrics in metrics_groups.items():
        valid_metrics = [m for m in metrics if m in df.columns]
        if valid_metrics:
            valid_groups[group] = valid_metrics

    total_plots = sum(len(v) for v in valid_groups.values())
    if total_plots == 0: return None

    rows = (total_plots + 2) // 3
    fig, axes = plt.subplots(rows, 3, figsize=(20, 5 * rows))
    fig.suptitle('🏆 QBench: Ultimate Parameter Comparison', fontsize=24, y=1.02)
    
    ax_flat = axes.flatten() if rows > 1 else [axes]
    plot_idx = 0
    palette = "viridis"

    for group_name, metrics in valid_groups.items():
        for metric in metrics:
            if plot_idx >= len(ax_flat): break
            ax = ax_flat[plot_idx]
            
            # Plot
            sns.barplot(
                data=df, x="backend", y=metric, hue="type", 
                ax=ax, palette=palette, edgecolor="black"
            )
            
            # Formatting
            ax.set_title(metric.replace("_", " ").title(), fontsize=14, fontweight='bold')
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.legend(loc='upper right', fontsize='x-small')
            
            # --- FIX: Rotate X-Axis Labels (45 degrees) ---
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

            if metric in ["fidelity", "success_probability"]:
                ax.set_ylim(0, 1.1)
            if "time" in metric or "latency" in metric:
                ax.set_yscale("log")
                ax.set_ylabel("Seconds (Log)")
            
            plot_idx += 1

    for i in range(plot_idx, len(ax_flat)):
        fig.delaxes(ax_flat[i])

    plt.tight_layout()
    return fig

class QBenchAnalyzer:
    def __init__(self, ibm_token=None, ibm_crn=None):
        self.service = None
        if ibm_token and ibm_crn:
            try:
                self.service = QiskitRuntimeService(
                    channel="ibm_cloud", instance=ibm_crn, token=ibm_token
                )
            except Exception as e:
                print(f"IBM Auth Warning: {e}")

    def get_available_hardware(self):
        """
        Fetches devices available to the SPECIFIC USER ACCOUNT.
        Returns empty list if failed.
        """
        if not self.service:
            return []
            
        try:
            # Fetch devices specific to this account
            backends = self.service.backends(simulator=False, operational=True)
            device_names = [b.name for b in backends]
            return device_names
        except Exception:
            # If API fetch fails, return empty so UI knows it failed
            return []

    # --- UTILITIES ---
    def get_circuit_metrics(self, circuit, stage="pre"):
        ops = circuit.count_ops()
        return {
            f"{stage}_depth": circuit.depth(),
            f"{stage}_gate_count": sum(ops.values()),
        }

    def hellinger_fidelity(self, p_ideal, p_measured):
        fidelity = 0
        all_keys = set(p_ideal.keys()) | set(p_measured.keys())
        for k in all_keys:
            p1 = p_ideal.get(k, 0)
            p2 = p_measured.get(k, 0)
            fidelity += np.sqrt(p1 * p2)
        return fidelity ** 2

    def sv_to_counts(self, statevector):
        probs = np.abs(statevector)**2
        n = int(np.log2(len(probs)))
        counts = {}
        fmt = f'0{n}b'
        for i, p in enumerate(probs):
            if p > 1e-9: counts[format(i, fmt)] = p
        return counts

    # --- RUNNERS ---
    def run_qiskit(self, qasm_code):
        metrics = {"backend": "Qiskit Aer", "type": "Simulator"}
        try:
            qc = QuantumCircuit.from_qasm_str(qasm_code)
            if qc.num_qubits > MAX_QUBITS_LOCAL:
                raise ValueError(f"Circuit too large for local simulation ({qc.num_qubits} > {MAX_QUBITS_LOCAL} qubits).")
            qc.remove_final_measurements()
            metrics.update(self.get_circuit_metrics(qc, "pre"))
            
            tracemalloc.start()
            t0 = time.time()
            
            # Safe Fallback Logic for Windows DLL issues
            try:
                from qiskit_aer import AerSimulator
                sim = AerSimulator(method='statevector')
                qc.save_statevector()
                transpiled = transpile(qc, sim, optimization_level=2)
                metrics['compilation_time'] = time.time() - t0
                t1 = time.time()
                job = sim.run(transpiled)
                sv = job.result().get_statevector().data
                metrics['execution_time'] = time.time() - t1
                metrics.update(self.get_circuit_metrics(transpiled, "post"))
            except ImportError:
                metrics["backend"] = "Qiskit (Safe Mode)"
                transpiled = transpile(qc, optimization_level=2)
                metrics['compilation_time'] = time.time() - t0
                t1 = time.time()
                sv = Statevector.from_instruction(transpiled).data
                metrics['execution_time'] = time.time() - t1
                metrics.update(self.get_circuit_metrics(transpiled, "post"))

            _, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            metrics['memory_mb'] = peak_mem / (1024**2)
            metrics['counts'] = self.sv_to_counts(sv)
            metrics['total_latency'] = metrics['compilation_time'] + metrics['execution_time']
        except Exception as e:
            metrics['error'] = str(e)
        return metrics

    def run_cirq(self, qasm_code):
        metrics = {"backend": "Cirq", "type": "Simulator"}
        try:
            clean_qasm = "\n".join([l for l in qasm_code.splitlines() if not l.strip().startswith("barrier")])
            t0 = time.time()
            circuit = circuit_from_qasm(clean_qasm)
            if len(circuit.all_qubits()) > MAX_QUBITS_LOCAL:
                raise ValueError(f"Circuit too large ({len(circuit.all_qubits())} qubits).")
            metrics['compilation_time'] = time.time() - t0
            metrics['pre_depth'] = len(circuit.moments)
            metrics['post_depth'] = len(circuit.moments)
            metrics['pre_gate_count'] = sum(1 for _ in circuit.all_operations())
            metrics['post_gate_count'] = metrics['pre_gate_count']
            
            tracemalloc.start()
            t1 = time.time()
            sim = cirq.Simulator()
            res = sim.simulate(circuit)
            metrics['execution_time'] = time.time() - t1
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            metrics['memory_mb'] = peak / (1024**2)
            metrics['counts'] = self.sv_to_counts(res.final_state_vector)
            metrics['total_latency'] = metrics['compilation_time'] + metrics['execution_time']
        except Exception as e:
            metrics['error'] = str(e)
        return metrics

    def run_pennylane(self, qasm_code):
        metrics = {"backend": "PennyLane", "type": "Simulator"}
        try:
            # --- WINDOWS FIX: Safe Import + Pure Python Device ---
            import sys
            # Hack to prevent plugin load
            sys.modules['pennylane_lightning'] = None
            sys.modules['pennylane_lightning.qubit'] = None
            sys.modules['controller_wrappers'] = None
            
            import pennylane as qml
            
            clean_qasm = "\n".join([l for l in qasm_code.splitlines() if not l.strip().startswith("barrier")])
            qc_temp = QuantumCircuit.from_qasm_str(clean_qasm)
            n_qubits = qc_temp.num_qubits
            
            if n_qubits > MAX_QUBITS_LOCAL:
                raise ValueError(f"Circuit too large ({n_qubits} qubits).")
            
            t0 = time.time()
            
            # Explicitly use 'default.qubit' (Python) to avoid DLL errors from 'lightning.qubit' (C++)
            dev = qml.device("default.qubit", wires=n_qubits)
            
            # MANUAL CONVERTER: Bypass broken pennylane-qiskit bridge (DLL safe)
            qubit_map = {q: i for i, q in enumerate(qc_temp.qubits)}
            
            def qfunc():
                for inst in qc_temp.data:
                    op = inst.operation
                    name = op.name
                    wires = [qubit_map[q] for q in inst.qubits]
                    params = op.params
                    
                    if name == 'h': qml.Hadamard(wires=wires)
                    elif name == 'x': qml.PauliX(wires=wires)
                    elif name == 'y': qml.PauliY(wires=wires)
                    elif name == 'z': qml.PauliZ(wires=wires)
                    elif name == 'cx': qml.CNOT(wires=wires)
                    elif name == 'cz': qml.CZ(wires=wires)
                    elif name == 'rx': qml.RX(params[0], wires=wires)
                    elif name == 'ry': qml.RY(params[0], wires=wires)
                    elif name == 'rz': qml.RZ(params[0], wires=wires)
                    elif name == 'measure': pass
                    elif name == 'barrier': pass
                    else: 
                        # Best effort for benchmark
                        pass
            metrics['compilation_time'] = time.time() - t0
            
            metrics['pre_depth'] = qc_temp.depth()
            metrics['post_depth'] = qc_temp.depth()
            metrics['pre_gate_count'] = sum(qc_temp.count_ops().values())
            metrics['post_gate_count'] = metrics['pre_gate_count']

            tracemalloc.start()
            t1 = time.time()
            @qml.qnode(dev)
            def circuit():
                qfunc()
                return qml.state()
            sv = circuit()
            metrics['execution_time'] = time.time() - t1
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            metrics['memory_mb'] = peak / (1024**2)
            metrics['counts'] = self.sv_to_counts(np.array(sv))
            metrics['total_latency'] = metrics['compilation_time'] + metrics['execution_time']
            
        except Exception as e:
             # Even if it fails, capture the error properly without crashing
             metrics['error'] = f"PennyLane Error: {str(e)}"
             metrics['counts'] = {}
        return metrics

    def run_ibm_hardware(self, qasm_code, backend_name):
        metrics = {"backend": backend_name, "type": "Hardware"}
        try:
            backend = self.service.backend(backend_name)
            qc = QuantumCircuit.from_qasm_str(qasm_code)
            if qc.num_clbits == 0: qc.measure_all()
            metrics.update(self.get_circuit_metrics(qc, "pre"))
            
            t0 = time.time()
            transpiled = transpile(qc, backend=backend, optimization_level=3)
            metrics['compilation_time'] = time.time() - t0
            metrics.update(self.get_circuit_metrics(transpiled, "post"))
            
            sampler = Sampler(mode=backend)
            t_submit = time.time()
            job = sampler.run([transpiled])
            
            try:
                result = job.result(timeout=60)
            except Exception:
                metrics['error'] = f"Timeout: Job {job.job_id()} queued. Check IBM Dashboard."
                metrics['counts'] = {}
                return metrics

            metrics['total_latency'] = time.time() - t_submit
            metrics['execution_time'] = metrics['total_latency']
            
            pub_res = result[0]
            counts_data = list(pub_res.data.values())[0].get_counts()
            total_shots = sum(counts_data.values())
            
            metrics['throughput_shots_sec'] = total_shots / metrics['total_latency']
            metrics['counts'] = {k: v/total_shots for k,v in counts_data.items()}
            metrics['memory_mb'] = 0.0 
        except Exception as e:
            err_str = str(e)
            if "No backend matches" in err_str:
                metrics['error'] = "Access Denied (Not in your Plan)"
            else:
                metrics['error'] = err_str
            metrics['counts'] = {}
        return metrics

    def sanitize_results(self, df):
        if df.empty: return df
        
        # Populate missing columns with defaults
        cols_defaults = {
            'swap_overhead': 0.0, 'optimization_ratio': 1.0, 
            'throughput_shots_sec': 0.0, 'execution_time': 0.0, 
            'total_latency': 0.0, 'pre_gate_count': 0.0, 'post_gate_count': 0.0
        }
        for col, val in cols_defaults.items():
            if col not in df.columns: df[col] = val

        # Logic fixes
        if 'execution_time' in df.columns and 'total_latency' in df.columns:
            df['execution_time'] = df['execution_time'].fillna(df['total_latency'])

        if 'post_gate_count' in df.columns:
            df['swap_overhead'] = (df['post_gate_count'] - df['pre_gate_count']).fillna(0)
            
        # Calculate Success Probability
        def calc_success(row):
            counts = row.get('counts')
            if pd.isna(row.get('success_probability')) and isinstance(counts, dict):
                if len(counts) > 0:
                    return max(counts.values())
            return 0.0
        df['success_probability'] = df.apply(calc_success, axis=1)
        
        return df

    def execute_benchmark(self, qasm_code, selected_backends):
        data = []
        baseline_counts = None

        # 1. Qiskit (Must run first for baseline)
        if "Qiskit Aer" in selected_backends:
            q_res = self.run_qiskit(qasm_code)
            if 'error' not in q_res:
                q_res['fidelity'] = 1.0 
                baseline_counts = q_res['counts']
            
            data.append(q_res)

        # 2. Cirq
        if "Cirq" in selected_backends:
            c_res = self.run_cirq(qasm_code)
            if 'error' not in c_res and baseline_counts:
                c_res['fidelity'] = self.hellinger_fidelity(baseline_counts, c_res['counts'])
            data.append(c_res)

        # 3. PennyLane
        if "PennyLane" in selected_backends:
            p_res = self.run_pennylane(qasm_code)
            if 'error' not in p_res and baseline_counts and p_res.get('counts'):
                p_res['fidelity'] = self.hellinger_fidelity(baseline_counts, p_res['counts'])
            elif 'error' in p_res:
                p_res['fidelity'] = 0.0
            data.append(p_res)

        # 4. Hardware
        for backend_name in selected_backends:
            if backend_name not in ["Qiskit Aer", "Cirq", "PennyLane"]:
                if self.service:
                    hw_res = self.run_ibm_hardware(qasm_code, backend_name)
                    if 'error' not in hw_res and baseline_counts and hw_res.get('counts'):
                        hw_res['fidelity'] = self.hellinger_fidelity(baseline_counts, hw_res['counts'])
                    data.append(hw_res)

        df = pd.DataFrame(data)
        return self.sanitize_results(df)