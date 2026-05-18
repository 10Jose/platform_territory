import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import '../styles/MLPanel.css';

const MLPanel = () => {
  const [predictions, setPredictions] = useState([]);
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState('');
  const [predictionResult, setPredictionResult] = useState(null);
  const [batchResult, setBatchResult] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [trainLoading, setTrainLoading] = useState(false);
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [cleanupDays, setCleanupDays] = useState(30);
  const [trainAlgorithm, setTrainAlgorithm] = useState('random_forest');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [predData, scoresData, expData, statsData] = await Promise.all([
        api.getMLPredictions().catch(() => []),
        api.getScores().catch(() => []),
        api.getMLExperiments().catch(() => []),
        api.getMLStats().catch(() => null),
      ]);
      setPredictions(predData || []);
      setZones(scoresData || []);
      setModelStatus(expData && expData.length > 0 ? expData[0] : null);
      setStats(statsData);
    } catch (err) {
      // Silencioso - puede no haber modelo entrenado aún
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = () => {
    setError(null);
    setInfo(null);
  };

  // HU-19: entrenar modelo (precondición de HU-20)
  const handleTrainModel = async () => {
    clearMessages();
    setTrainLoading(true);
    try {
      const result = await api.trainModel({
        algorithm: trainAlgorithm,
        target_variable: 'score',
        test_size: 0.2,
      });
      const r2 = result?.metrics?.r2;
      setInfo(
        `Modelo entrenado (${result.algorithm}, ${result.model_version}). ` +
        `R² = ${r2 !== undefined ? r2.toFixed(3) : 'N/A'}.`
      );
      await loadData();
    } catch (err) {
      if (err.message.includes('404') || err.message.includes('No hay datos')) {
        setError('No hay datos de scoring. Ejecuta el cálculo de scoring primero.');
      } else {
        setError('Error al entrenar modelo: ' + err.message);
      }
    } finally {
      setTrainLoading(false);
    }
  };

  // Criterio 1, 2: predicción individual con comparación contra score real
  const handlePredict = async () => {
    clearMessages();
    if (!selectedZone) {
      setError('Selecciona una zona primero');
      return;
    }
    setLoading(true);
    setPredictionResult(null);
    try {
      const result = await api.predictZone(selectedZone);
      setPredictionResult(result);
      await loadData();
    } catch (err) {
      if (err.message.includes('404') || err.message.includes('No hay')) {
        setError('No hay un modelo entrenado. Entrena un modelo primero.');
      } else {
        setError('Error al predecir: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  // Criterio 3: predicción batch
  const handlePredictAll = async () => {
    clearMessages();
    setBatchLoading(true);
    setBatchResult(null);
    try {
      const result = await api.predictAllZones();
      setBatchResult(result);
      setInfo(`Predicción batch completada: ${result.predicted}/${result.total} zonas.`);
      await loadData();
    } catch (err) {
      setError('Error al predecir todas las zonas: ' + err.message);
    } finally {
      setBatchLoading(false);
    }
  };

  // Criterio 6: limpieza
  const handleCleanup = async () => {
    clearMessages();
    if (!window.confirm(
      `¿Eliminar predicciones con más de ${cleanupDays} días? Esta acción no se puede deshacer.`
    )) {
      return;
    }
    setLoading(true);
    try {
      const result = await api.deleteOldPredictions(cleanupDays);
      setInfo(`${result.deleted} predicciones eliminadas (más antiguas que ${result.days} días).`);
      await loadData();
    } catch (err) {
      setError('Error al limpiar predicciones: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getOpportunityClass = (label) => {
    if (label === 'Alta') return 'opportunity-high';
    if (label === 'Media') return 'opportunity-medium';
    if (label === 'Baja') return 'opportunity-low';
    return 'opportunity-unknown';
  };

  const formatNumber = (n, digits = 2) => {
    if (n === null || n === undefined || Number.isNaN(n)) return 'N/A';
    return Number(n).toFixed(digits);
  };

  const handleRefresh = () => {
    clearMessages();
    loadData();
  };

  if (loading && predictions.length === 0 && !batchResult) {
    return (
      <div className="ml-loading">
        <div className="spinner-large"></div>
        <p>Cargando predicciones...</p>
      </div>
    );
  }

  return (
    <div className="ml-container">
      {/* Header */}
      <div className="ml-header">
        <div>
          <h1 className="ml-title">Predicción de Potencial</h1>
          <p className="ml-subtitle">
            Estima el potencial territorial usando inteligencia artificial
          </p>
        </div>
        <button className="btn-refresh" onClick={handleRefresh}>
          <span className="material-symbols-outlined">refresh</span>
          Actualizar
        </button>
      </div>

      {/* Estado del modelo + entrenamiento (HU-19) */}
      <div className="model-status-bar">
        {modelStatus ? (
          <>
            <span className="material-symbols-outlined">check_circle</span>
            <span>
              Modelo activo · algoritmo: <strong>{modelStatus.algorithm}</strong> · R²:{' '}
              <strong>{modelStatus.metric_value?.toFixed(2) ?? 'N/A'}</strong>
            </span>
          </>
        ) : (
          <>
            <span className="material-symbols-outlined">warning</span>
            <span>No hay modelo entrenado. Entrena uno antes de predecir.</span>
          </>
        )}

        <div className="train-controls">
          <select
            value={trainAlgorithm}
            onChange={(e) => setTrainAlgorithm(e.target.value)}
            className="form-select-inline"
          >
            <option value="random_forest">Random Forest</option>
            <option value="linear_regression">Regresión Lineal</option>
          </select>
          <button
            className="btn-train"
            onClick={handleTrainModel}
            disabled={trainLoading}
          >
            <span className="material-symbols-outlined">model_training</span>
            {trainLoading
              ? 'Entrenando...'
              : modelStatus ? 'Reentrenar modelo' : 'Entrenar modelo'}
          </button>
        </div>
      </div>

      {/* Mensajes */}
      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}
      {info && (
        <div className="info-message">
          <span className="material-symbols-outlined">info</span>
          {info}
        </div>
      )}

      {/* Criterio 5: estadísticas */}
      {stats && stats.total > 0 && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Total predicciones</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Alta oportunidad</span>
            <span className="stat-value opportunity-high">
              {stats.by_label?.Alta ?? 0}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Media oportunidad</span>
            <span className="stat-value opportunity-medium">
              {stats.by_label?.Media ?? 0}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Baja oportunidad</span>
            <span className="stat-value opportunity-low">
              {stats.by_label?.Baja ?? 0}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Promedio</span>
            <span className="stat-value">
              {formatNumber(stats.distribution?.mean, 2)}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Última predicción</span>
            <span className="stat-value">
              {stats.last_prediction_at
                ? new Date(stats.last_prediction_at).toLocaleString()
                : 'N/A'}
            </span>
          </div>
        </div>
      )}

      <div className="ml-grid">
        {/* Columna izquierda: predicciones */}
        <div className="ml-left">
          <div className="ml-card">
            <h2>Estimar Potencial de una Zona</h2>
            <p className="card-desc">
              Selecciona una zona o predice todas a la vez
            </p>

            <div className="form-group">
              <label>Zona a analizar</label>
              <select
                value={selectedZone}
                onChange={(e) => setSelectedZone(e.target.value)}
                className="form-select"
              >
                <option value="">Selecciona una zona...</option>
                {zones.map(zone => (
                  <option key={zone.zone_code} value={zone.zone_code}>
                    {zone.zone_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="ml-actions">
              <button
                className="btn-predict"
                onClick={handlePredict}
                disabled={!selectedZone || loading}
              >
                <span className="material-symbols-outlined">query_stats</span>
                {loading ? 'Analizando...' : 'Estimar Potencial'}
              </button>

              {/* Criterio 3 */}
              <button
                className="btn-predict-all"
                onClick={handlePredictAll}
                disabled={batchLoading || zones.length === 0}
              >
                <span className="material-symbols-outlined">batch_prediction</span>
                {batchLoading ? 'Procesando...' : 'Predecir todas las zonas'}
              </button>
            </div>

            {/* Criterio 1, 2: resultado individual con comparación */}
            {predictionResult && (
              <div className="prediction-result-card">
                <h3>{predictionResult.zone_name}</h3>
                <div className="prediction-main">
                  <div className="prediction-score">
                    <span className="pred-label">Potencial Estimado</span>
                    <span className={`pred-value-large ${getOpportunityClass(predictionResult.prediction_label)}`}>
                      {formatNumber(predictionResult.predicted_value, 1)}
                    </span>
                  </div>
                  <div className="prediction-level">
                    <span className="pred-label">Clasificación</span>
                    <span className={`opportunity-badge-large ${getOpportunityClass(predictionResult.prediction_label)}`}>
                      {predictionResult.prediction_label}
                    </span>
                  </div>
                </div>

                {/* Criterio 2: comparación con score real */}
                {predictionResult.actual_score !== null &&
                 predictionResult.actual_score !== undefined && (
                  <div className="comparison-block">
                    <div className="comparison-row">
                      <span>Score real (analítico):</span>
                      <strong>{formatNumber(predictionResult.actual_score, 2)}</strong>
                    </div>
                    <div className="comparison-row">
                      <span>Predicción ML:</span>
                      <strong>{formatNumber(predictionResult.predicted_value, 2)}</strong>
                    </div>
                    <div className="comparison-row">
                      <span>Diferencia (predicción − real):</span>
                      <strong className={predictionResult.difference >= 0 ? 'diff-positive' : 'diff-negative'}>
                        {predictionResult.difference > 0 ? '+' : ''}
                        {formatNumber(predictionResult.difference, 2)}
                      </strong>
                    </div>
                  </div>
                )}

                <p className="prediction-note">
                  * Esta predicción se basa en el modelo entrenado con datos históricos
                </p>
              </div>
            )}

            {/* Criterio 3: resultado batch */}
            {batchResult && (
              <div className="batch-result">
                <h3>Resultado de Predicción Batch</h3>
                <p>
                  {batchResult.predicted} predichas de {batchResult.total}{' '}
                  ({batchResult.failed} fallidas)
                </p>
              </div>
            )}
          </div>

          {/* Criterio 6: cleanup */}
          <div className="ml-card cleanup-card">
            <h3>Limpieza de Predicciones</h3>
            <p className="card-desc">
              Elimina predicciones antiguas para mantener la BD ordenada.
            </p>
            <div className="cleanup-form">
              <label>
                Días mínimos:
                <input
                  type="number"
                  min="0"
                  value={cleanupDays}
                  onChange={(e) => setCleanupDays(Number(e.target.value))}
                  className="form-input"
                />
              </label>
              <button
                className="btn-cleanup"
                onClick={handleCleanup}
                disabled={loading}
              >
                <span className="material-symbols-outlined">delete_sweep</span>
                Eliminar antiguas
              </button>
            </div>
          </div>

          {/* Info card */}
          <div className="ml-card info-card">
            <span className="material-symbols-outlined info-icon">lightbulb</span>
            <div>
              <h3>¿Cómo funciona?</h3>
              <p>
                El sistema analiza patrones en los datos históricos
                (población, ingreso, educación, competencia) para estimar el
                potencial de las zonas. La clasificación (Alta/Media/Baja) usa
                percentiles 25 y 75 sobre las predicciones reales almacenadas.
              </p>
            </div>
          </div>
        </div>

        {/* Columna derecha: historial */}
        <div className="ml-right">
          <div className="ml-card">
            <h2>Predicciones Recientes</h2>
            {predictions.length === 0 ? (
              <div className="empty-section">
                <span className="material-symbols-outlined">query_stats</span>
                <p>No hay predicciones realizadas aún</p>
                <p className="empty-hint">
                  Selecciona una zona y haz clic en "Estimar Potencial"
                </p>
              </div>
            ) : (
              <div className="predictions-list">
                {predictions.slice(0, 20).map(pred => {
                  const actualScore = zones.find(
                    z => z.zone_code === pred.zone_code
                  )?.score;
                  return (
                    <div key={pred.id} className="prediction-item">
                      <div className="pred-header">
                        <span className="pred-zone">{pred.zone_name}</span>
                        <span className={`pred-value ${getOpportunityClass(pred.prediction_label)}`}>
                          {formatNumber(pred.prediction_value, 1)}
                        </span>
                      </div>
                      <div className="pred-footer">
                        <span className={`opportunity-badge ${getOpportunityClass(pred.prediction_label)}`}>
                          {pred.prediction_label}
                        </span>
                        {actualScore !== undefined && (
                          <span className="actual-score">
                            Score real: {formatNumber(actualScore, 1)}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MLPanel;
