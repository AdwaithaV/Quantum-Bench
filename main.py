import sys
# GLOBAL WORKAROUND: Force disable broken PennyLane plugins (DLL error fix)
try:
    sys.modules['pennylane_lightning'] = None
    sys.modules['pennylane_lightning.qubit'] = None
    sys.modules['controller_wrappers'] = None
except: pass

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from app.runner import QBenchAnalyzer, plot_master_dashboard


st.set_page_config(page_title="QBench Pro", layout="wide")

# CSS INJECTION
import base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    bg_code = get_base64("assets/bg.png")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bg_code}");
            background-size: cover;
            background-position: center;
            background-blend-mode: overlay;
            background-color: rgba(54, 69, 79, 0.95); /* Deep Charcoal overlay */
        }}
        /* Custom Button Style */
        div.stButton > button {{
            background: linear-gradient(145deg, #1e262c, #232d34);
            color: #00BFFF;
            border: 1px solid #00BFFF;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }}
        div.stButton > button:hover {{
            background: #00BFFF;
            color: #1e262c;
            box-shadow: 0 0 15px #00BFFF;
            transform: translateY(-2px);
        }}
        /* Custom Tab Color */
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
            color: #D3D3D3;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #00BFFF !important;
            border-bottom-color: #00BFFF !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
except Exception: pass

st.title("QBench Pro: Ultimate Quantum Benchmark")
st.markdown("Compare Simulators (Qiskit, Cirq, PennyLane) vs Real IBM Quantum Hardware.")

# --- SIDEBAR ---
st.sidebar.header("1. Configuration")
st.sidebar.info("To run on Hardware, you need an IBM Quantum Account (IBM Cloud).")
ibm_crn = st.sidebar.text_input("IBM Cloud CRN", type="password")
ibm_api = st.sidebar.text_input("IBM API Key", type="password")

# Initialize Analyzer with credentials if provided
analyzer = QBenchAnalyzer(ibm_token=ibm_api, ibm_crn=ibm_crn)

st.sidebar.header("2. Select Backends")
simulators = st.sidebar.multiselect(
    "Simulators", 
    ["Qiskit Aer", "Cirq", "PennyLane"],
    default=["Qiskit Aer", "Cirq", "PennyLane"]
)

# Default hardware list (empty until fetched)
if 'hardware_list' not in st.session_state:
    st.session_state.hardware_list = []

if st.sidebar.button("Fetch Available Hardware"):
    if not ibm_api:
        st.sidebar.error("Please enter an API Key first.")
    else:
        with st.sidebar:
            with st.spinner("Connecting to IBM Cloud..."):
                fetched = analyzer.get_available_hardware()
                if fetched:
                    st.session_state.hardware_list = fetched
                    st.success(f"Found {len(fetched)} devices!")
                else:
                    st.warning("No devices found or Auth failed.")

hardware_options = st.session_state.hardware_list

selected_hardware = st.sidebar.multiselect("Quantum Hardware", hardware_options)

# --- MAIN ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Input Quantum Circuit (OpenQASM 2.0)")
    default_qasm = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
h q[0];
cx q[0], q[1];
cx q[1], q[2];
cx q[2], q[3];
rx(0.5) q[0];
"""
    qasm_code = st.text_area("Paste QASM Code", default_qasm, height=250)

with col2:
    # Removed Info Message as requested
    run_btn = st.button("RUN BENCHMARK", type="primary", use_container_width=True)

if run_btn:
    all_backends = simulators + selected_hardware
    
    if not all_backends:
        st.error("Select at least one backend!")
    else:
        with st.spinner(f"Benchmarking on {len(all_backends)} devices..."):
            # Pass the combined list of strings (simulators + hardware names)
            df = analyzer.execute_benchmark(qasm_code, all_backends)
            
            if df.empty:
                st.error("No data returned. Check your backend selection.")
            else:
                st.success("Benchmark Complete!")
                
                # METRICS TABS
                tab1, tab2, tab3 = st.tabs(["Master Dashboard", "Data Table", "Memory Matrix"])
                
                with tab1:
                    fig = plot_master_dashboard(df)
                    if fig: st.pyplot(fig)
                    else: st.warning("Not enough data to plot.")

                with tab2:
                    # Clean display dataframe
                    display_df = df.drop(columns=['counts'], errors='ignore')
                    st.dataframe(display_df)

                with tab3:
                    st.subheader("Memory & Resource Matrix")
                    cols_to_show = ['backend', 'type', 'memory_mb', 'total_latency', 'fidelity']
                    valid_cols = [c for c in cols_to_show if c in df.columns]
                    st.dataframe(df[valid_cols])
                    
                    if len(df) > 1 and 'fidelity' in df.columns:
                        st.write("### Resource Heatmap")
                        try:
                            # Pivot data for heatmap
                            h_data = df.set_index('backend')[['memory_mb', 'total_latency', 'fidelity']]
                            # Normalize columns for better heatmap visualization
                            normalized_df = (h_data - h_data.min()) / (h_data.max() - h_data.min())
                            
                            fig_heat, ax_heat = plt.subplots(figsize=(8, 5))
                            sns.heatmap(h_data, annot=True, cmap="YlGnBu", ax=ax_heat)
                            st.pyplot(fig_heat)
                        except Exception as e:
                            st.info(f"Heatmap unavailable: {e}")