import streamlit as st
from app.runner import run_qiskit

def main():
    st.set_page_config(page_title="QuantumBench", layout="wide")
    st.title("🧪 QuantumBench: Quantum Circuit Benchmarking Tool")

    # Upload .qasm file
    uploaded_file = st.file_uploader("Upload your QASM circuit", type=["qasm"])

    qasm_code = None
    if uploaded_file:
        qasm_code = uploaded_file.read().decode("utf-8")
        st.code(qasm_code, language="qasm")

    # Select simulators to benchmark
    simulators = st.multiselect("Select simulators", ["Qiskit", "PennyLane", "Cirq"])

    # Benchmark on click
    if st.button("Run Benchmark"):
        if not qasm_code:
            st.warning("Please upload a QASM circuit.")
        elif not simulators:
            st.warning("Select at least one simulator.")
        else:
            st.info("Benchmarking in progress...")

            results = []

            if "Qiskit" in simulators:
                result = run_qiskit(qasm_code)
                results.append(result)

            # Display results
            st.subheader("🔍 Benchmark Results")
            for res in results:
                if "error" in res:
                    st.error(f"{res['backend']} error: {res['error']}")
                else:
                    st.markdown(f"**Backend:** {res['backend']}")
                    st.markdown(f"- ⏱ Execution Time: `{res['time']:.4f}` seconds")
                    st.markdown(f"- 🎯 Fidelity: `{res['fidelity']:.4f}`")
                    st.markdown("📦 Statevector (truncated):")
                    st.code(res['statevector'][:4], language="json")  # show only first few elements

if __name__ == "__main__":
    main()
