import streamlit as st
import pandas as pd
from app.runner import run_qiskit, run_pennylane, run_cirq

def main():
    st.set_page_config(page_title="QuantumBench", layout="wide")
    st.title("🔬 QuantumBench: Quantum Circuit Benchmarking Tool")

    # Upload QASM file
    uploaded_file = st.file_uploader("📂 Upload your QASM circuit", type=["qasm"])
    qasm_code = uploaded_file.read().decode("utf-8") if uploaded_file else None

    if qasm_code:
        st.code(qasm_code, language="qasm")

    # Simulator selection
    simulators = st.multiselect("⚙️ Select simulators to benchmark", ["Qiskit", "PennyLane", "Cirq"])

    # Initialize session state to persist results
    if "results" not in st.session_state:
        st.session_state.results = []

    # Run benchmark on button click
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

            st.session_state.results = results

    # Display results if available
    if st.session_state.get("results"):
        st.subheader("📊 Benchmark Results")

        # Create columns
        cols = st.columns(len(st.session_state.results))

        # Prepare chart data
        exec_time_data = {
            "Backend": [],
            "Execution Time (s)": [],
        }

        for i, res in enumerate(st.session_state.results):
            with cols[i]:
                if "error" in res:
                    st.error(f"{res['backend']} error: {res['error']}")
                else:
                    st.markdown(f"### `{res['backend']}`")
                    st.markdown(f"⏱️ **Time:** `{res['time']:.4f}` seconds")

                    fidelity = res.get("fidelity")
                    if fidelity is not None:
                        st.markdown(f"🎯 **Fidelity:** `{fidelity:.4f}`")
                    else:
                        st.markdown("🎯 **Fidelity:** `Not Available`")

                    st.markdown("🧬 **Statevector (truncated):**")
                    statevector = res.get("statevector", [])
                    st.code(statevector[:4], language="json")

                    exec_time_data["Backend"].append(res["backend"])
                    exec_time_data["Execution Time (s)"].append(res["time"])

        # Plot bar chart
        st.subheader("📈 Execution Time Comparison")
        df_time = pd.DataFrame(exec_time_data)
        st.bar_chart(df_time.set_index("Backend"))

    # Optional: Clear results button
    if st.button("🧹 Clear Results"):
        st.session_state.results = []
        st.success("Cleared previous results.")

if __name__ == "__main__":
    main()
