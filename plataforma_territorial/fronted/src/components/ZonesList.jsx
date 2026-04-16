import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './FileUploadModern.css';

const ZonesList = ({ refreshTrigger }) => {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchZones = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getZones(0, 100);
      setZones(data.zones || []);
    } catch (err) {
      console.error('Error fetching zones:', err);
      setError(err.message || 'Error al cargar zonas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchZones();
  }, [refreshTrigger]);

  if (loading) {
    return (
      <div className="zones-section">
        <p className="zones-loading">Cargando zonas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="zones-section">
        <p className="zones-error">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="zones-section">
      <div className="zones-header">
        <h3 className="zones-title">📌 Zonas disponibles</h3>
        <button onClick={fetchZones} disabled={loading} className="refresh-button">
          {loading ? 'Cargando...' : '🔄 Actualizar'}
        </button>
      </div>
      {zones.length === 0 ? (
        <p className="zones-empty">No hay zonas disponibles. Por favor, carga un archivo CSV válido.</p>
      ) : (
        <ul className="zones-list">
          {zones.map((zone, idx) => (
            <li key={idx} className="zone-item">
              <strong>{zone.name}</strong>
              {zone.code && <span className="zone-code"> (Código: {zone.code})</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ZonesList;