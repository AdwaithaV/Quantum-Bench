
import React, { useState } from 'react';
import './App.css';
import SimSelector from './simSelector';

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

  // const toggleSimulator = (sim) => {
  //   setSimulators((prev) =>
  //     prev.includes(sim) ? prev.filter((s) => s !== sim) : [...prev, sim]
  //   );
  // };

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

      {/* <div className="upload-section">
        <label>Upload your QASM uploadcircuit</label>
        <input type="file" accept=".qasm" onChange={handleFileUpload} />
        {qasmCode && <pre className="code-block">{qasmCode}</pre>}
      </div> */}
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
            {results.map((res, idx) => (
              <div className="result-box" key={idx}>
                <h3>{res.backend}</h3>
                {res.error ? (
                  <p className="error">Error: {res.error}</p>
                ) : (
                  <>
                    <p><strong>Time:</strong> {res.time.toFixed(4)}s</p>
                    <p><strong>Fidelity:</strong> {res.fidelity !== undefined ? res.fidelity.toFixed(4) : 'Not Available'}</p>
                    <p><strong>Statevector (truncated):</strong></p>
                    <pre className="code-block">{JSON.stringify(res.statevector?.slice(0, 4), null, 2)}</pre>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
