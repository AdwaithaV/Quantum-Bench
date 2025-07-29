import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

function BarChartComponent({
    data,
    dataKey = "time",
    title = "Execution Time Comparison",
    yAxisLabel = "Time",
    barColor = "#8884d8"
  }) {
    const executionData = data.filter(d => !d.backend.startsWith("Fidelity"));
  
    const backendCount = executionData.length;
    let filteredData = executionData;
  
    if (data.length === 6) {
      filteredData = executionData.slice(0, 3);  
    } else if (data.length === 3) {
      filteredData = executionData.slice(0, 2);  
    } else if (data.length === 2) {
      filteredData = executionData.slice(0, 1);  
    }
  
    return (
      <div className="chart-container">
        <h3>{title}</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={filteredData} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="backend" />
            <YAxis label={{ value: yAxisLabel, angle: -90, position: 'insideLeft', dx: -9, dy: -10,style: { fill: '#ff6347' } }} />
            <Tooltip />
            <Legend />
            <Bar dataKey={dataKey} fill={barColor} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }
  

export default BarChartComponent;
