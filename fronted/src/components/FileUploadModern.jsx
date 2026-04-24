/**
 * Pantalla principal: subida de CSV al BFF, botón HU-07 (sync transformación) y lista de zonas.
 */
import React, { useState, useRef } from 'react';
import './FileUploadModern.css';
import ZonesList from './ZonesList';
import { api } from '../services/api';

const FileUploadModern = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [refreshZones, setRefreshZones] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncTransformResult, setSyncTransformResult] = useState(null);
  const [syncTransformLoading, setSyncTransformLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      const msg = 'Solo se permiten archivos CSV.';
      setError(msg);
      console.error(msg);
      setFile(null);
      return;
    }

    if (selectedFile.size === 0) {
      const msg = 'El archivo está vacío.';
      setError(msg);
      console.error(msg);
      setFile(null);
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      const msg = 'Archivo mayor a 50MB.';
      setError(msg);
      console.error(msg);
      setFile(null);
      return;
    }

    setError(null);
    setFile(selectedFile);
    setResult(null);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      const msg = 'Selecciona un archivo.';
      setError(msg);
      console.error(msg);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.loadFile(file);
      setResult(data);
      setRefreshZones(prev => !prev);
      setSyncing(true);
      setTimeout(() => setSyncing(false), 3000);
    } catch (err) {
      const errorMsg = err.detail || err.message || 'Error al cargar';
      setError(errorMsg);
      console.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleHu07Sync = async () => {
    setSyncTransformLoading(true);
    setSyncTransformResult(null);
    setError(null);
    try {
      const data = await api.syncZonesTransform();
      setSyncTransformResult(data);
      setRefreshZones((prev) => !prev);
    } catch (err) {
      const errorMsg = err.message || 'Error en transformación HU-07';
      setError(errorMsg);
    } finally {
      setSyncTransformLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <main className="main-content">
        <div className="container">

          <h2>Subir archivo CSV</h2>

          <form onSubmit={handleSubmit}>
            <div
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <p>{file ? file.name : 'Arrastra tu archivo aquí'}</p>

              <button type="button" onClick={triggerFileInput}>
                Seleccionar archivo
              </button>

              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>

            {file && (
              <button type="submit">
                {loading ? 'Subiendo...' : 'Subir archivo'}
              </button>
            )}
          </form>

          {error && <p style={{ color: 'red' }}>{error}</p>}

          <div className="flex-center mt-6" style={{ flexDirection: 'column', gap: '0.75rem' }}>
            <p style={{ margin: 0, color: '#475569', fontSize: '0.9rem', textAlign: 'center', maxWidth: '36rem' }}>
              <strong>HU-07 — Transformación:</strong> toma el último dataset válido en ingestion, aplica reglas con Pandas,
              guarda en <code>transformed_zone_data</code> y registra <code>transformation_runs</code> (sin modificar el CSV original).
            </p>
            <button
              type="button"
              className="primary-button"
              onClick={handleHu07Sync}
              disabled={syncTransformLoading}
              style={{ maxWidth: '320px' }}
            >
              <span className="material-symbols-outlined">transform</span>
              {syncTransformLoading ? 'Transformando…' : 'Ejecutar transformación (sync zonas)'}
            </button>
          </div>

          {syncTransformResult && (
            <div className="success-message" style={{ marginTop: '1.25rem' }}>
              <h3>Transformación HU-07 completada</h3>
              <p><strong>Dataset ingestion ID:</strong> {syncTransformResult.dataset_id}</p>
              <p><strong>Transformation run ID:</strong> {syncTransformResult.transformation_run_id}</p>
              <p><strong>Zonas procesadas:</strong> {syncTransformResult.zones_processed}</p>
              <p><strong>Upserts:</strong> {syncTransformResult.upserted}</p>
              <p><strong>Versión reglas:</strong> {syncTransformResult.rules_version}</p>
              <details style={{ marginTop: '0.75rem' }}>
                <summary className="json-summary">Respuesta completa</summary>
                <pre className="json-pre">{JSON.stringify(syncTransformResult, null, 2)}</pre>
              </details>
            </div>
          )}

          {syncing && (
            <div className="syncing-message">
              <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>sync</span>
              Sincronizando zonas con el servidor...
            </div>
          )}

          {result && (
            <div>
              <h3>Resultado:</h3>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}

          <ZonesList refreshTrigger={refreshZones} />
        </div>
      </main>
    </div>
  );
};

export default FileUploadModern;
