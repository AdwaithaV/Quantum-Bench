import Select from 'react-select';
import React from 'react';
import './App.css';


function simSelector({ selectedSimulators, setSelectedSimulators, runBenchmark, clearSelection }) {
    const simulatorOptions = [
        { value: 'qiskit', label: 'Qiskit' },
        { value: 'cirq', label: 'Cirq' },
        { value: 'braket', label: 'Amazon Braket' },
        { value: 'projectq', label: 'ProjectQ' },
        // Add more simulators as needed
      ];
      
      const customStyles = {
        control: (provided) => ({
          ...provided,
          backgroundColor: '#2d2b38',
          borderColor: '#3a3845',
          color: '#fff',
          borderRadius: '0.5rem',
          padding: '2px 6px',
        }),
        multiValue: (provided) => ({
          ...provided,
          backgroundColor: '#4b445a',
          color: '#fff',
          borderRadius: '0.3rem',
        }),
        multiValueLabel: (provided) => ({
          ...provided,
          color: '#fff',
        }),
        option: (provided, state) => ({
          ...provided,
          backgroundColor: state.isFocused ? '#3d3a4f' : '#2d2b38',
          color: '#fff',
        }),
        menu: (provided) => ({
          ...provided,
          backgroundColor: '#2d2b38',
        }),
      };
    return (
        <div className="mb-6">
        <label className="text-white text-sm mb-1 block">Select simulators to benchmark</label>
        <Select
            isMulti
            options={simulatorOptions}
            value={selectedSimulators}
            onChange={setSelectedSimulators}
            styles={customStyles}
            placeholder="Choose options"
        />
        <div className="flex gap-4 mt-4">
            <button
            onClick={runBenchmark}
            className="px-4 py-2 bg-white text-black rounded hover:bg-gray-200 transition"
            >
            Run Benchmark
            </button>
            <button
            onClick={clearSelection}
            className="px-4 py-2 border border-white text-white rounded hover:bg-white hover:text-black transition"
            >
            CLEAR
            </button>
        </div>
        </div>
    );
}

  export default simSelector