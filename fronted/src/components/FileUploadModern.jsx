<<<<<<< HEAD
=======
/**
 * Pantalla principal: subida de CSV al BFF, botón HU-07 (sync transformación) y lista de zonas.
 */
>>>>>>> origin/Miguel
import React, { useState, useRef } from 'react';
import './FileUploadModern.css';
import ZonesList from './ZonesList';
import { api } from '../services/api';
import { useError } from '../App';

const FileUploadModern = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [refreshZones, setRefreshZones] = useState(false);
  const [syncing, setSyncing] = useState(false);
<<<<<<< HEAD
=======
  const [syncTransformResult, setSyncTransformResult] = useState(null);
  const [syncTransformLoading, setSyncTransformLoading] = useState(false);
>>>>>>> origin/Miguel
  const fileInputRef = useRef(null);
  const { showError } = useError();

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
      showError(msg);
      setFile(null);
      return;
    }

    if (selectedFile.size === 0) {
      const msg = 'El archivo está vacío (0 bytes). Por favor selecciona un archivo con datos.';
      setError(msg);
      showError(msg);
      setFile(null);
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      const msg = 'El archivo excede el tamaño máximo permitido de 50MB.';
      setError(msg);
      showError(msg);
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
      const msg = 'Por favor selecciona un archivo.';
      setError(msg);
      showError(msg);
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
      const errorMsg = err.detail || err.message || 'Error al cargar el archivo';
      setError(errorMsg);
      showError(errorMsg, err.status ? `Código: ${err.status}` : null);
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

<<<<<<< HEAD
=======
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
      showError(errorMsg);
    } finally {
      setSyncTransformLoading(false);
    }
  };

>>>>>>> origin/Miguel
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="header">
        <nav className="nav">
          <div className="logo">Plataforma Territorial</div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Hero */}
          <div className="hero">
            <h1>Analítica Territorial</h1>
            <p>Carga tu archivo CSV con datos territoriales y obtén análisis inteligentes para tu negocio.</p>
          </div>

          {/* Upload Zone */}
          <form onSubmit={handleSubmit}>
            <div
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="upload-content">
                <div className="icon-circle">
                  <span className="material-symbols-outlined upload-icon">cloud_upload</span>
                </div>
                <div>
                  <div className="upload-text">
                    {file ? file.name : 'Arrastra y suelta tu archivo .csv aquí'}
                  </div>
                  <div className="upload-subtext">
                    {file ? `${(file.size / 1024).toFixed(2)} KB` : 'o haz clic en el botón para buscar'}
                  </div>
                </div>
                <button
                  type="button"
                  className="primary-button"
                  onClick={triggerFileInput}
                  disabled={loading}
                >
                  <span className="material-symbols-outlined">upload_file</span>
                  {loading ? 'Subiendo...' : 'Seleccionar archivo'}
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden-input"
                disabled={loading}
              />
            </div>

            {/* Submit Button */}
            {file && (
              <div className="flex-center mt-6">
                <button
                  type="submit"
                  disabled={loading}
                  className="submit-button"
                >
                  {loading ? 'Procesando...' : 'Subir archivo'}
                </button>
              </div>
            )}
          </form>

          {/* Meta Info */}
          <div className="meta-info">
            <span className="badge">Formatos soportados: .csv</span>
            <span className="separator">•</span>
            <span className="size-info">Tamaño máximo: 50MB</span>
          </div>

<<<<<<< HEAD
=======
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

>>>>>>> origin/Miguel
          {/* Mensaje de sincronización */}
          {syncing && (
            <div className="syncing-message">
              <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>sync</span>
              Sincronizando zonas con el servidor...
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Result Display */}
          {result && (
            <div className="success-message">
              <h3>{result.status === 'already_loaded' ? '⚠️ Archivo ya cargado' : '✅ Carga exitosa:'}</h3>
              <p><strong>Archivo:</strong> {result.filename}</p>
              <p><strong>ID:</strong> {result.id}</p>
              <p><strong>Total filas:</strong> {result.rows}</p>
              <p><strong>Filas válidas:</strong> {result.valid_rows}</p>
              <p><strong>Filas inválidas:</strong> {result.invalid_rows}</p>
              {result.message && <p><strong>Mensaje:</strong> {result.message}</p>}

              {result.errors && result.errors.length > 0 && (
                <div className="error-summary">
                  <details>
                    <summary>
                      ⚠️ Ver errores detallados ({result.errors.length} fila(s) con problemas)
                    </summary>
                    <div className="error-container">
                      {result.errors.map((err, idx) => (
                        <div key={idx} className="error-item">
                          <div className="error-title">
                            🔴 Fila {err.row + 1}
                          </div>
                          <ul className="error-list">
                            {err.errors.map((error, i) => (
                              <li key={i}>{error}</li>
                            ))}
                          </ul>
                          <details>
                            <summary className="error-data-summary">
                              📄 Mostrar datos originales
                            </summary>
                            <pre className="error-data-pre">
                              {JSON.stringify(err.row_data, null, 2)}
                            </pre>
                          </details>
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}

              <details style={{ marginTop: '1rem' }}>
                <summary className="json-summary">
                  📦 Ver respuesta JSON completa
                </summary>
                <pre className="json-pre">{JSON.stringify(result, null, 2)}</pre>
              </details>
            </div>
          )}

          <ZonesList refreshTrigger={refreshZones} />
        </div>
      </main>

      {/* Background Decorations */}
      <div className="bg-decoration"></div>
      <div className="bg-decoration-left"></div>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="copyright">© 2026 Todos los derechos reservados.</div>
          <div className="footer-links">
            <button
              onClick={() => alert('Política de Privacidad - Próximamente')}
              className="link-button"
            >
              Política de Privacidad
            </button>
            <button
              onClick={() => alert('Términos de Servicio - Próximamente')}
              className="link-button"
            >
              Términos de Servicio
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default FileUploadModern;