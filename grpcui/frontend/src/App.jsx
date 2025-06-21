import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [endpoints, setEndpoints] = useState([]);
  const [endpoint, setEndpoint] = useState('');
  const [method, setMethod] = useState('');
  const [body, setBody] = useState('{}');
  const [result, setResult] = useState('');

  useEffect(() => {
    axios.get('/api/endpoints').then(res => setEndpoints(res.data));
  }, []);

  const run = async () => {
    const req = { id: Date.now().toString(), endpoint, method, body: JSON.parse(body) };
    const res = await axios.post(`/api/projects/default/requests`, req);
    const idx = (await axios.get(`/api/projects/default/requests`)).data.length - 1;
    const runRes = await axios.post(`/api/projects/default/requests/${idx}/run`);
    setResult(runRes.data.result);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>gRPC UI</h1>
      <div>
        <label>Endpoint
          <select value={endpoint} onChange={e => setEndpoint(e.target.value)}>
            <option value="">--choose--</option>
            {endpoints.map(ep => <option key={ep.name} value={ep.name}>{ep.name}</option>)}
          </select>
        </label>
      </div>
      <div>
        <input value={method} onChange={e => setMethod(e.target.value)} placeholder="Service/Method" />
      </div>
      <div>
        <textarea rows={6} cols={60} value={body} onChange={e => setBody(e.target.value)}></textarea>
      </div>
      <button onClick={run}>Run</button>
      <pre>{result}</pre>
    </div>
  );
}

export default App;
