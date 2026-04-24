import React, { useEffect, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const ConfigPanel = () => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const fetchConfig = async () => {
    try {
      const res = await fetch(`${API_URL}/api/configuration/`);
      if (!res.ok) throw new Error("Error al cargar configuración");
      const data = await res.json();
      setConfig(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchConfig(); }, []);

  const handleChange = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: parseFloat(value) || 0 }));
    setMessage(null);
  };

  const weightsTotal = config
    ? Math.round((config.weight_population + config.weight_income + config.weight_education + config.weight_business) * 100)
    : 0;

  const handleSave = async () => {
    if (weightsTotal !== 100) {
      setError(`Los pesos deben sumar 100%. Suma actual: ${weightsTotal}%`);
      return;
    }
    if (config.threshold_high <= config.threshold_medium) {
      setError("El umbral alto debe ser mayor que el umbral medio");
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/configuration/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Error al guardar");
      }
      const updated = await res.json();
      setConfig(updated);
      setMessage("Configuración guardada correctamente");
      setTimeout(() => setMessage(null), 3000);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div style={{ padding: 30 }}>Cargando configuración...</div>;

  if (!config) return <div style={{ padding: 30, color: "red" }}>{error || "Sin configuración"}</div>;

  return (
    <div style={{ padding: 30, backgroundColor: "#f4f6f8" }}>
      <h2 style={{ marginBottom: 20, color: "#0f172a" }}>⚙️ Configuración del Modelo</h2>

      <div style={{ backgroundColor: "white", borderRadius: 12, boxShadow: "0 4px 12px rgba(0,0,0,0.1)", padding: 24, maxWidth: 600 }}>

        {/* Pesos */}
        <h3 style={{ color: "#0d9488", marginBottom: 12 }}>Pesos del modelo</h3>
        <p style={{ fontSize: 13, color: "#64748b", marginBottom: 16 }}>
          Los pesos deben sumar 100%.
          Total actual: <strong style={{ color: weightsTotal === 100 ? "#16a34a" : "#dc2626" }}>{weightsTotal}%</strong>
        </p>

        {[
          { key: "weight_population", label: "Densidad poblacional" },
          { key: "weight_income", label: "Ingreso promedio" },
          { key: "weight_education", label: "Nivel educativo" },
          { key: "weight_business", label: "Presencia comercial" },
        ].map(({ key, label }) => (
          <div key={key} style={{ display: "flex", alignItems: "center", marginBottom: 10, gap: 12 }}>
            <label style={{ width: 180, fontSize: 14 }}>{label}</label>
            <input
              type="number"
              step="0.05"
              min="0"
              max="1"
              value={config[key]}
              onChange={e => handleChange(key, e.target.value)}
              style={inputStyle}
            />
            <span style={{ fontSize: 13, color: "#64748b" }}>{Math.round(config[key] * 100)}%</span>
          </div>
        ))}

        {/* Umbrales */}
        <h3 style={{ color: "#0d9488", margin: "20px 0 12px" }}>Umbrales de clasificación</h3>
        {[
          { key: "threshold_high", label: "Alta oportunidad ≥" },
          { key: "threshold_medium", label: "Oportunidad media ≥" },
        ].map(({ key, label }) => (
          <div key={key} style={{ display: "flex", alignItems: "center", marginBottom: 10, gap: 12 }}>
            <label style={{ width: 180, fontSize: 14 }}>{label}</label>
            <input
              type="number"
              step="0.05"
              min="0"
              max="1"
              value={config[key]}
              onChange={e => handleChange(key, e.target.value)}
              style={inputStyle}
            />
          </div>
        ))}

        {/* Normalización */}
        <h3 style={{ color: "#0d9488", margin: "20px 0 12px" }}>Valores máximos de normalización</h3>
        {[
          { key: "max_population_density", label: "Densidad poblacional" },
          { key: "max_average_income", label: "Ingreso promedio" },
          { key: "max_education_level", label: "Nivel educativo" },
          { key: "max_commercial_presence", label: "Presencia comercial" },
        ].map(({ key, label }) => (
          <div key={key} style={{ display: "flex", alignItems: "center", marginBottom: 10, gap: 12 }}>
            <label style={{ width: 180, fontSize: 14 }}>{label}</label>
            <input
              type="number"
              step="1"
              min="0.01"
              value={config[key]}
              onChange={e => handleChange(key, e.target.value)}
              style={inputStyle}
            />
          </div>
        ))}

        {/* Mensajes */}
        {error && <p style={{ color: "#dc2626", marginTop: 16 }}>{error}</p>}
        {message && <p style={{ color: "#16a34a", marginTop: 16 }}>{message}</p>}

        {/* Botón guardar */}
        <button
          onClick={handleSave}
          disabled={saving || weightsTotal !== 100}
          style={{
            marginTop: 20,
            padding: "10px 24px",
            backgroundColor: weightsTotal === 100 ? "#0d9488" : "#94a3b8",
            color: "white",
            border: "none",
            borderRadius: 8,
            cursor: weightsTotal === 100 ? "pointer" : "not-allowed",
            fontSize: 15,
          }}
        >
          {saving ? "Guardando..." : "Guardar configuración"}
        </button>
      </div>
    </div>
  );
};

const inputStyle = {
  width: 100,
  padding: "6px 10px",
  border: "1px solid #d1d5db",
  borderRadius: 6,
  fontSize: 14,
};

export default ConfigPanel;
