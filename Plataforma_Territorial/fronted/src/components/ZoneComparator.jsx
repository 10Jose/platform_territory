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
        zone_code: item.zone_code,
        zone_name: item.zone_name,
      }));
      setAvailableZones(zones);
    } catch (err) {
      setError(err.message || 'No se pudieron cargar las zonas.');
    } finally {
      setLoadingZones(false);
    }
  };

  useEffect(() => {
    fetchZones();
  }, []);

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
    return (
      <div className="indicators-loading">
        <div className="spinner"></div>
        <p>Cargando zonas para comparación...</p>
      </div>
    );
  }

  return (
    <div className="comparator-container">
      <div className="comparator-header">
        <h2>Comparador de Zonas</h2>
        <p>Selecciona 2 o más zonas para visualizar indicadores y score lado a lado.</p>
      </div>

      <div className="comparator-controls">
        <label htmlFor="zone-select" className="comparator-label">
          Zonas disponibles (usa Ctrl/Cmd para selección múltiple)
        </label>
        <select
          id="zone-select"
          className="comparator-select"
          multiple
          value={selectedZones}
          onChange={handleSelectionChange}
        >
          {availableZones.map(zone => (
            <option key={zone.zone_code} value={zone.zone_code}>
              {zone.zone_name} ({zone.zone_code})
            </option>
          ))}
        </select>

        <button className="refresh-data-button" onClick={runComparison} disabled={loadingComparison}>
          {loadingComparison ? 'Comparando...' : 'Comparar zonas'}
        </button>
      </div>

      {selectedZones.length < 2 && (
        <div className="comparator-hint">
          Selecciona al menos 2 zonas para habilitar una comparación válida.
        </div>
      )}

      {error && <div className="indicators-error">Error: {error}</div>}

      {comparisonData?.zones?.length > 1 && (
        <>
          <div className="data-table-container comparator-table-wrapper">
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Indicador</th>
                    {comparisonData.zones.map(zone => (
                      <th key={zone.zone_code} className="text-right">
                        {zone.zone_name}
                      </th>
                    ))}
                    <th className="text-right">Variación</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.comparison.map(row => (
                    <tr key={row.metric} className={row.significant_difference ? 'significant-row' : ''}>
                      <td>
                        {row.label}
                        {row.significant_difference && <span className="difference-badge">Dif. &gt; 20%</span>}
                      </td>
                      {comparisonData.zones.map(zone => {
                        const zoneValue = row.values[zone.zone_code];
                        const maxValue = Math.max(...Object.values(row.values).filter(value => typeof value === 'number'));
                        const minValue = Math.min(...Object.values(row.values).filter(value => typeof value === 'number'));
                        const isExtreme = row.significant_difference && (zoneValue === maxValue || zoneValue === minValue);
                        return (
                          <td key={`${row.metric}-${zone.zone_code}`} className={`text-right ${isExtreme ? 'significant-cell' : ''}`}>
                            {Number(zoneValue || 0).toLocaleString()}
                          </td>
                        );
                      })}
                      <td className={`text-right ${row.significant_difference ? 'significant-cell' : ''}`}>
                        {row.variation_pct}%
                      </td>
                    </tr>
                  ))}
                  <tr className="score-row">
                    <td>Score</td>
                    {comparisonData.zones.map(zone => (
                      <td key={`score-${zone.zone_code}`} className="text-right">
                        {zone.score}
                      </td>
                    ))}
                    <td className="text-right">Normalizado</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="comparator-chart">
            <h3>Gráfico comparativo de score</h3>
            <div className="chart-bars">
              {comparisonData.zones.map(zone => (
                <div key={`bar-${zone.zone_code}`} className="chart-bar-item">
                  <div
                    className="chart-bar"
                    style={{ width: `${maxScore > 0 ? (zone.score / maxScore) * 100 : 0}%` }}
                  >
                    {zone.score}
                  </div>
                  <span className="chart-label">{zone.zone_name}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ZoneComparator;
