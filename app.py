# -*- coding: utf-8 -*-
import os
import datetime
from flask import Flask, jsonify, request, render_template_string, redirect, url_for

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Base de datos de empleados (Añadido "es_admin" para control de acceso)
EMPLEADOS_DB = {
    "105544": {
        "nombre": "Carlos Serrano",
        "cargo": "Coordinador de Operaciones de Seguridad",
        "gerencia": "Gerencia de Seguridad Integral",
        "es_admin": True  # Permiso para ver reportes de incidentes
    },
    "123456": {
        "nombre": "Usuario de Prueba",
        "cargo": "Operador de Monitoreo",
        "gerencia": "Gerencia de Seguridad Integral",
        "es_admin": False
    }
}

# Registro en memoria para almacenar reportes de incidentes
INCIDENTES_DB = []

tz_caracas = datetime.timezone(datetime.timedelta(hours=-4))
now = datetime.datetime.now(tz_caracas)

gps_data = {
    "Unidad-01": {"lat": 10.4765223, "lng": -66.8326641, "speed": 0, "fecha": now.strftime("%H:%M:%S")},
    "Unidad-02": {"lat": 10.4782000, "lng": -66.8341000, "speed": 0, "fecha": now.strftime("%H:%M:%S")},
    "Unidad-03": {"lat": 10.4751000, "lng": -66.8309000, "speed": 0, "fecha": now.strftime("%H:%M:%S")}
}

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Ingreso - Policlínica Metropolitana</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { width: 100vw; min-height: 100vh; background-color: #ffffff; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 20px; position: relative; overflow-x: hidden; }
        .bg-squares { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 1; pointer-events: none; }
        .square { position: absolute; border-radius: 4px; opacity: 0.85; }
        .sq-yellow { background-color: #eab308; }
        .sq-darkblue { background-color: #0f4c5c; }
        .sq-lightblue { background-color: #38bdf8; }
        .sq-gray { background-color: #94a3b8; }
        .sq-1 { top: 15%; right: 8%; width: 32px; height: 32px; transform: rotate(25deg); }
        .sq-2 { top: 28%; right: 12%; width: 25px; height: 25px; transform: rotate(35deg); }
        .sq-3 { top: 38%; left: 4%; width: 38px; height: 38px; transform: rotate(10deg); }
        .sq-4 { top: 48%; right: 6%; width: 35px; height: 35px; transform: rotate(12deg); }
        .sq-5 { top: 58%; left: 5%; width: 42px; height: 42px; transform: rotate(30deg); }
        .sq-6 { top: 10%; right: 15%; width: 32px; height: 32px; }
        .sq-7 { bottom: 20%; left: 10%; width: 25px; height: 25px; }
        .sq-8 { top: 75%; right: 25%; width: 38px; height: 38px; }
        .sq-9 { top: 40%; left: 5%; width: 42px; height: 42px; }
        .logo-img { position: absolute; top: 10px; left: 4px; width: 75px; height: 75px; object-fit: contain; z-index: 10; }
        .top-header { width: 100%; text-align: center; padding-top: 5px; position: relative; z-index: 5; }
        .header-title { font-size: 18px; font-weight: 800; color: #0f172a; line-height: 1.2; }
        .header-subtitle { font-size: 13px; font-weight: 600; color: #475569; margin-top: 2px; }
        .header-system { font-size: 14.5px; font-weight: 700; color: #0284c7; margin-top: 2px; }
        .center-container {
            width: 100%; max-width: 320px; text-align: center; display: flex; flex-direction: column;
            align-items: center; margin: auto; position: relative; z-index: 5;
            background: rgba(255, 255, 255, 0.55); padding: 24px 16px; border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.7); box-shadow: 0 8px 32px rgba(0,0,0,0.06);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        }
        form { width: 100%; }
        .input-group { margin-bottom: 18px; }
        label { display: block; font-size: 12px; font-weight: 700; color: #334155; margin-bottom: 8px; text-align: center; }
        input[type="text"] {
            width: 100%; padding: 14px; border-radius: 10px;
            border: 1.5px solid rgba(2, 132, 199, 0.3); background: rgba(255, 255, 255, 0.65);
            color: #0f172a; font-size: 14px; font-weight: 600; text-align: center; outline: none;
            backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); transition: all 0.3s ease;
        }
        input[type="text"]:focus { border-color: #0284c7; background: rgba(255, 255, 255, 0.85); box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.15); }
        button { width: 100%; padding: 14px; border-radius: 10px; border: none; background: #0284c7; color: #ffffff; font-size: 14px; font-weight: 700; cursor: pointer; box-shadow: 0 3px 10px rgba(2, 132, 199, 0.3); transition: background 0.2s; }
        button:hover { background: #0369a1; }
        .error-message { background-color: rgba(254, 242, 242, 0.85); border: 1px solid #fca5a5; color: #dc2626; font-size: 11px; font-weight: 600; padding: 10px; border-radius: 8px; margin-top: 15px; width: 100%; backdrop-filter: blur(4px); }
    </style>
</head>
<body>
    <div class="bg-squares">
        <div class="square sq-yellow sq-1"></div>
        <div class="square sq-darkblue sq-2"></div>
        <div class="square sq-lightblue sq-3"></div>
        <div class="square sq-yellow sq-4"></div>
        <div class="square sq-darkblue sq-5"></div>
        <div class="square sq-yellow sq-6"></div>
        <div class="square sq-yellow sq-7"></div>
        <div class="square sq-gray sq-8"></div>
        <div class="square sq-gray sq-9"></div>
    </div>
    <img src="/static/logo.png" alt="Logo Policlínica Metropolitana" class="logo-img" />
    <div class="top-header">
        <div class="header-title">Policlínica Metropolitana</div>
        <div class="header-subtitle">Gerencia de Seguridad Integral</div>
        <div class="header-system">Seguimiento de Transporte</div>
    </div>
    <div class="center-container">
        <form method="POST" action="/login">
            <div class="input-group">
                <label for="emp_code">Ingrese su Código de Empleado</label>
                <input type="text" id="emp_code" name="emp_code" placeholder="Ej: 123456" required autofocus autocomplete="off" />
            </div>
            <button type="submit">Ingresar</button>
        </form>
        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>"""

WELCOME_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Bienvenido - Policlínica Metropolitana</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { width: 100vw; min-height: 100vh; background-color: #ffffff; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 24px 20px; position: relative; overflow-x: hidden; }
        .bg-squares { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 1; pointer-events: none; }
        .square { position: absolute; border-radius: 4px; opacity: 0.85; }
        .sq-yellow { background-color: #eab308; }
        .sq-darkblue { background-color: #0f4c5c; }
        .sq-1 { top: 12%; right: 8%; width: 32px; height: 32px; transform: rotate(25deg); }
        .sq-2 { top: 30%; left: 5%; width: 38px; height: 38px; transform: rotate(10deg); }
        .logo-img { position: absolute; top: 10px; left: 4px; width: 75px; height: 75px; object-fit: contain; z-index: 10; }
        .top-header { width: 100%; text-align: center; padding-top: 5px; position: relative; z-index: 5; }
        .header-title { font-size: 18px; font-weight: 800; color: #0f172a; line-height: 1.2; }
        .header-subtitle { font-size: 13px; font-weight: 600; color: #475569; margin-top: 2px; }
        .header-system { font-size: 14.5px; font-weight: 700; color: #0284c7; margin-top: 2px; }
        .welcome-card { width: 100%; max-width: 340px; background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 28px 20px; text-align: center; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); border: 1px solid #f1f5f9; position: relative; z-index: 5; margin: auto; backdrop-filter: blur(8px); }
        .user-avatar { width: 64px; height: 64px; background: #e0f2fe; color: #0284c7; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 800; margin: 0 auto 16px auto; box-shadow: inset 0 0 0 3px #ffffff, 0 4px 12px rgba(2, 132, 199, 0.2); }
        .welcome-label { font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
        .user-name { font-size: 20px; font-weight: 800; color: #0f172a; margin: 4px 0 12px 0; }
        .info-pill { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; margin-bottom: 20px; }
        .user-role { font-size: 13px; font-weight: 700; color: #1e293b; }
        .user-dept { font-size: 12px; font-weight: 600; color: #64748b; margin-top: 2px; }
        .loading-text { font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 14px; }
        .timer-circle { width: 60px; height: 60px; border-radius: 50%; background: #0284c7; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 800; margin: 0 auto; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35); animation: pulse 1s infinite alternate; }
        @keyframes pulse { 0% { transform: scale(0.96); } 100% { transform: scale(1.04); } }
    </style>
</head>
<body>
    <div class="bg-squares">
        <div class="square sq-yellow sq-1"></div>
        <div class="square sq-darkblue sq-2"></div>
    </div>
    <img src="/static/logo.png" alt="Logo Policlínica Metropolitana" class="logo-img" />
    <div class="top-header">
        <div class="header-title">Policlínica Metropolitana</div>
        <div class="header-subtitle">Gerencia de Seguridad Integral</div>
        <div class="header-system">Seguimiento de Transporte</div>
    </div>
    <div class="welcome-card">
        <div class="user-avatar">{{ emp.nombre[0] }}</div>
        <div class="welcome-label">Bienvenido(a)</div>
        <div class="user-name">{{ emp.nombre }}</div>
        <div class="info-pill">
            <div class="user-role">{{ emp.cargo }}</div>
            <div class="user-dept">{{ emp.gerencia }}</div>
        </div>
        <div class="loading-text">Cargando el sistema de monitoreo...</div>
        <div class="timer-circle" id="countdown">5</div>
    </div>
    <script>
        let seconds = 5;
        const timerElement = document.getElementById('countdown');
        const interval = setInterval(() => {
            seconds--;
            if (seconds >= 0) timerElement.textContent = seconds;
            if (seconds === 0) {
                clearInterval(interval);
                window.location.href = "{{ url_for('map_view', code=code) }}";
            }
        }, 1000);
    </script>
</body>
</html>"""

MAP_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>Monitoreo de Transporte - Policlínica Metropolitana</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/openlayers/4.6.5/ol.css" type="text/css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/openlayers/4.6.5/ol.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        html, body { width: 100vw; height: 100vh; overflow: hidden; background: #0f172a; }
        #map { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; z-index: 1; }

        .top-container {
            position: fixed; top: 8px; left: 50%; transform: translateX(-50%);
            width: 94%; max-width: 420px; z-index: 99999;
            display: flex; flex-direction: column; align-items: center; gap: 4px;
        }

        .header-banner {
            width: 100%; background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px; padding: 6px 10px; color: #ffffff;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35); text-align: center;
        }

        .header-line1 { font-size: 12px; font-weight: 800; color: #ffffff; line-height: 1.1; }
        .header-line2 { font-size: 9px; font-weight: 600; color: #94a3b8; margin-top: 1px; }
        .header-line3 { font-size: 10px; font-weight: 700; color: #38bdf8; margin-top: 1px; }

        .stops-panel {
            width: 100%; background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 10px; padding: 5px 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            display: flex; flex-direction: column; align-items: center; gap: 3px;
        }

        .stops-label { font-size: 8.5px; font-weight: 800; color: #f59e0b; text-transform: uppercase; letter-spacing: 0.5px; }
        .stops-bar { display: flex; gap: 5px; justify-content: center; width: 100%; }

        .stop-btn {
            background: rgba(15, 23, 42, 0.90); border: 1px solid rgba(245, 158, 11, 0.4);
            color: #f59e0b; font-weight: 700; font-size: 9.5px;
            padding: 3px 8px; border-radius: 6px; cursor: pointer; user-select: none; transition: all 0.2s ease;
        }
        .stop-btn:active { transform: scale(0.94); background: rgba(245, 158, 11, 0.2); }

        .bottom-controls {
            position: fixed; bottom: 8px; left: 50%; transform: translateX(-50%);
            width: 96%; max-width: 420px; z-index: 99999;
            display: flex; flex-direction: column; gap: 4px; align-items: center;
        }

        .action-bar { display: flex; gap: 5px; justify-content: center; width: 100%; }

        .action-btn {
            background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(10px);
            padding: 4px 8px; border-radius: 6px; font-size: 9px; font-weight: 700; text-decoration: none;
            display: inline-flex; align-items: center; cursor: pointer; transition: all 0.2s;
        }
        .schedule-btn { border: 1px solid rgba(168, 85, 247, 0.5); color: #c084fc; }
        .incident-btn { border: 1px solid rgba(239, 68, 68, 0.5); color: #ef4444; background: rgba(239, 68, 68, 0.1); }
        .survey-btn { border: 1px solid rgba(56, 189, 248, 0.5); color: #38bdf8; }
        .admin-btn { border: 1px solid rgba(234, 179, 8, 0.5); color: #eab308; }

        .units-row { width: 100%; display: flex; gap: 4px; justify-content: space-between; }

        .unit-card {
            flex: 1; background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(56, 239, 125, 0.35); border-radius: 8px; padding: 6px 4px; color: #ffffff;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4); cursor: pointer; user-select: none;
            display: flex; flex-direction: column; justify-content: space-between; text-align: center;
        }
        .unit-card:active { transform: scale(0.97); background: rgba(30, 41, 59, 0.95); }

        .unit-header { display: flex; flex-direction: column; align-items: center; margin-bottom: 2px; }
        .unit-title { font-size: 9.5px; font-weight: 800; color: #ffffff; }
        .unit-status { font-size: 7.5px; color: #38ef7d; font-weight: 800; background: rgba(56, 239, 125, 0.15); padding: 0.5px 4px; border-radius: 3px; border: 1px solid rgba(56, 239, 125, 0.3); margin-top: 1px; }

        .unit-body { display: flex; flex-direction: column; gap: 1px; margin: 3px 0; }
        .unit-target { font-size: 8px; font-weight: 700; color: #f59e0b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
        .unit-eta { font-size: 8.5px; font-weight: 800; color: #38bdf8; }
        .unit-hint { font-size: 6.5px; color: #64748b; margin-top: 1px; text-transform: uppercase; font-weight: 700; }

        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(8px);
            z-index: 999999; display: flex; justify-content: center; align-items: center;
            opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
        }
        .modal-overlay.active { opacity: 1; pointer-events: auto; }

        .modal-box {
            background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(168, 85, 247, 0.4);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6); border-radius: 14px; padding: 16px; width: 90%; max-width: 340px;
            color: #ffffff; text-align: center; transform: scale(0.9); transition: transform 0.3s ease;
        }
        .modal-overlay.active .modal-box { transform: scale(1); }

        .modal-title { font-size: 14px; font-weight: 800; color: #c084fc; margin-bottom: 10px; }
        .modal-title.incident-title { color: #ef4444; }

        .schedule-group { background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 8px; margin-bottom: 8px; text-align: center; }
        .schedule-header { font-weight: 800; font-size: 10.5px; color: #38bdf8; margin-bottom: 4px; text-transform: uppercase; }
        .schedule-list { list-style: none; font-size: 10px; color: #cbd5e1; font-weight: 600; line-height: 1.4; }

        .modal-close-btn {
            margin-top: 6px; width: 100%; padding: 8px; border: none; border-radius: 8px;
            background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ffffff; font-size: 11px; font-weight: 800; cursor: pointer;
        }

        .incident-select, .incident-btn-submit {
            width: 100%; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-size: 11px; font-weight: 700;
        }
        .incident-select { background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(255, 255, 255, 0.2); color: #ffffff; outline: none; }
        .incident-btn-submit { background: #ef4444; color: #ffffff; border: none; cursor: pointer; }
        .incident-btn-submit:hover { background: #dc2626; }
    </style>
</head>
<body>

    <div class="top-container">
        <div class="header-banner">
            <div class="header-line1">Policlínica Metropolitana</div>
            <div class="header-line2">Gerencia de Seguridad Integral</div>
            <div class="header-line3">Monitoreo de Transporte</div>
        </div>

        <div class="stops-panel">
            <div class="stops-label">📍 Seleccione una parada</div>
            <div class="stops-bar">
                <button class="stop-btn" onclick="centerOnStop('stop-clinica')">Clínica</button>
                <button class="stop-btn" onclick="centerOnStop('stop-metro')">Metro</button>
                <button class="stop-btn" onclick="centerOnStop('stop-gama')">Gama</button>
            </div>
        </div>
    </div>

    <div class="bottom-controls">
        <div class="action-bar">
            <button onclick="toggleModal('scheduleModal', true)" class="action-btn schedule-btn">🕒 Horarios</button>
            <button onclick="toggleModal('incidentModal', true)" class="action-btn incident-btn">🚨 Incidente</button>
            <a href="https://forms.gle/MERriZ2iw7zrfcY27" target="_blank" rel="noopener noreferrer" class="action-btn survey-btn">⭐ Encuesta</a>
            {% if emp.es_admin %}
            <a href="{{ url_for('ver_incidentes', code=code) }}" class="action-btn admin-btn">📋 Reportes</a>
            {% endif %}
        </div>

        <div class="units-row">
            <div class="unit-card" onclick="centerOnUnit('Unidad-01')">
                <div class="unit-header">
                    <span class="unit-title">🚐 U-01</span>
                    <span class="unit-status" id="unit-status-1">--</span>
                </div>
                <div class="unit-body">
                    <div class="unit-target" id="next-stop-name-1">➡️ --</div>
                </div>
                <div class="unit-eta" id="next-stop-eta-1">⏱️ --</div>
                <div class="unit-hint">🎯 Centrar</div>
            </div>

            <div class="unit-card" onclick="centerOnUnit('Unidad-02')">
                <div class="unit-header">
                    <span class="unit-title">🚐 U-02</span>
                    <span class="unit-status" id="unit-status-2">--</span>
                </div>
                <div class="unit-body">
                    <div class="unit-target" id="next-stop-name-2">➡️ --</div>
                </div>
                <div class="unit-eta" id="next-stop-eta-2">⏱️ --</div>
                <div class="unit-hint">🎯 Centrar</div>
            </div>

            <div class="unit-card" onclick="centerOnUnit('Unidad-03')">
                <div class="unit-header">
                    <span class="unit-title">🚐 U-03</span>
                    <span class="unit-status" id="unit-status-3">--</span>
                </div>
                <div class="unit-body">
                    <div class="unit-target" id="next-stop-name-3">➡️ --</div>
                </div>
                <div class="unit-eta" id="next-stop-eta-3">⏱️ --</div>
                <div class="unit-hint">🎯 Centrar</div>
            </div>
        </div>
    </div>

    <!-- Modal Horarios -->
    <div class="modal-overlay" id="scheduleModal" onclick="toggleModal('scheduleModal', false)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="modal-title">🕒 Horario de Transporte</div>
            <div class="schedule-group">
                <div class="schedule-header">📅 Lunes a Viernes</div>
                <ul class="schedule-list">
                    <li>☀️ 06:00 a.m. a 09:45 a.m.</li>
                    <li>🌤️ 11:30 a.m. a 02:30 p.m.</li>
                    <li>🌙 04:00 p.m. a 08:30 p.m.</li>
                </ul>
            </div>
            <div class="schedule-group">
                <div class="schedule-header">🎉 Sábados, Domingos y Feriados</div>
                <ul class="schedule-list">
                    <li>☀️ 06:30 a.m. a 09:30 a.m.</li>
                    <li>🌤️ 11:30 a.m. a 02:00 p.m.</li>
                    <li>🌙 04:00 p.m. a 08:00 p.m.</li>
                </ul>
            </div>
            <button class="modal-close-btn" onclick="toggleModal('scheduleModal', false)">Cerrar</button>
        </div>
    </div>

    <!-- Modal Reportar Incidente -->
    <div class="modal-overlay" id="incidentModal" onclick="toggleModal('incidentModal', false)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="modal-title incident-title">🚨 Reportar Incidente</div>
            <form id="incidentForm" onsubmit="submitIncident(event)">
                <select id="inc_unit" class="incident-select" required>
                    <option value="">Seleccione la Unidad...</option>
                    <option value="Unidad-01">Unidad-01</option>
                    <option value="Unidad-02">Unidad-02</option>
                    <option value="Unidad-03">Unidad-03</option>
                </select>

                <select id="inc_type" class="incident-select" required>
                    <option value="">Seleccione Tipo de Incidente...</option>
                    <option value="Unidad Accidentada">Unidad Accidentada</option>
                    <option value="Colisión">Colisión</option>
                    <option value="Riña">Riña</option>
                    <option value="Sobre Carga">Sobre Carga</option>
                </select>

                <button type="submit" class="incident-btn-submit">Enviar Reporte</button>
            </form>
            <button class="modal-close-btn" onclick="toggleModal('incidentModal', false)">Cancelar</button>
        </div>
    </div>

    <div id="map"></div>

    <!-- Variables Jinja2 -->
    <script>
        var userCode = "{{ code }}";
    </script>

    {% raw %}
    <script>
        var inactivityTimer;
        var INACTIVITY_LIMIT = 10 * 60 * 1000;

        function resetInactivityTimer() {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(function() {
                alert("Su sesión ha expirado por inactividad (10 minutos).");
                window.location.href = "/login";
            }, INACTIVITY_LIMIT);
        }

        window.onload = resetInactivityTimer;
        document.onmousemove = resetInactivityTimer;
        document.onkeypress = resetInactivityTimer;
        document.ontouchstart = resetInactivityTimer;
        document.onclick = resetInactivityTimer;

        function toggleModal(modalId, show) {
            var modal = document.getElementById(modalId);
            if (show) modal.classList.add('active');
            else modal.classList.remove('active');
        }

        function submitIncident(e) {
            e.preventDefault();
            var unit = document.getElementById('inc_unit').value;
            var type = document.getElementById('inc_type').value;

            fetch('/api/incidente', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: userCode,
                    unidad: unit,
                    tipo: type
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'OK') {
                    alert('Incidente reportado exitosamente.');
                    toggleModal('incidentModal', false);
                    document.getElementById('incidentForm').reset();
                } else {
                    alert('Error enviando el reporte.');
                }
            })
            .catch(() => alert('Error de conexión.'));
        }

        var unitsCoords = {
            "Unidad-01": { lat: 10.4765223, lon: -66.8326641, speed: 0, rotation: 0 },
            "Unidad-02": { lat: 10.4782000, lon: -66.8341000, speed: 0, rotation: 0 },
            "Unidad-03": { lat: 10.4751000, lon: -66.8309000, speed: 0, rotation: 0 }
        };

        var vanSvg = 'data:image/svg+xml;utf8,' + encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="28" height="28">
                <ellipse cx="32" cy="54" rx="26" ry="6" fill="rgba(0,0,0,0.3)"/>
                <path d="M 10 24 C 10 20, 14 18, 20 18 L 44 18 C 50 18, 54 22, 56 28 L 58 38 C 58 42, 56 46, 52 46 L 12 46 C 8 46, 6 42, 6 36 L 6 28 Z" fill="#FFFFFF" stroke="#1E293B" stroke-width="2.5" stroke-linejoin="round"/>
                <path d="M 42 21 L 52 28 L 42 28 Z" fill="#38BDF8"/>
                <rect x="28" y="21" width="11" height="7" rx="1" fill="#38BDF8"/>
                <rect x="14" y="21" width="11" height="7" rx="1" fill="#38BDF8"/>
                <rect x="55" y="34" width="3" height="5" rx="1" fill="#FACC15"/>
                <rect x="6" y="34" width="3" height="5" rx="1" fill="#EF4444"/>
                <circle cx="18" cy="46" r="6" fill="#0F172A" stroke="#FFFFFF" stroke-width="1.5"/>
                <circle cx="46" cy="46" r="6" fill="#0F172A" stroke="#FFFFFF" stroke-width="1.5"/>
            </svg>
        `);

        function createStopSvg(badgeText) {
            return 'data:image/svg+xml;utf8,' + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="34" height="34">
                    <ellipse cx="32" cy="56" rx="16" ry="5" fill="rgba(0,0,0,0.35)"/>
                    <path d="M 32 4 C 18 4, 8 14, 8 28 C 8 44, 32 60, 32 60 C 32 60, 56 44, 56 28 C 56 14, 46 4, 32 4 Z" fill="#F59E0B" stroke="#FFFFFF" stroke-width="2.5"/>
                    <circle cx="32" cy="26" r="16" fill="#0F172A"/>
                    <text x="32" y="30" font-family="sans-serif" font-size="9.5" font-weight="900" fill="#F59E0B" text-anchor="middle">${badgeText}</text>
                </svg>
            `);
        }

        var unitFeatures = {};
        var unitKeys = ["Unidad-01", "Unidad-02", "Unidad-03"];

        unitKeys.forEach(function(key) {
            var f = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([unitsCoords[key].lon, unitsCoords[key].lat])),
                unitId: key, isUnit: true
            });
            f.setStyle(new ol.style.Style({
                image: new ol.style.Icon({ 
                    anchor: [0.5, 0.5], 
                    src: vanSvg, 
                    scale: 1.0,
                    rotation: 0,
                    rotateWithView: true
                })
            }));
            unitFeatures[key] = f;
        });

        var defaultStops = [
            { id: 'stop-clinica', name: 'Clínica PCM', badge: 'PCM', lon: -66.8326641, lat: 10.4765223 },
            { id: 'stop-metro', name: 'Metro Los Cortijos', badge: 'METRO', lon: -66.8341000, lat: 10.4782000 },
            { id: 'stop-gama', name: 'Gama Expreso', badge: 'GAMA', lon: -66.8309000, lat: 10.4751000 }
        ];

        var savedStops = JSON.parse(localStorage.getItem('pcm_stops_coords_v4') || 'null');
        var stopsData = savedStops || defaultStops;

        var stopFeatures = stopsData.map(function(s) {
            var feature = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([s.lon, s.lat])),
                stopId: s.id, isStop: true
            });
            feature.setStyle(new ol.style.Style({
                image: new ol.style.Icon({ anchor: [0.5, 1.0], src: createStopSvg(s.badge), scale: 1.0 })
            }));
            return feature;
        });

        var vectorSource = new ol.source.Vector({ features: [unitFeatures["Unidad-01"], unitFeatures["Unidad-02"], unitFeatures["Unidad-03"]].concat(stopFeatures) });
        var vectorLayer = new ol.layer.Vector({ source: vectorSource });

        var map = new ol.Map({
            target: 'map',
            layers: [new ol.layer.Tile({ source: new ol.source.OSM() }), vectorLayer],
            view: new ol.View({ center: ol.proj.fromLonLat([-66.8326641, 10.4765223]), zoom: 16.5 }),
            controls: []
        });

        function centerOnUnit(unitKey) {
            var u = unitsCoords[unitKey];
            if (u) map.getView().animate({ center: ol.proj.fromLonLat([u.lon, u.lat]), duration: 600 });
        }

        function centerOnStop(stopId) {
            var stop = stopsData.find(s => s.id === stopId);
            if (stop) map.getView().animate({ center: ol.proj.fromLonLat([stop.lon, stop.lat]), duration: 600 });
        }

        function isTimeInRanges(currentMinutes, ranges) {
            return ranges.some(range => {
                var start = range[0] * 60 + range[1];
                var end = range[2] * 60 + range[3];
                return currentMinutes >= start && currentMinutes <= end;
            });
        }

        function isWorkingHours() {
            var now = new Date();
            var day = now.getDay();
            var minutesNow = now.getHours() * 60 + now.getMinutes();

            if (day >= 1 && day <= 5) {
                return isTimeInRanges(minutesNow, [[6, 0, 9, 45], [11, 30, 14, 30], [16, 0, 20, 30]]);
            } else {
                return isTimeInRanges(minutesNow, [[6, 30, 9, 30], [11, 30, 14, 0], [16, 0, 20, 0]]);
            }
        }

        function updateUnitStatuses() {
            var active = isWorkingHours();
            var statusText = active ? "ACTIVA" : "EN DESCANSO";
            var statusColor = active ? "rgba(56, 239, 125, 0.15)" : "rgba(148, 163, 184, 0.15)";
            var borderColor = active ? "rgba(56, 239, 125, 0.3)" : "rgba(148, 163, 184, 0.3)";
            var textColor = active ? "#38ef7d" : "#94a3b8";

            [1, 2, 3].forEach(function(idx) {
                var el = document.getElementById('unit-status-' + idx);
                if (el) {
                    el.innerText = statusText;
                    el.style.background = statusColor;
                    el.style.borderColor = borderColor;
                    el.style.color = textColor;
                }
            });
        }

        // --- CÁLCULO DE ÁNGULO DE ORIENTACIÓN (BEARING) ---
        function calculateBearing(startLon, startLat, endLon, endLat) {
            var rad = Math.PI / 180;
            var lat1 = startLat * rad;
            var lat2 = endLat * rad;
            var dLon = (endLon - startLon) * rad;

            var y = Math.sin(dLon) * Math.cos(lat2);
            var x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);

            return Math.atan2(y, x); // Retorna el ángulo en radianes
        }

        // --- ANIMACIÓN DE MOVIMIENTO E INTERPOLACIÓN ---
        var activeAnimations = {};

        function animateMarker(unitKey, startLonLat, endLonLat, duration, targetRotation) {
            if (activeAnimations[unitKey]) {
                cancelAnimationFrame(activeAnimations[unitKey]);
            }

            var startTime = Date.now();
            var feature = unitFeatures[unitKey];
            var currentStyle = feature.getStyle();
            var currentRotation = currentStyle.getImage().getRotation() || 0;

            function step() {
                var elapsed = Date.now() - startTime;
                var progress = Math.min(elapsed / duration, 1);

                // Interpolación lineal de la posición
                var currentLon = startLonLat[0] + (endLonLat[0] - startLonLat[0]) * progress;
                var currentLat = startLonLat[1] + (endLonLat[1] - startLonLat[1]) * progress;

                // Interpolación de la rotación
                var rot = currentRotation + (targetRotation - currentRotation) * progress;

                // Actualización de geometría y estilo de la marca
                feature.getGeometry().setCoordinates(ol.proj.fromLonLat([currentLon, currentLat]));
                
                var newStyle = new ol.style.Style({
                    image: new ol.style.Icon({
                        anchor: [0.5, 0.5],
                        src: vanSvg,
                        scale: 1.0,
                        rotation: rot,
                        rotateWithView: true
                    })
                });
                feature.setStyle(newStyle);

                if (progress < 1) {
                    activeAnimations[unitKey] = requestAnimationFrame(step);
                }
            }

            step();
        }

        function updateData() {
            fetch('/api/gps?' + new Date().getTime())
                .then(res => res.json())
                .then(data => {
                    if (data) {
                        unitKeys.forEach(function(key) {
                            if (data[key]) {
                                var uData = data[key];
                                var oldLon = unitsCoords[key].lon;
                                var oldLat = unitsCoords[key].lat;
                                var newLon = uData.lng;
                                var newLat = uData.lat;

                                // Solo animar e interpolar si las coordenadas variaron
                                if (oldLon !== newLon || oldLat !== newLat) {
                                    var bearing = calculateBearing(oldLon, oldLat, newLon, newLat);

                                    // Transición fluida durante 2000 ms
                                    animateMarker(key, [oldLon, oldLat], [newLon, newLat], 2000, bearing);

                                    // Guardar nueva posición de origen
                                    unitsCoords[key].lat = newLat;
                                    unitsCoords[key].lon = newLon;
                                    unitsCoords[key].rotation = bearing;
                                }
                            }
                        });
                    }
                })
                .catch(err => console.error("Error al actualizar posiciones GPS:", err));
        }

        setInterval(updateData, 2500);
        setInterval(updateUnitStatuses, 30000);
        updateData();
        updateUnitStatuses();
    </script>
    {% endraw %}
</body>
</html>"""

INCIDENT_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Reporte de Incidentes - Policlínica Metropolitana</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0f172a; color: #ffffff; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h2 { color: #ef4444; margin-bottom: 20px; text-align: center; font-size: 20px; }
        .back-btn { display: inline-block; padding: 8px 16px; background: rgba(255,255,255,0.1); color: #fff; text-decoration: none; border-radius: 8px; font-size: 12px; margin-bottom: 20px; }
        .card { background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 14px; margin-bottom: 12px; }
        .card-header { display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 6px; margin-bottom: 8px; }
        .unit-name { font-weight: 800; color: #38bdf8; }
        .inc-type { font-weight: 800; color: #ef4444; }
        .details { font-size: 12px; color: #94a3b8; line-height: 1.5; }
        .no-data { text-align: center; color: #64748b; margin-top: 40px; font-weight: 700; }
    </style>
</head>
<body>
    <div class="container">
        <a href="{{ url_for('map_view', code=code) }}" class="back-btn">⬅ Volver al Mapa</a>
        <h2>🚨 Panel de Incidentes Reportados</h2>
        {% if incidentes %}
            {% for item in incidentes %}
            <div class="card">
                <div class="card-header">
                    <span class="unit-name">{{ item.unidad }}</span>
                    <span class="inc-type">{{ item.tipo }}</span>
                </div>
                <div class="details">
                    <div><b>Reportado por:</b> {{ item.reportado_por }} (Código: {{ item.codigo }} )</div>
                    <div><b>Cargo:</b> {{ item.cargo }}</div>
                    <div><b>Hora:</b> {{ item.hora }}</div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-data">No hay reportes registrados hasta el momento.</div>
        {% endif %}
    </div>
</body>
</html>"""

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        code = request.form.get('emp_code', '').strip()
        if code in EMPLEADOS_DB:
            return redirect(url_for('welcome', code=code))
        else:
            error = "Código de empleado no autorizado o incorrecto."
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/welcome/<code>', methods=['GET'])
def welcome(code):
    if code not in EMPLEADOS_DB:
        return redirect(url_for('login'))
    emp = EMPLEADOS_DB[code]
    return render_template_string(WELCOME_TEMPLATE, emp=emp, code=code)

@app.route('/map/<code>', methods=['GET'])
def map_view(code):
    if code not in EMPLEADOS_DB:
        return redirect(url_for('login'))
    emp = EMPLEADOS_DB[code]
    return render_template_string(MAP_TEMPLATE, emp=emp, code=code)

@app.route('/api/gps', methods=['GET'])
def get_gps():
    return jsonify(gps_data)

@app.route('/api/incidente', methods=['POST'])
def registrar_incidente():
    data = request.get_json() or {}
    code = data.get('code')
    unidad = data.get('unidad')
    tipo = data.get('tipo')

    if code in EMPLEADOS_DB and unidad and tipo:
        emp = EMPLEADOS_DB[code]
        nuevo_incidente = {
            "unidad": unidad,
            "tipo": tipo,
            "codigo": code,
            "reportado_por": emp["nombre"],
            "cargo": emp["cargo"],
            "hora": datetime.datetime.now(tz_caracas).strftime("%d/%m/%Y - %I:%M:%S %p")
        }
        INCIDENTES_DB.insert(0, nuevo_incidente)
        return jsonify({"status": "OK"}), 200
    return jsonify({"status": "ERROR"}), 400

@app.route('/admin/incidentes/<code>', methods=['GET'])
def ver_incidentes(code):
    if code not in EMPLEADOS_DB or not EMPLEADOS_DB[code].get("es_admin"):
        return "Acceso denegado. No tiene permisos de administrador.", 403
    return render_template_string(INCIDENT_REPORT_TEMPLATE, incidentes=INCIDENTES_DB, code=code)

@app.route('/traccar', methods=['GET', 'POST'])
def traccar_receiver():
    lat = request.args.get('lat') or request.form.get('lat')
    lng = request.args.get('lon') or request.args.get('lng') or request.form.get('lon') or request.form.get('lng')
    speed = request.args.get('speed', 0)

    if lat and lng:
        try:
            gps_data["Unidad-01"]["lat"] = float(lat)
            gps_data["Unidad-01"]["lng"] = float(lng)
            gps_data["Unidad-01"]["speed"] = float(speed)
            gps_data["Unidad-01"]["fecha"] = datetime.datetime.now(tz_caracas).strftime("%H:%M:%S")
            return "OK", 200
        except Exception as e:
            return f"Error: {str(e)}", 400
    return "Receptor GPS Traccar Activo", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
