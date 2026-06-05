// Base URL for API
const API_URL = window.location.origin;

// State management
let charts = {
    dashboard: null,
    xgboost: null,
    prophet: null,
    importance: null
};

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    // Initialise Lucide Icons
    lucide.createIcons();
    
    // Set default slider value display
    const slider = document.getElementById('xgb-steps');
    const sliderVal = document.getElementById('xgb-steps-val');
    slider.addEventListener('input', (e) => {
        sliderVal.textContent = `${e.target.value} hrs`;
    });
    
    // Nav Tab handling
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const tabName = item.getAttribute('data-tab');
            switchToTab(tabName);
        });
    });

    // Check API status & load dashboard data
    checkApiStatus();
    
    // Form submissions
    document.getElementById('xgb-auto-form').addEventListener('submit', runXgbAutoPrediction);
    document.getElementById('xgb-manual-form').addEventListener('submit', runXgbManualPrediction);
    document.getElementById('prophet-form').addEventListener('submit', runProphetPrediction);
});

// Switch Tab logic
function switchToTab(tabName) {
    // Update navigation sidebar active class
    document.querySelectorAll('.nav-item').forEach(item => {
        if(item.getAttribute('data-tab') === tabName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Toggle content panes
    document.querySelectorAll('.tab-content').forEach(pane => {
        if(pane.id === `tab-${tabName}`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });

    // Custom Header updates based on tab
    const title = document.getElementById('page-title');
    const subtitle = document.getElementById('page-subtitle');
    
    if (tabName === 'dashboard') {
        title.textContent = 'Panel General';
        subtitle.textContent = 'Monitoreo y predicciones de demanda del Sistema Interconectado Nacional';
    } else if (tabName === 'xgboost') {
        title.textContent = 'Predicción Corto Plazo (XGBoost)';
        subtitle.textContent = 'Simulación horaria autorregresiva con retroalimentación del historial de XM';
    } else if (tabName === 'prophet') {
        title.textContent = 'Planificación Largo Plazo (Prophet)';
        subtitle.textContent = 'Pronóstico de rango temporal agregando estacionalidad diaria, semanal y anual';
    } else if (tabName === 'metrics-info') {
        title.textContent = 'Métricas y Modelamiento';
        subtitle.textContent = 'Resultados de validación cruzada y análisis de importancia de características';
        // Render importance chart once tab is visible (Chart.js needs visible containers for width computation)
        setTimeout(renderImportanceChart, 50);
    }
}

// Check Backend Status
async function checkApiStatus() {
    const apiDot = document.querySelector('#api-status .status-dot');
    const apiText = document.querySelector('#api-status .status-text');
    const xgbDot = document.querySelector('#xgb-status .status-dot');
    const xgbText = document.querySelector('#xgb-status .status-text');
    const prophetDot = document.querySelector('#prophet-status .status-dot');
    const prophetText = document.querySelector('#prophet-status .status-text');

    try {
        const response = await fetch(`${API_URL}/api/v1/health`);
        const data = await response.json();
        
        if (data.status === 'online') {
            apiDot.className = 'status-dot online';
            apiText.textContent = 'Backend Online';
            
            // XGBoost
            if (data.models.xgboost_loaded) {
                xgbDot.className = 'status-dot online';
                xgbText.textContent = 'XGBoost Cargado';
            } else {
                xgbDot.className = 'status-dot offline';
                xgbText.textContent = 'XGBoost No Encontrado';
            }
            
            // Prophet
            if (data.models.prophet_loaded) {
                prophetDot.className = 'status-dot online';
                prophetText.textContent = 'Prophet Cargado';
            } else {
                prophetDot.className = 'status-dot offline';
                prophetText.textContent = 'Prophet No Encontrado';
            }

            // Load metrics & initial dashboard data
            loadMetricsAndDashboard();
        }
    } catch (error) {
        console.error('Error al conectar con la API:', error);
        apiDot.className = 'status-dot offline';
        apiText.textContent = 'Backend Offline';
    }
}

let loadedMetrics = null;

// Fetch and Render Metrics
async function loadMetricsAndDashboard() {
    try {
        const response = await fetch(`${API_URL}/api/v1/metrics`);
        const metrics = await response.json();
        loadedMetrics = metrics;

        // Render card values
        document.getElementById('val-xgb-r2').textContent = metrics.xgboost.metrics.r2.toFixed(4);
        document.getElementById('val-xgb-mae').textContent = Math.round(metrics.xgboost.metrics.mae).toLocaleString() + ' kWh';
        document.getElementById('val-prophet-mape').textContent = (metrics.prophet.metrics.mape_3d * 100).toFixed(1) + '%';

        // Load default dashboard simulation
        loadDefaultDashboardChart();
    } catch (e) {
        console.error("Error al cargar métricas:", e);
    }
}

// Load Default Demo Chart on Dashboard
async function loadDefaultDashboardChart() {
    // Generate a default autoregressive forecast for dashboard show-off
    try {
        const response = await fetch(`${API_URL}/api/v1/predict/xgboost/auto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_time: '2025-11-20T00:00:00',
                steps: 48
            })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const labels = data.predictions.map(p => {
                const d = new Date(p.timestamp);
                return `${d.toLocaleDateString('es-CO', {month:'short', day:'numeric'})} ${d.getHours()}:00`;
            });
            const predicted = data.predictions.map(p => p.predicted_value);
            const actual = data.predictions.map(p => p.actual_value);

            const ctx = document.getElementById('dashboardChart').getContext('2d');
            
            if (charts.dashboard) charts.dashboard.destroy();
            
            charts.dashboard = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Demanda Real (XM)',
                            data: actual,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            borderWidth: 2.5,
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'Predicción XGBoost t+48 (Autoregresivo)',
                            data: predicted,
                            borderColor: '#3b82f6',
                            borderDash: [5, 5],
                            borderWidth: 2,
                            pointStyle: 'circle',
                            pointRadius: 3,
                            fill: false,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.03)' },
                            ticks: { color: '#64748b' }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.03)' },
                            ticks: { 
                                color: '#64748b',
                                callback: function(value) {
                                    return (value / 1e6).toFixed(1) + 'M kWh';
                                }
                            }
                        }
                    }
                }
            });
        }
    } catch(e) {
        console.error("Error al renderizar gráfico por defecto:", e);
    }
}

// Predict short-term (XGBoost Auto)
async function runXgbAutoPrediction(e) {
    e.preventDefault();
    const loader = document.getElementById('xgb-loader');
    loader.style.display = 'flex';

    const startTime = document.getElementById('xgb-start-time').value + ':00';
    const steps = parseInt(document.getElementById('xgb-steps').value);

    try {
        const response = await fetch(`${API_URL}/api/v1/predict/xgboost/auto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_time: startTime,
                steps: steps
            })
        });
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            const labels = data.predictions.map(p => {
                const d = new Date(p.timestamp);
                return `${d.toLocaleDateString('es-CO', {month:'short', day:'numeric'})} ${d.getHours()}:00`;
            });
            const predicted = data.predictions.map(p => p.predicted_value);
            const actual = data.predictions.map(p => p.actual_value);

            // Compute summary metrics
            const maxVal = Math.max(...predicted);
            const minVal = Math.min(...predicted);
            document.getElementById('xgb-max-pred').textContent = Math.round(maxVal).toLocaleString() + ' kWh';
            document.getElementById('xgb-min-pred').textContent = Math.round(minVal).toLocaleString() + ' kWh';
            document.getElementById('xgb-summary-box').style.display = 'flex';

            const ctx = document.getElementById('xgbChart').getContext('2d');
            
            if (charts.xgboost) charts.xgboost.destroy();
            
            charts.xgboost = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Historial Real (XM)',
                            data: actual,
                            borderColor: 'rgba(245, 158, 11, 0.45)',
                            backgroundColor: 'transparent',
                            borderWidth: 1.5,
                            fill: false,
                            tension: 0.1
                        },
                        {
                            label: 'Simulación XGBoost',
                            data: predicted,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 2.5,
                            fill: true,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#94a3b8', font: { family: 'Inter' } }
                        },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.03)' },
                            ticks: { color: '#64748b' }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.03)' },
                            ticks: { 
                                color: '#64748b',
                                callback: function(value) { return (value / 1e6).toFixed(1) + 'M kWh'; }
                            }
                        }
                    }
                }
            });
        } else {
            alert("Error en la predicción: " + data.detail);
        }
    } catch(err) {
        console.error("Error:", err);
        alert("Ocurrió un error al conectar con el servidor.");
    } finally {
        loader.style.display = 'none';
    }
}

