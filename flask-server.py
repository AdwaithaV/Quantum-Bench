from flask import Flask, request, jsonify
from app.runner import run_qiskit, run_pennylane, run_cirq
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/api/run-benchmark", methods=["POST"])
def run_benchmark():
    data = request.get_json()
    qasm_code = data.get("qasm")
    simulators_raw = data.get("simulators", [])
    simulators = [s["value"] for s in simulators_raw]
    if not qasm_code:
        return jsonify({"error": "Missing QASM code"}), 400

    results = []
    
    if "qiskit" in simulators:
        print("qisikit")
        results.append(run_qiskit(qasm_code))
    if "pennylane" in simulators:
        print('pennylane')
        results.append(run_pennylane(qasm_code))
    if "cirq" in simulators:
        print("cirq")
        results.append(run_cirq(qasm_code))
    df = pd.DataFrame(results)
    df = df.fillna(0)
    df['statevector'] = df['statevector'].apply(lambda vec: [str(x) for x in vec])
    df['time'] = df['time'].round(4)
    json_data = df.to_dict(orient='records')
    print(json_data)
    return jsonify(json_data), 200

if __name__ == "__main__":
    app.run(port=5000)
