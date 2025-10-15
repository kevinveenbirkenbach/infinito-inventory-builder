<h1>Infinito Inventory Builder</h1>
<p>
  Generate Ansible inventories interactively from invokable Infinito.Nexus roles.
</p>
import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [roles, setRoles] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [host, setHost] = useState("localhost");
  const [style, setStyle] = useState("group");
  const [ignore, setIgnore] = useState("");
  const [inventory, setInventory] = useState("");

  useEffect(() => {
    fetch(`${API}/roles?invokable_only=true`)
      .then(r => r.json())
      .then(j => {
        setRoles(j.items || []);
        setFiltered(j.items || []);
      });
  }, []);

  const onFilter = (q) => {
    q = q.toLowerCase();
    setFiltered(roles.filter(r => r.toLowerCase().includes(q)));
  };

  const download = (name, content) => {
    const blob = new Blob([content], { type: "text/yaml" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const genInventory = async () => {
    const body = {
      host,
      style,
      ignore: ignore.split(",").map(s => s.trim()).filter(Boolean)
    };
    const res = await fetch(`${API}/generate/inventory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const j = await res.json();
    setInventory(j.content);
    download(j.filename, j.content);
  };

  return (
    <div style={{ fontFamily: "system-ui", padding: 16, maxWidth: 960, margin: "0 auto" }}>
      <h1>Infinito Inventory Builder</h1>
      <p>Generate Ansible inventories interactively from invokable Infinito.Nexus roles.</p>

      <input placeholder="Search roles…" onChange={e => onFilter(e.target.value)} />
      <ul style={{ columns: 2 }}>
        {filtered.map(r => (<li key={r}>{r}</li>))}
      </ul>

      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap:"wrap" }}>
        <label>Host: <input value={host} onChange={e => setHost(e.target.value)} /></label>
        <label>Style:
          <select value={style} onChange={e => setStyle(e.target.value)}>
            <option value="group">group</option>
            <option value="hostvars">hostvars</option>
          </select>
        </label>
        <label>Ignore (comma-separated): <input value={ignore} onChange={e => setIgnore(e.target.value)} placeholder="web-app-x,svc-db-y" /></label>
        <button onClick={genInventory}>Download inventory.yml</button>
      </div>

      <h3>Preview</h3>
      <pre style={{ background: "#f6f6f6", padding: 12, whiteSpace: "pre-wrap" }}>{inventory}</pre>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
