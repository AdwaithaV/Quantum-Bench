
import React, { useState } from 'react';
import './App.css';
import SimSelector from './components/simSelector';
import BarChartComponent from './components/BarChart';


function Dashboard() {
  const [qasmCode, setQasmCode] = useState('');
  const [simulators, setSimulators] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.qasm')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setQasmCode(e.target.result);
      };
      reader.readAsText(file);
    } else {
      alert('Please upload a .qasm file');
    }
  };

  const runBenchmark = async () => {
    if (!qasmCode) {
      alert('Please upload a QASM circuit.');
      return;
    }
    if (simulators.length === 0) {
      alert('Select at least one simulator.');
      return;
    }
    setLoading(true);
    console.log(simulators);
    try {
      const response = await fetch('/api/run-benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ qasm: qasmCode, simulators }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error during benchmarking:', error);
      alert('Error running benchmark. Check console for details.');
    }
    setLoading(false);
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <div className="container">
      <h1>QuantumBench: Quantum Circuit Benchmarking Tool</h1>
      <div className="upload-section">
      <label>Upload your QASM circuit</label>
      <div
        className="drop-zone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFileUpload({ target: { files: e.dataTransfer.files } });
        }}
      >
        <div className="upload-text">
          Drag and drop file here <br />
          <span className="upload-subtext">Limit 200MB per file • QASM</span>
        </div>
        <label htmlFor="qasm-upload" className="browse-btn">Browse files</label>
        <input
          id="qasm-upload"
          type="file"
          accept=".qasm"
          onChange={handleFileUpload}
          hidden
        />
      </div>
      {qasmCode && <pre className="code-block">{qasmCode}</pre>}
    </div>

    <SimSelector
      selectedSimulators={simulators}
      setSelectedSimulators={setSimulators}
      runBenchmark={runBenchmark}
      clearSelection={clearResults}
      loading={loading}
    />
      {results.length > 0 && (
        <div className="results">
          <h2>Benchmark Results</h2>
          <div className="results-columns">
            {['Qiskit', 'PennyLane', 'Cirq'].map((backend) => {
              const res = results.find(r => r.backend === backend);
              return (
                <div className="result-box" key={backend}>
                  <h3 className="backend-title">{backend}</h3>
                  {res && !res.error ? (
                    <>
                      <p><strong>Time:</strong> <span className="time-value">{res.time.toFixed(4)}</span> seconds</p>
                      <p><strong>Statevector (truncated):</strong></p>
                      <pre className="code-block">{JSON.stringify(res.statevector?.slice(0, 4), null, 2)}</pre>
                    </>
                  ) : (
                    <p className="error">Error: {res?.error || 'No data'}</p>
                  )}
                </div>
              );
            })}
          </div>
          <BarChartComponent
            data={results.map(res => ({
              backend: res.backend,
              time: res.time
            }))}
          />

          <button className="clear-btn" onClick={clearResults}>Clear Results</button>
        </div>
      )}

    </div>
  );
}

export default Dashboard;
