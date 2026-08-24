# -*- coding: utf-8 -*-
import os
import datetime
from flask import Flask, jsonify, request, render_template_string, redirect, url_for

app = Flask(__name__, static_url_path='/static', static_folder='static')

EMPLEADOS_DB = {
    "105544": {
        "nombre": "Carlos Serrano",
        "cargo": "Coordinador de Operaciones de Seguridad",
        "gerencia": "Gerencia de Seguridad Integral"
    },
    "123456": {
        "nombre": "Usuario de Prueba",
        "cargo": "Operador de Monitoreo",
        "gerencia": "Gerencia de Seguridad Integral"
    }
}

tz_caracas = datetime.timezone(datetime.timedelta(hours=-4))
now = datetime.datetime.now(tz_caracas)

gps_data = {
    "Unidad-01": {
        "lat": 10.4765223,
        "lng": -66.8326641,
        "speed": 0,
        "fecha": now.strftime("%H:%M:%S")
    },
    "Unidad-02": {
        "lat": 10.4782000,
        "lng": -66.8341000,
        "speed": 0,
        "fecha": now.strftime("%H:%M:%S")
    },
    "Unidad-03": {
        "lat": 10.4751000,
        "lng": -66.8309000,
        "speed": 0,
        "fecha": now.strftime("%H:%M:%S")
    }
}

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Ingreso - Policlínica Metropolitana</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { 
            width: 100vw; min-height: 100vh; background-color: #ffffff; 
            display: flex; flex-direction: column; justify-content: space-between; align-items: center; 
            padding: 20px; position: relative; overflow-x: hidden;
        }
        .bg-squares { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 1; pointer-events: none; }
        .square { position: absolute; border-radius: 4px; opacity: 0.85; }
        .sq-yellow { background-color: #eab308; }
        .sq-darkblue { background-color: #0f4c5c; }
        .sq-lightblue { background-color: #38bdf8; }
        .sq-1 { top: 15%; right: 8%; width: 32px; height: 32px; transform: rotate(25deg); }
        .sq-2 { top: 28%; right: 12%; width: 25px; height: 25px; transform: rotate(35deg); }
        .sq-3 { top: 38%; left: 4%; width: 38px; height: 38px; transform: rotate(10deg); }
        .sq-4 { top: 48%; right: 6%; width: 35px; height: 35px; transform: rotate(12deg); }
        .sq-5 { top: 58%; left: 5%; width: 42px; height: 42px; transform: rotate(30deg); }
        .logo-img { position: absolute; top: 10px; left: 4px; width: 75px; height: 75px; object-fit: contain; z-index: 10; }
        .top-header { width: 100%; text-align: center; padding-top: 5px; position: relative; z-index: 5; }
        .header-title { font-size: 18px; font-weight: 800; color: #0f172a; line-height: 1.2; }
        .header-subtitle { font-size: 13px; font-weight: 600; color: #475569; margin-top: 2px; }
        .header-system { font-size: 14.5px; font-weight: 700; color: #0284c7; margin-top: 2px; }
        .center-container { 
            width: 100%; max-width: 320px; text-align: center; display: flex; flex-direction: column; 
            align-items: center; margin: auto; position: relative; z-index: 5; background: rgba(255, 255, 255, 0.92); 
            padding: 20px 10px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); backdrop-filter: blur(5px);
        }
        form { width: 100%; }
        .input-group { margin-bottom: 18px; }
        label { display: block; font-size: 12px; font-weight: 700; color: #334155; margin-bottom: 8px; text-align: center; }
        input[type="text"] { width: 100%; padding: 14px; border-radius: 10px; border: 2px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 14px; text-align: center; outline: none; }
        input[type="text"]:focus { border-color: #0284c7; }
        button { width: 100%; padding: 14px; border-radius: 10px; border: none; background: #0284c7; color: #ffffff; font-size: 14px; font-weight: 700; cursor: pointer; box-shadow: 0 3px 10px rgba(2, 132, 199, 0.3); }
        .error-message { background-color: #fef2f2; border: 1px solid #fca5a5; color: #dc2626; font-size: 11px; font-weight: 600; padding: 10px; border-radius: 8px; margin-top: 15px; width: 100%; }
    </style>
</head>
<body>
    <div class="bg-squares">
        <div class="square sq-yellow sq-1"></div>
        <div class="square sq-darkblue sq-2"></div>
        <div class="square sq-lightblue sq-3"></div>
        <div class="square sq-yellow sq-4"></div>
        <div class="square sq-darkblue sq-5"></div>
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
    <div></div>
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
        .sq-lightblue { background-color: #38bdf8; }
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
    <div></div>
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
            width: 100%;
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px; padding: 6px 10px; color: #ffffff;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35); text-align: center;
        }

        .header-line1 { font-size: 12px; font-weight: 800; color: #ffffff; line-height: 1.1; }
        .header-line2 { font-size: 9px; font-weight: 600; color: #94a3b8; margin-top: 1px; }
        .header-line3 { font-size: 10px; font-weight: 700; color: #38bdf8; margin-top: 1px; }
        .header-line4 { font-size: 8.5px; font-weight: 500; color: #cbd5e1; margin-top: 2px; display: inline-block; background: rgba(255,255,255,0.08); padding: 1px 6px; border-radius: 6px; }

        .stops-panel {
            width: 100%;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 10px; padding: 5px 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            display: flex; flex-direction: column; align-items: center; gap: 3px;
        }

        .stops-label { font-size: 8.5px; font-weight: 800; color: #f59e0b; text-transform: uppercase; letter-spacing: 0.5px; }
        .stops-bar { display: flex; gap: 5px; justify-content: center; width: 100%; }

        .stop-btn {
            background: rgba(15, 23, 42, 0.90);
            border: 1px solid rgba(245, 158, 11, 0.4);
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
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(10px);
            padding: 4px 8px; border-radius: 6px; font-size: 9px; font-weight: 700; text-decoration: none;
            display: inline-flex; align-items: center; cursor: pointer; transition: all 0.2s;
        }
        .schedule-btn { border: 1px solid rgba(168, 85, 247, 0.5); color: #c084fc; }
        .incident-btn { border: 1px solid rgba(239, 68, 68, 0.5); color: #ef4444; }
        .survey-btn { border: 1px solid rgba(56, 189, 248, 0.5); color: #38bdf8; }

        .units-row {
            width: 100%; display: flex; gap: 4px; justify-content: space-between;
        }

        .unit-card {
            flex: 1; background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(56, 239, 125, 0.35);
            border-radius: 8px; padding: 6px 4px; color: #ffffff;
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
        .schedule-group { background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 8px; margin-bottom: 8px; text-align: center; }
        .schedule-header { font-weight: 800; font-size: 10.5px; color: #38bdf8; margin-bottom: 4px; text-transform: uppercase; }
        .schedule-list { list-style: none; font-size: 10px; color: #cbd5e1; font-weight: 600; line-height: 1.4; }

        .modal-close-btn {
            margin-top: 2px; width: 100%; padding: 8px; border: none; border-radius: 8px;
            background: rgba(168, 85, 247, 0.2); border: 1px solid rgba(168, 85, 247, 0.5);
            color: #c084fc; font-size: 11px; font-weight: 800; cursor: pointer;
        }
    </style>
</head>
<body>

    <div class="top-container">
        <div class="header-banner">
            <div class="header-line1">Policlínica Metropolitana</div>
            <div class="header-line2">Gerencia de Seguridad Integral</div>
            <div class="header-line3">Monitoreo de Transporte</div>
            <div class="header-line4">Última act: <span id="fecha">--:--:--</span></div>
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
            <button onclick="toggleModal(true)" class="action-btn schedule-btn">🕒 Horarios</button>
            <a href="#" id="incident-link" target="_blank" class="action-btn incident-btn">🚨 Incidente</a>
            <a href="#" id="survey-link" target="_blank" class="action-btn survey-btn">⭐ Encuesta</a>
        </div>

        <div class="units-row">
            <div class="unit-card" onclick="centerOnUnit('Unidad-01')">
                <div class="unit-header">
                    <span class="unit-title">🚐 U-01</span>
                    <span class="unit-status">EN LÍNEA</span>
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
                    <span class="unit-status">EN LÍNEA</span>
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
                    <span class="unit-status">EN LÍNEA</span>
                </div>
                <div class="unit-body">
                    <div class="unit-target" id="next-stop-name-3">➡️ --</div>
                </div>
                <div class="unit-eta" id="next-stop-eta-3">⏱️ --</div>
                <div class="unit-hint">🎯 Centrar</div>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="scheduleModal" onclick="toggleModal(false)">
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

            <button class="modal-close-btn" onclick="toggleModal(false)">Cerrar</button>
        </div>
    </div>

    <div id="map"></div>

    {% raw %}
    <script>
        // --- CONTROL DE INACTIVIDAD (10 MINUTOS) ---
        var inactivityTimer;
        var INACTIVITY_LIMIT = 10 * 60 * 1000; // 10 minutos en milisegundos

        function resetInactivityTimer() {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(function() {
                alert("Su sesión ha expirado por inactividad (10 minutos).");
                window.location.href = "/login";
            }, INACTIVITY_LIMIT);
        }

        // Detectar cualquier interacción del usuario
        window.onload = resetInactivityTimer;
        document.onmousemove = resetInactivityTimer;
        document.onkeypress = resetInactivityTimer;
        document.ontouchstart = resetInactivityTimer;
        document.onclick = resetInactivityTimer;
        document.onscroll = resetInactivityTimer;

        var unitsCoords = {
            "Unidad-01": { lat: 10.4765223, lon: -66.8326641, speed: 0 },
            "Unidad-02": { lat: 10.4782000, lon: -66.8341000, speed: 0 },
            "Unidad-03": { lat: 10.4751000, lon: -66.8309000, speed: 0 }
        };

        function toggleModal(show) {
            var modal = document.getElementById('scheduleModal');
            if (show) modal.classList.add('active');
            else modal.classList.remove('active');
        }

        var vanSvg = 'data:image/svg+xml;utf8,' + encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="26" height="26">
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
                unitId: key,
                isUnit: true
            });
            f.setStyle(new ol.style.Style({
                image: new ol.style.Icon({ anchor: [0.5, 0.5], src: vanSvg, scale: 1.0 })
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
                stopId: s.id,
                isStop: true
            });
            feature.setStyle(new ol.style.Style({
                image: new ol.style.Icon({ anchor: [0.5, 1.0], src: createStopSvg(s.badge), scale: 1.0 })
            }));
            return feature;
        });

        var allFeatures = [unitFeatures["Unidad-01"], unitFeatures["Unidad-02"], unitFeatures["Unidad-03"]].concat(stopFeatures);
        var vectorSource = new ol.source.Vector({ features: allFeatures });
        var vectorLayer = new ol.layer.Vector({ source: vectorSource });

        var map = new ol.Map({
            target: 'map',
            layers: [
                new ol.layer.Tile({ source: new ol.source.OSM() }),
                vectorLayer
            ],
            view: new ol.View({
                center: ol.proj.fromLonLat([-66.8326641, 10.4765223]),
                zoom: 16.5
            }),
            controls: []
        });

        var selectInteraction = new ol.interaction.Select({ filter: f => f.get('isStop') === true });
        var translateInteraction = new ol.interaction.Translate({ features: selectInteraction.getFeatures() });

        map.addInteraction(selectInteraction);
        map.addInteraction(translateInteraction);

        translateInteraction.on('translateend', function(e) {
            e.features.forEach(function(feature) {
                if (feature.get('isStop')) {
                    var coords = ol.proj.toLonLat(feature.getGeometry().getCoordinates());
                    var stopId = feature.get('stopId');
                    var match = stopsData.find(s => s.id === stopId);
                    if (match) {
                        match.lon = coords[0];
                        match.lat = coords[1];
                        localStorage.setItem('pcm_stops_coords_v4', JSON.stringify(stopsData));
                    }
                }
            });
            updateAllEtas();
        });

        function centerOnUnit(unitKey) {
            var u = unitsCoords[unitKey];
            if (u) {
                map.getView().animate({ center: ol.proj.fromLonLat([u.lon, u.lat]), duration: 600 });
            }
        }

        function centerOnStop(stopId) {
            var stop = stopsData.find(s => s.id === stopId);
            if (stop) map.getView().animate({ center: ol.proj.fromLonLat([stop.lon, stop.lat]), duration: 600 });
        }

        function getDistanceMeters(lat1, lon1, lat2, lon2) {
            var R = 6371000;
            var dLat = (lat2 - lat1) * Math.PI / 180;
            var dLon = (lon2 - lon1) * Math.PI / 180;
            var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        }

        function updateAllEtas() {
            unitKeys.forEach(function(key, index) {
                var u = unitsCoords[key];
                var idx = index + 1;
                if (!stopsData || stopsData.length === 0) return;
                var closestStop = null;
                var minDistance = Infinity;

                stopsData.forEach(function(stop) {
                    var dist = getDistanceMeters(u.lat, u.lon, stop.lat, stop.lon);
                    if (dist < minDistance) {
                        minDistance = dist;
                        closestStop = stop;
                    }
                });

                if (closestStop) {
                    document.getElementById('next-stop-name-' + idx).innerText = '➡️ ' + closestStop.name;
                    if (minDistance < 35) {
                        document.getElementById('next-stop-eta-' + idx).innerText = '⏱️ ¡En parada!';
                    } else {
                        var effectiveSpeed = u.speed > 5 ? u.speed : 20;
                        var timeMinutes = Math.round(((minDistance / 1000) / effectiveSpeed) * 60);
                        document.getElementById('next-stop-eta-' + idx).innerText = '⏱️ ' + (timeMinutes <= 1 ? '<1 min' : '~' + timeMinutes + 'm');
                    }
                }
            });
        }

        function updateData() {
            fetch('/api/gps?' + new Date().getTime())
                .then(res => res.json())
                .then(data => {
                    if (data) {
                        unitKeys.forEach(function(key, index) {
                            if (data[key]) {
                                var uData = data[key];
                                unitsCoords[key].lat = uData.lat;
                                unitsCoords[key].lon = uData.lng;
                                unitsCoords[key].speed = uData.speed;

                                document.getElementById('fecha').innerText = uData.fecha;

                                unitFeatures[key].getGeometry().setCoordinates(ol.proj.fromLonLat([uData.lng, uData.lat]));
                            }
                        });
                        updateAllEtas();
                    }
                })
                .catch(err => console.log(err));
        }

        setInterval(updateData, 2500);
        updateData();
        setTimeout(() => { map.updateSize(); }, 300);
    </script>
    {% endraw %}
</body>
</html>
"""

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
    return render_template_string(MAP_TEMPLATE)

@app.route('/api/gps', methods=['GET'])
def get_gps():
    return jsonify(gps_data)

@app.route('/traccar', methods=['GET', 'POST'])
@app.route('/api/gps', methods=['POST'])
def update_gps():
    unit_id = request.args.get('unit') or request.form.get('unit') or 'Unidad-01'
    lat = request.args.get('lat') or request.form.get('lat')
    lng = request.args.get('lon') or request.form.get('lng') or request.form.get('lon') or request.form.get('lng')
    speed = request.args.get('speed') or request.form.get('speed') or 0
    timestamp = request.args.get('timestamp') or request.form.get('timestamp')

    if not lat and request.is_json:
        data = request.get_json(silent=True) or {}
        unit_id = data.get('unit', 'Unidad-01')
        lat = data.get('lat') or data.get('latitude')
        lng = data.get('lon') or data.get('lng') or data.get('longitude')
        speed = data.get('speed', 0)
        timestamp = data.get('timestamp') or data.get('time')

    if unit_id not in gps_data:
        unit_id = 'Unidad-01'

    if lat and lng:
        try:
            speed_kmh = round(float(speed) * 1.852, 1) if float(speed) < 100 else round(float(speed), 1)
            if timestamp:
                try:
                    dt_utc = datetime.datetime.fromtimestamp(int(timestamp), datetime.timezone.utc)
                    fecha_fmt = dt_utc.astimezone(tz_caracas).strftime("%H:%M:%S")
                except ValueError:
                    fecha_fmt = datetime.datetime.now(tz_caracas).strftime("%H:%M:%S")
            else:
                fecha_fmt = datetime.datetime.now(tz_caracas).strftime("%H:%M:%S")

            gps_data[unit_id] = {
                'lat': float(lat),
                'lng': float(lng),
                'speed': speed_kmh,
                'fecha': fecha_fmt
            }
            return "OK", 200
        except ValueError:
            pass

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
