import streamlit as st
from app.runner import run_qiskit, run_pennylane, run_cirq

def main():
    st.set_page_config(page_title="QuantumBench", layout="wide")
    st.title("🔬 QuantumBench: Quantum Circuit Benchmarking Tool")

    # File upload
    uploaded_file = st.file_uploader("📂 Upload your QASM circuit", type=["qasm"])
    qasm_code = uploaded_file.read().decode("utf-8") if uploaded_file else None

    if qasm_code:
        st.code(qasm_code, language="qasm")

    # Simulator selection
    simulators = st.multiselect("⚙️ Select simulators to benchmark", ["Qiskit", "PennyLane", "Cirq"])

    # Initialize session state for results
    if "results" not in st.session_state:
        st.session_state.results = []

    # Run benchmark button
    if st.button("🚀 Run Benchmark"):
        if not qasm_code:
            st.warning("⚠️ Please upload a QASM circuit.")
        elif not simulators:
            st.warning("⚠️ Select at least one simulator.")
        else:
            st.info("⏳ Benchmarking in progress...")
            results = []

            if "Qiskit" in simulators:
                results.append(run_qiskit(qasm_code))
            if "PennyLane" in simulators:
                results.append(run_pennylane(qasm_code))
            if "Cirq" in simulators:
                results.append(run_cirq(qasm_code))

            # Store in session state to persist across reruns
            st.session_state.results = results

    # Display stored results
    if st.session_state.get("results"):
        st.subheader("📊 Benchmark Results")
        for res in st.session_state.results:
            if "error" in res:
                st.error(f"{res['backend']} error: {res['error']}")
            else:
                st.markdown(f"**Backend:** `{res['backend']}`")
                st.markdown(f"⏱️ Execution Time: `{res['time']:.4f}` seconds")

                fidelity = res.get("fidelity")
                if fidelity is not None:
                    st.markdown(f"🎯 Fidelity: `{fidelity:.4f}`")
                else:
                    st.markdown("🎯 Fidelity: `Not Available`")

                st.markdown("🧬 Statevector (truncated):")
                statevector = res.get("statevector", [])
                st.code(statevector[:4], language="json")

if __name__ == "__main__":
    main()