// Predict manual input for XGBoost
async function runXgbManualPrediction(e) {
    e.preventDefault();
    
    const payload = {
        hora: parseInt(document.getElementById('man-hora').value),
        dia_semana: parseInt(document.getElementById('man-dia').value),
        mes: parseInt(document.getElementById('man-mes').value),
        tendencia: parseInt(document.getElementById('man-tendencia').value),
        lag_1: parseFloat(document.getElementById('man-lag1').value),
        lag_24: parseFloat(document.getElementById('man-lag24').value),
        lag_168: parseFloat(document.getElementById('man-lag168').value)
    };

    try {
        const response = await fetch(`${API_URL}/api/v1/predict/xgboost/manual`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            const predVal = data.predictions[0].predicted_value;
            alert(`Demanda Predicha: ${Math.round(predVal).toLocaleString()} kWh`);
        } else {
            alert("Error: " + data.detail);
        }
    } catch(err) {
        alert("Error de conexión: " + err.message);
    }
}

// Predict Prophet
async function runProphetPrediction(e) {
    e.preventDefault();
    const loader = document.getElementById('prophet-loader');
    loader.style.display = 'flex';

    const startDate = document.getElementById('prophet-start-date').value;
    const endDate = document.getElementById('prophet-end-date').value;

    try {
        const response = await fetch(`${API_URL}/api/v1/predict/prophet`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate
            })
        });
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            const labels = data.predictions.map(p => {
                const d = new Date(p.timestamp);
                return `${d.toLocaleDateString('es-CO', {month:'short', day:'numeric'})} ${d.getHours()}:00`;
            });
            const predicted = data.predictions.map(p => p.predicted_value);
            const lower = data.predictions.map(p => p.yhat_lower);
            const upper = data.predictions.map(p => p.yhat_upper);
            const actual = data.predictions.map(p => p.actual_value);

            // Summary metrics
            const avgUpper = upper.reduce((a,b) => a+b, 0) / upper.length;
            const avgLower = lower.reduce((a,b) => a+b, 0) / lower.length;
            document.getElementById('prophet-avg-upper').textContent = Math.round(avgUpper).toLocaleString() + ' kWh';
            document.getElementById('prophet-avg-lower').textContent = Math.round(avgLower).toLocaleString() + ' kWh';
            document.getElementById('prophet-summary-box').style.display = 'flex';

            const ctx = document.getElementById('prophetChart').getContext('2d');
            
            if (charts.prophet) charts.prophet.destroy();
            
            charts.prophet = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Límite Superior (yhat_upper)',
                            data: upper,
                            borderColor: 'rgba(16, 185, 129, 0.4)',
                            borderWidth: 1,
                            borderDash: [2, 2],
                            fill: false,
                            pointRadius: 0
                        },
                        {
                            label: 'Límite Inferior (yhat_lower)',
                            data: lower,
                            borderColor: 'rgba(16, 185, 129, 0.2)',
                            borderWidth: 1,
                            fill: '-1', // Fill down to upper dataset
                            backgroundColor: 'rgba(16, 185, 129, 0.03)',
                            pointRadius: 0
                        },
                        {
                            label: 'Predicción Prophet',
                            data: predicted,
                            borderColor: '#10b981',
                            backgroundColor: 'transparent',
                            borderWidth: 2.5,
                            fill: false,
                            tension: 0.2
                        },
                        {
                            label: 'Demanda Real (XM)',
                            data: actual,
                            borderColor: 'rgba(245, 158, 11, 0.75)',
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { 
                                color: '#94a3b8',
                                font: { family: 'Inter' },
                                filter: function(item, chartData) {
                                    // Remove upper/lower bounds from legends to keep it clean
                                    return !item.text.includes('Límite');
                                }
                            }
                        },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.03)' },
                            ticks: { color: '#64748b' }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.03)' },
                            ticks: { 
                                color: '#64748b',
                                callback: function(value) { return (value / 1e6).toFixed(1) + 'M kWh'; }
                            }
                        }
                    }
                }
            });
        } else {
            alert("Error en Prophet: " + data.detail);
        }
    } catch(err) {
        console.error("Error:", err);
        alert("Ocurrió un error al conectar con el servidor.");
    } finally {
        loader.style.display = 'none';
    }
}

// Render Feature Importance Chart
function renderImportanceChart() {
    if (!loadedMetrics || charts.importance) return;

    const importanceData = loadedMetrics.xgboost.feature_importance;
    
    // Sort importance
    const sortedFeatures = Object.entries(importanceData)
        .sort((a, b) => b[1] - a[1]);

    const labels = sortedFeatures.map(item => item[0]);
    const values = sortedFeatures.map(item => item[1]);

    const ctx = document.getElementById('importanceChart').getContext('2d');
    
    charts.importance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Importancia relativa',
                data: values,
                backgroundColor: 'rgba(59, 130, 246, 0.65)',
                borderColor: '#3b82f6',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#64748b' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}
