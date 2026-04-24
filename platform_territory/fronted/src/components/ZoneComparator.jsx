import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';

const ZoneComparator = () => {
  const [availableZones, setAvailableZones] = useState([]);
  const [selectedZones, setSelectedZones] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [loadingZones, setLoadingZones] = useState(true);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [error, setError] = useState(null);

  const fetchZones = async () => {
    setLoadingZones(true);
    setError(null);
    try {
      const indicators = await api.getIndicators();
      const zones = (indicators || []).map(item => ({
        zone_code: item.zone_code || item.zone_name || item.id,
        zone_name: item.zone_name || item.zone_code || `Zona ${item.id}`,
      }));
      setAvailableZones(zones);
    } catch (err) {
      setError(err.message || 'No se pudieron cargar las zonas.');
    } finally {
      setLoadingZones(false);
    }
  };

  useEffect(() => { fetchZones(); }, []);

  const handleSelectionChange = (event) => {
    const values = Array.from(event.target.selectedOptions).map(option => option.value);
    setSelectedZones(values);
    setComparisonData(null);
    setError(null);
  };

  const runComparison = async () => {
    if (selectedZones.length < 2) {
      setError('Selecciona al menos 2 zonas para comparar.');
      return;
    }
    setLoadingComparison(true);
    setError(null);
    try {
      const data = await api.compareZones(selectedZones);
      setComparisonData(data);
    } catch (err) {
      setError(err.message || 'No se pudo comparar las zonas.');
      setComparisonData(null);
    } finally {
      setLoadingComparison(false);
    }
  };

  const maxScore = useMemo(() => {
    if (!comparisonData?.zones?.length) return 0;
    return Math.max(...comparisonData.zones.map(zone => zone.score || 0));
  }, [comparisonData]);

  if (loadingZones) {
    return <div style={{ padding: 30 }}>Cargando zonas para comparación...</div>;
  }

  return (
    <div style={{ padding: 30, backgroundColor: '#f4f6f8' }}>
      <h2 style={{ marginBottom: 10, color: '#0f172a' }}>Comparador de Zonas</h2>
      <p style={{ color: '#64748b', marginBottom: 16 }}>Selecciona 2 o más zonas (Ctrl/Cmd + click).</p>

      <select
        multiple
        value={selectedZones}
        onChange={handleSelectionChange}
        style={{ width: '100%', maxWidth: 400, height: 150, padding: 8, borderRadius: 8, border: '1px solid #d1d5db', marginBottom: 12 }}
      >
        {availableZones.map(zone => (
          <option key={zone.zone_code} value={zone.zone_code}>
            {zone.zone_name} ({zone.zone_code})
          </option>
        ))}
      </select>

      <br />
      <button
        onClick={runComparison}
        disabled={loadingComparison || selectedZones.length < 2}
        style={{
          padding: '10px 24px', backgroundColor: selectedZones.length >= 2 ? '#0d9488' : '#94a3b8',
          color: 'white', border: 'none', borderRadius: 8, cursor: selectedZones.length >= 2 ? 'pointer' : 'not-allowed', fontSize: 15, marginBottom: 16,
        }}
      >
        {loadingComparison ? 'Comparando...' : 'Comparar zonas'}
      </button>

      {selectedZones.length < 2 && selectedZones.length > 0 && (
        <p style={{ color: '#f59e0b' }}>Selecciona al menos 2 zonas para habilitar la comparación.</p>
      )}

      {error && <p style={{ color: '#dc2626' }}>Error: {error}</p>}

      {comparisonData?.zones?.length > 1 && (
        <>
          <div style={{ overflowX: 'auto', backgroundColor: 'white', borderRadius: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)', padding: 16, marginBottom: 20 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                  <th style={thStyle}>Indicador</th>
                  {comparisonData.zones.map(zone => (
                    <th key={zone.zone_code} style={{ ...thStyle, textAlign: 'right' }}>{zone.zone_name}</th>
                  ))}
                  <th style={{ ...thStyle, textAlign: 'right' }}>Variación</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.comparison.map(row => (
                  <tr key={row.metric} style={{ borderBottom: '1px solid #f1f5f9', backgroundColor: row.significant_difference ? '#fef3c7' : 'transparent' }}>
                    <td style={tdStyle}>
                      {row.label}
                      {row.significant_difference && <span style={{ marginLeft: 8, fontSize: 11, backgroundColor: '#f59e0b', color: 'white', padding: '2px 6px', borderRadius: 4 }}>Dif. &gt; 20%</span>}
                    </td>
                    {comparisonData.zones.map(zone => (
                      <td key={`${row.metric}-${zone.zone_code}`} style={{ ...tdStyle, textAlign: 'right' }}>
                        {Number(row.values[zone.zone_code] || 0).toLocaleString()}
                      </td>
                    ))}
                    <td style={{ ...tdStyle, textAlign: 'right', fontWeight: row.significant_difference ? 'bold' : 'normal', color: row.significant_difference ? '#dc2626' : '#64748b' }}>
                      {row.variation_pct}%
                    </td>
                  </tr>
                ))}
                <tr style={{ borderTop: '2px solid #0d9488', fontWeight: 'bold' }}>
                  <td style={tdStyle}>Score</td>
                  {comparisonData.zones.map(zone => (
                    <td key={`score-${zone.zone_code}`} style={{ ...tdStyle, textAlign: 'right' }}>{zone.score}</td>
                  ))}
                  <td style={{ ...tdStyle, textAlign: 'right', color: '#64748b' }}>Normalizado</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ backgroundColor: 'white', borderRadius: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)', padding: 16 }}>
            <h3 style={{ color: '#0f172a', marginBottom: 12 }}>Gráfico comparativo de score</h3>
            {comparisonData.zones.map(zone => (
              <div key={`bar-${zone.zone_code}`} style={{ display: 'flex', alignItems: 'center', marginBottom: 8, gap: 10 }}>
                <span style={{ width: 100, fontSize: 13 }}>{zone.zone_name}</span>
                <div style={{ flex: 1, backgroundColor: '#e2e8f0', borderRadius: 6, height: 28 }}>
                  <div style={{
                    width: `${maxScore > 0 ? (zone.score / maxScore) * 100 : 0}%`,
                    backgroundColor: '#0d9488', borderRadius: 6, height: 28,
                    display: 'flex', alignItems: 'center', paddingLeft: 8, color: 'white', fontSize: 13, fontWeight: 'bold',
                  }}>
                    {zone.score}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

const thStyle = { padding: '10px 12px', textAlign: 'left', fontSize: 13, color: '#475569' };
const tdStyle = { padding: '10px 12px', fontSize: 14 };

export default ZoneComparator;
