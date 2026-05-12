#!/usr/bin/env python3
"""
Doureios Ippos — Web GUI (Flask + SocketIO)
Επαγγελματικό web interface για ethical hacking
"""

import os
import sys
import json
import datetime
import subprocess
import threading
import shutil
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_socketio import SocketIO, emit

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from nlp_engine import detect_intent, needs_clarification, build_confirmation
from report_generator import generate_report, get_reports_list, REPORTS_DIR

app = Flask(__name__)
app.config['SECRET_KEY'] = 'doureios-ippos-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Session storage
session_data = {
    "history": [],
    "last_scan_output": "",
    "last_scan_type": "",
    "last_target": "",
    "operator": "Operator",
}

TOOLS = [
    "nmap","hydra","john","nikto","sqlmap","gobuster",
    "dirb","tshark","tcpdump","aircrack-ng","netdiscover",
    "enum4linux","whois","dig","netcat","msfconsole",
]

def check_tools():
    return {t: bool(shutil.which(t)) for t in TOOLS}

# ─────────────────────────────────────────────────────────────
#  HTML TEMPLATE — Full professional UI
# ─────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Δούρειος Ίππος — Ethical Hacking Assistant</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

  :root {
    --gold:      #C8940E;
    --gold-lt:   #F0C840;
    --gold-dk:   #8A5C04;
    --blue:      #1B2A6B;
    --blue-lt:   #2A3F9F;
    --bg:        #07070F;
    --bg2:       #0D0D1C;
    --bg3:       #111128;
    --border:    rgba(200,148,14,0.25);
    --border-lt: rgba(200,148,14,0.5);
    --text:      #D4D4E8;
    --text-dim:  #7878A0;
    --green:     #22CC66;
    --red:       #CC3333;
    --cyan:      #22CCCC;
  }

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ── HEADER ── */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 24px;
    background: linear-gradient(90deg, var(--bg2) 0%, #0A0A18 50%, var(--bg2) 100%);
    border-bottom: 1px solid var(--border-lt);
    flex-shrink: 0;
  }
  .header-logo {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .header-logo img {
    height: 52px;
    width: 52px;
    object-fit: contain;
    filter: drop-shadow(0 0 8px rgba(200,148,14,0.5));
  }
  .header-logo-text h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: var(--gold);
    letter-spacing: 3px;
    line-height: 1.1;
    text-shadow: 0 0 20px rgba(200,148,14,0.4);
  }
  .header-logo-text p {
    font-size: 11px;
    color: var(--text-dim);
    letter-spacing: 2px;
    text-transform: uppercase;
  }
  .header-status {
    display: flex;
    align-items: center;
    gap: 18px;
  }
  .status-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-dim);
    letter-spacing: 1px;
    text-transform: uppercase;
  }
  .status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
    animation: pulse 2s infinite;
  }
  .status-dot.offline { background: var(--red); box-shadow: 0 0 6px var(--red); }
  @keyframes pulse {
    0%,100% { opacity:1; }
    50% { opacity:0.5; }
  }
  .time-display {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: var(--gold);
    letter-spacing: 1px;
  }

  /* ── MAIN LAYOUT ── */
  .main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* ── LEFT SIDEBAR ── */
  .sidebar {
    width: 240px;
    background: var(--bg2);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    overflow-y: auto;
  }
  .sidebar-section {
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
  }
  .sidebar-title {
    font-family: 'Orbitron', monospace;
    font-size: 9px;
    color: var(--gold);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }
  .tool-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--text-dim);
  }
  .tool-status {
    width: 6px; height: 6px;
    border-radius: 50%;
  }
  .tool-status.ok { background: var(--green); box-shadow: 0 0 4px var(--green); }
  .tool-status.missing { background: var(--red); }

  .quick-cmd {
    display: block;
    padding: 6px 10px;
    margin: 3px 0;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 11px;
    color: var(--text-dim);
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    width: 100%;
    font-family: 'Rajdhani', sans-serif;
  }
  .quick-cmd:hover {
    border-color: var(--gold);
    color: var(--gold);
    background: rgba(200,148,14,0.08);
  }
  .quick-cmd .cmd-icon { margin-right: 6px; }

  /* ── CENTER CHAT ── */
  .chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    scroll-behavior: smooth;
  }
  .chat-messages::-webkit-scrollbar { width: 4px; }
  .chat-messages::-webkit-scrollbar-track { background: var(--bg); }
  .chat-messages::-webkit-scrollbar-thumb { background: var(--border-lt); border-radius: 2px; }

  /* Messages */
  .msg {
    display: flex;
    gap: 12px;
    max-width: 90%;
    animation: fadeIn 0.3s ease;
  }
  @keyframes fadeIn { from { opacity:0; transform: translateY(8px); } to { opacity:1; transform:none; } }

  .msg.user { align-self: flex-end; flex-direction: row-reverse; }
  .msg.system { align-self: flex-start; }
  .msg.output { align-self: flex-start; max-width: 100%; width: 100%; }

  .msg-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
  }
  .msg.system .msg-avatar {
    background: linear-gradient(135deg, var(--gold-dk), var(--gold));
    border: 1px solid var(--gold);
    box-shadow: 0 0 10px rgba(200,148,14,0.3);
  }
  .msg.user .msg-avatar {
    background: linear-gradient(135deg, var(--blue), var(--blue-lt));
    border: 1px solid var(--blue-lt);
  }

  .msg-bubble {
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.5;
  }
  .msg.system .msg-bubble {
    background: var(--bg3);
    border: 1px solid var(--border);
    color: var(--text);
    border-top-left-radius: 2px;
  }
  .msg.user .msg-bubble {
    background: linear-gradient(135deg, var(--blue), var(--blue-lt));
    border: 1px solid var(--blue-lt);
    color: #fff;
    border-top-right-radius: 2px;
  }
  .msg.clarify .msg-bubble {
    border-color: var(--gold);
    background: rgba(200,148,14,0.08);
  }
  .msg-time {
    font-size: 10px;
    color: var(--text-dim);
    margin-top: 4px;
    font-family: 'Share Tech Mono', monospace;
  }

  /* Terminal output */
  .terminal-block {
    background: #050510;
    border: 1px solid var(--border);
    border-left: 3px solid var(--gold);
    border-radius: 6px;
    padding: 14px 16px;
    width: 100%;
  }
  .terminal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }
  .terminal-title {
    font-family: 'Orbitron', monospace;
    font-size: 10px;
    color: var(--gold);
    letter-spacing: 2px;
  }
  .terminal-actions {
    display: flex;
    gap: 8px;
  }
  .terminal-btn {
    padding: 3px 10px;
    font-size: 10px;
    border: 1px solid var(--border-lt);
    background: transparent;
    color: var(--text-dim);
    cursor: pointer;
    border-radius: 3px;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 1px;
    transition: all 0.2s;
  }
  .terminal-btn:hover { border-color: var(--gold); color: var(--gold); }
  .terminal-body {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #A0FFB0;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 400px;
    overflow-y: auto;
    line-height: 1.6;
  }
  .terminal-body::-webkit-scrollbar { width: 3px; }
  .terminal-body::-webkit-scrollbar-thumb { background: var(--border-lt); }

  /* Consent dialog */
  .consent-dialog {
    background: var(--bg3);
    border: 1px solid var(--gold);
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
  }
  .consent-title {
    color: var(--gold);
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    margin-bottom: 8px;
  }
  .consent-info { font-size: 13px; margin-bottom: 12px; }
  .consent-target { color: var(--cyan); font-weight: 600; }
  .consent-btns { display: flex; gap: 10px; }
  .btn-consent-yes {
    padding: 7px 20px;
    background: linear-gradient(135deg, #1A4A1A, #225522);
    border: 1px solid var(--green);
    color: var(--green);
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 1px;
    transition: all 0.2s;
  }
  .btn-consent-yes:hover { background: rgba(34,204,102,0.2); }
  .btn-consent-no {
    padding: 7px 20px;
    background: transparent;
    border: 1px solid var(--red);
    color: var(--red);
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Rajdhani', sans-serif;
    font-size: 13px;
    letter-spacing: 1px;
    transition: all 0.2s;
  }
  .btn-consent-no:hover { background: rgba(204,51,51,0.1); }

  /* ── INPUT AREA ── */
  .input-area {
    padding: 14px 20px;
    background: var(--bg2);
    border-top: 1px solid var(--border);
    flex-shrink: 0;
  }
  .input-row {
    display: flex;
    gap: 10px;
    align-items: flex-end;
  }
  .input-wrapper {
    flex: 1;
    position: relative;
  }
  .lang-badge {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 10px;
    color: var(--text-dim);
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
    pointer-events: none;
  }
  #userInput {
    width: 100%;
    padding: 12px 60px 12px 16px;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
    outline: none;
    transition: border-color 0.2s;
    resize: none;
    min-height: 46px;
    max-height: 120px;
  }
  #userInput:focus { border-color: var(--gold); }
  #userInput::placeholder { color: var(--text-dim); }

  .btn-send {
    padding: 12px 20px;
    background: linear-gradient(135deg, var(--gold-dk), var(--gold));
    border: none;
    border-radius: 8px;
    color: var(--bg);
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .btn-send:hover { filter: brightness(1.2); transform: translateY(-1px); }
  .btn-send:active { transform: translateY(0); }
  .btn-send:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  .input-hint {
    font-size: 11px;
    color: var(--text-dim);
    margin-top: 6px;
    letter-spacing: 0.5px;
  }

  /* ── RIGHT PANEL ── */
  .right-panel {
    width: 220px;
    background: var(--bg2);
    border-left: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    overflow-y: auto;
  }
  .panel-section {
    padding: 14px 14px;
    border-bottom: 1px solid var(--border);
  }
  .panel-title {
    font-family: 'Orbitron', monospace;
    font-size: 9px;
    color: var(--gold);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .report-item {
    padding: 6px 8px;
    margin: 3px 0;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 10px;
    color: var(--text-dim);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }
  .report-item a {
    color: var(--cyan);
    text-decoration: none;
    font-size: 10px;
  }
  .report-item a:hover { color: var(--gold); }

  .stat-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .stat-label { color: var(--text-dim); }
  .stat-value { color: var(--gold); font-family: 'Share Tech Mono', monospace; }

  /* Loading animation */
  .typing-indicator {
    display: flex;
    gap: 5px;
    padding: 10px 14px;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 12px;
    width: fit-content;
  }
  .typing-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--gold);
    animation: typing 1.2s infinite;
  }
  .typing-dot:nth-child(2) { animation-delay: 0.2s; }
  .typing-dot:nth-child(3) { animation-delay: 0.4s; }
  @keyframes typing {
    0%,60%,100% { opacity:0.2; transform: scale(1); }
    30% { opacity:1; transform: scale(1.3); }
  }

  /* Scrollbar global */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border-lt); border-radius: 3px; }

  /* Responsive */
  @media (max-width: 900px) {
    .sidebar, .right-panel { display: none; }
  }

  .gold { color: var(--gold); }
  .green { color: var(--green); }
  .red { color: var(--red); }
  .cyan { color: var(--cyan); }
  strong { color: var(--gold-lt); }
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-logo">
    <img src="/logo" alt="Δούρειος Ίππος" onerror="this.style.display='none'">
    <div class="header-logo-text">
      <h1>ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ</h1>
      <p>Ethical Hacking Assistant v2.0</p>
    </div>
  </div>
  <div class="header-status">
    <div class="status-badge">
      <div class="status-dot" id="connDot"></div>
      <span id="connStatus">ΣΥΝΔΕΔΕΜΕΝΟΣ</span>
    </div>
    <div class="time-display" id="clock">00:00:00</div>
  </div>
</div>

<!-- MAIN -->
<div class="main">

  <!-- LEFT SIDEBAR -->
  <div class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-title">⚙ Εργαλεία / Tools</div>
      <div id="toolsList"></div>
    </div>
    <div class="sidebar-section">
      <div class="sidebar-title">⚡ Γρήγορες Εντολές</div>
      <button class="quick-cmd" onclick="sendQuick('σκάναρε το localhost')"><span class="cmd-icon">🔍</span>Scan localhost</button>
      <button class="quick-cmd" onclick="sendQuick('σκάναρε το 192.168.1.0/24')"><span class="cmd-icon">🌐</span>Scan LAN</button>
      <button class="quick-cmd" onclick="sendQuick('βοήθεια')"><span class="cmd-icon">❓</span>Βοήθεια</button>
      <button class="quick-cmd" onclick="sendQuick('εργαλεία')"><span class="cmd-icon">🛠</span>Εργαλεία</button>
      <button class="quick-cmd" onclick="sendQuick('δημιούργησε report')"><span class="cmd-icon">📄</span>PDF Report</button>
    </div>
    <div class="sidebar-section">
      <div class="sidebar-title">📊 Στατιστικά</div>
      <div class="stat-row"><span class="stat-label">Σαρώσεις</span><span class="stat-value" id="statScans">0</span></div>
      <div class="stat-row"><span class="stat-label">Reports</span><span class="stat-value" id="statReports">0</span></div>
      <div class="stat-row"><span class="stat-label">Session</span><span class="stat-value" id="statTime">00:00</span></div>
    </div>
  </div>

  <!-- CHAT -->
  <div class="chat-area">
    <div class="chat-messages" id="chatMessages"></div>
    <div class="input-area">
      <div class="input-row">
        <div class="input-wrapper">
          <textarea id="userInput" placeholder="Γράψε εντολή στα Ελληνικά ή English... (Enter για αποστολή)" rows="1"></textarea>
          <span class="lang-badge" id="langBadge">EL</span>
        </div>
        <button class="btn-send" id="sendBtn" onclick="sendMessage()">ΑΠΟΣΤΟΛΗ</button>
      </div>
      <div class="input-hint">⚠ Μόνο για εξουσιοδοτημένα συστήματα &nbsp;|&nbsp; Ctrl+Enter για νέα γραμμή &nbsp;|&nbsp; Enter για αποστολή</div>
    </div>
  </div>

  <!-- RIGHT PANEL -->
  <div class="right-panel">
    <div class="panel-section">
      <div class="panel-title">📁 Reports</div>
      <div id="reportsList"><div style="font-size:11px;color:var(--text-dim)">Δεν υπάρχουν reports ακόμα</div></div>
    </div>
    <div class="panel-section">
      <div class="panel-title">🕐 Ιστορικό</div>
      <div id="historyList"></div>
    </div>
  </div>

</div>

<script>
const socket = io();
let scanCount = 0, reportCount = 0;
const startTime = Date.now();
let pendingConsent = null;

// ── CLOCK ──
setInterval(() => {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toTimeString().split(' ')[0];
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const m = Math.floor(elapsed/60).toString().padStart(2,'0');
  const s = (elapsed%60).toString().padStart(2,'0');
  document.getElementById('statTime').textContent = `${m}:${s}`;
}, 1000);

// ── CONNECTION ──
socket.on('connect', () => {
  document.getElementById('connDot').classList.remove('offline');
  document.getElementById('connStatus').textContent = 'ΣΥΝΔΕΔΕΜΕΝΟΣ';
  socket.emit('init');
});
socket.on('disconnect', () => {
  document.getElementById('connDot').classList.add('offline');
  document.getElementById('connStatus').textContent = 'ΑΠΟΣΥΝΔΕΔΕΜΕΝΟΣ';
});

// ── INIT ──
socket.on('init_data', data => {
  renderTools(data.tools);
  renderReports(data.reports);
  addSystemMessage(
    '🐴 Καλώς ήρθες στον <strong>Δούρειο Ίππο v2.0</strong>!<br>' +
    'Γράψε εντολή στα <span class="gold">Ελληνικά</span> ή <span class="cyan">English</span>.<br>' +
    'Π.χ. <em>"σκάναρε το 192.168.1.1"</em> ή <em>"scan 192.168.1.1"</em>'
  );
});

// ── TOOLS ──
function renderTools(tools) {
  const el = document.getElementById('toolsList');
  el.innerHTML = Object.entries(tools).map(([name, ok]) =>
    `<div class="tool-item">
      <span>${name}</span>
      <div class="tool-status ${ok?'ok':'missing'}" title="${ok?'Εγκατεστημένο':'Λείπει'}"></div>
    </div>`
  ).join('');
}

// ── REPORTS ──
function renderReports(reports) {
  const el = document.getElementById('reportsList');
  if (!reports || reports.length === 0) {
    el.innerHTML = '<div style="font-size:11px;color:var(--text-dim)">Δεν υπάρχουν reports ακόμα</div>';
    return;
  }
  el.innerHTML = reports.slice(0,5).map(r => {
    const name = r.split('/').pop().split('\\').pop();
    return `<div class="report-item">
      <span style="font-size:9px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${name}</span>
      <a href="/download_report?path=${encodeURIComponent(r)}" target="_blank">⬇</a>
    </div>`;
  }).join('');
  reportCount = reports.length;
  document.getElementById('statReports').textContent = reportCount;
}

// ── LANGUAGE DETECTION ──
document.getElementById('userInput').addEventListener('input', function() {
  const text = this.value;
  const greekChars = (text.match(/[\u0370-\u03FF\u1F00-\u1FFF]/g)||[]).length;
  const badge = document.getElementById('langBadge');
  badge.textContent = greekChars > 2 ? 'EL' : 'EN';
  // Auto-resize
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// ── ENTER KEY ──
document.getElementById('userInput').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ── SEND MESSAGE ──
function sendMessage() {
  const input = document.getElementById('userInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = 'auto';
  addUserMessage(text);
  showTyping();
  socket.emit('user_message', { text });
  document.getElementById('sendBtn').disabled = true;
}

function sendQuick(cmd) {
  document.getElementById('userInput').value = cmd;
  sendMessage();
}

// ── SOCKET EVENTS ──
socket.on('system_message', data => {
  hideTyping();
  document.getElementById('sendBtn').disabled = false;
  if (data.type === 'clarify') {
    addClarifyMessage(data.message);
  } else {
    addSystemMessage(data.message);
  }
});

socket.on('consent_required', data => {
  hideTyping();
  document.getElementById('sendBtn').disabled = false;
  pendingConsent = data;
  addConsentDialog(data);
});

socket.on('scan_output', data => {
  hideTyping();
  document.getElementById('sendBtn').disabled = false;
  addTerminalOutput(data.title, data.output, data.scan_type);
  scanCount++;
  document.getElementById('statScans').textContent = scanCount;
  addToHistory(data.title);
});

socket.on('report_ready', data => {
  hideTyping();
  document.getElementById('sendBtn').disabled = false;
  addSystemMessage(`📄 <span class="green">Report δημιουργήθηκε!</span><br><a href="/download_report?path=${encodeURIComponent(data.path)}" target="_blank" style="color:var(--cyan)">⬇ Κατέβασε: ${data.filename}</a>`);
  socket.emit('get_reports');
});

// ── SCAN OPTIONS ──
socket.on('scan_options', data => {
  hideTyping();
  document.getElementById('sendBtn').disabled = false;
  addScanOptions(data);
});

socket.on('reports_list', data => {
  renderReports(data.reports);
});

socket.on('error_msg', data => {
  hideTyping();
  document.getElementById('sendBtn').disabled = false;
  addSystemMessage(`<span class="red">⚠ ${data.message}</span>`);
});

// ── CONSENT ──
function handleConsent(approved) {
  if (!pendingConsent) return;
  document.querySelectorAll('.consent-dialog').forEach(d => d.remove());
  if (approved) {
    addSystemMessage('<span class="green">✓ Εξουσιοδότηση επιβεβαιώθηκε. Εκτελώ...</span>');
    showTyping();
    document.getElementById('sendBtn').disabled = true;
    socket.emit('consent_response', { approved: true, action: pendingConsent.action });
  } else {
    addSystemMessage('<span class="red">✗ Ακυρώθηκε.</span>');
    socket.emit('consent_response', { approved: false });
  }
  pendingConsent = null;
}

// ── UI HELPERS ──

function addScanOptions(data) {
  const time = new Date().toLocaleTimeString('el-GR', {hour:'2-digit', minute:'2-digit'});
  const opts = data.options.map((o,i) => 
    `<button class="quick-cmd" style="margin:4px 0;width:100%;text-align:left" 
      onclick="selectScanOption(${i+1}, '${escHtml(data.action)}', '${escHtml(data.target||'')}')">
      <span style="color:var(--gold);margin-right:8px">${i+1}</span> ${o}
    </button>`
  ).join('');
  appendMsg(`
    <div class="msg system clarify">
      <div class="msg-avatar">🐴</div>
      <div>
        <div class="msg-bubble">
          <strong>${data.title}</strong><br><br>${opts}
        </div>
        <div class="msg-time">${time}</div>
      </div>
    </div>`);
}

function selectScanOption(choice, action, target) {
  document.querySelectorAll('.msg.system.clarify:last-child').forEach(el => el.style.opacity='0.5');
  addUserMessage(`Επιλογή ${choice}`);
  showTyping();
  document.getElementById('sendBtn').disabled = true;
  socket.emit('scan_option_selected', { choice, action, target });
}

function addUserMessage(text) {
  const time = new Date().toLocaleTimeString('el-GR', {hour:'2-digit', minute:'2-digit'});
  appendMsg(`
    <div class="msg user">
      <div>
        <div class="msg-bubble">${escHtml(text)}</div>
        <div class="msg-time" style="text-align:right">${time}</div>
      </div>
      <div class="msg-avatar">👤</div>
    </div>`);
}

function addSystemMessage(html) {
  const time = new Date().toLocaleTimeString('el-GR', {hour:'2-digit', minute:'2-digit'});
  appendMsg(`
    <div class="msg system">
      <div class="msg-avatar">🐴</div>
      <div>
        <div class="msg-bubble">${html}</div>
        <div class="msg-time">${time}</div>
      </div>
    </div>`);
}

function addClarifyMessage(html) {
  const time = new Date().toLocaleTimeString('el-GR', {hour:'2-digit', minute:'2-digit'});
  appendMsg(`
    <div class="msg system clarify">
      <div class="msg-avatar">🐴</div>
      <div>
        <div class="msg-bubble">💬 ${html}</div>
        <div class="msg-time">${time}</div>
      </div>
    </div>`);
}

function addTerminalOutput(title, output, scanType) {
  const id = 'term_' + Date.now();
  appendMsg(`
    <div class="msg output">
      <div class="terminal-block">
        <div class="terminal-header">
          <span class="terminal-title">▶ ${escHtml(title)}</span>
          <div class="terminal-actions">
            <button class="terminal-btn" onclick="copyOutput('${id}')">COPY</button>
            <button class="terminal-btn" onclick="requestReport('${escHtml(title)}', '${id}')">PDF REPORT</button>
          </div>
        </div>
        <div class="terminal-body" id="${id}">${escHtml(output)}</div>
      </div>
    </div>`);
}

function addConsentDialog(data) {
  appendMsg(`
    <div class="msg output">
      <div class="consent-dialog">
        <div class="consent-title">⚠ ΕΠΙΒΕΒΑΙΩΣΗ ΕΞΟΥΣΙΟΔΟΤΗΣΗΣ</div>
        <div class="consent-info">
          Στόχος: <span class="consent-target">${escHtml(data.target||'N/A')}</span><br>
          Ενέργεια: <span class="gold">${escHtml(data.description||'')}</span><br><br>
          <strong>Έχεις εξουσιοδότηση για αυτό το σύστημα;</strong>
        </div>
        <div class="consent-btns">
          <button class="btn-consent-yes" onclick="handleConsent(true)">✓ ΝΑΙ, ΕΧΩΑΔΕΙΑ</button>
          <button class="btn-consent-no" onclick="handleConsent(false)">✗ ΑΚΥΡΩΣΗ</button>
        </div>
      </div>
    </div>`);
}

function showTyping() {
  const existing = document.getElementById('typingIndicator');
  if (existing) return;
  const div = document.createElement('div');
  div.id = 'typingIndicator';
  div.className = 'msg system';
  div.innerHTML = `
    <div class="msg-avatar">🐴</div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  document.getElementById('chatMessages').appendChild(div);
  scrollBottom();
}

function hideTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function appendMsg(html) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.innerHTML = html;
  container.appendChild(div.firstElementChild);
  scrollBottom();
}

function scrollBottom() {
  const el = document.getElementById('chatMessages');
  el.scrollTop = el.scrollHeight;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function copyOutput(id) {
  const el = document.getElementById(id);
  if (el) navigator.clipboard.writeText(el.textContent);
}

function requestReport(title, termId) {
  socket.emit('generate_report', { title, output_id: termId });
}

function addToHistory(title) {
  const el = document.getElementById('historyList');
  const item = document.createElement('div');
  item.style.cssText = 'font-size:10px;color:var(--text-dim);padding:3px 0;border-bottom:1px solid var(--border);';
  item.textContent = '▸ ' + title.substring(0, 28);
  el.insertBefore(item, el.firstChild);
  if (el.children.length > 10) el.lastChild.remove();
}
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/logo')
def serve_logo():
    logo_path = Path(__file__).parent / 'logo.png'
    if logo_path.exists():
        return send_file(str(logo_path), mimetype='image/png')
    return '', 404

@app.route('/download_report')
def download_report():
    path = request.args.get('path', '')
    if path and Path(path).exists() and path.endswith('.pdf'):
        return send_file(path, as_attachment=True)
    return 'Not found', 404

# ─────────────────────────────────────────────────────────────
#  SOCKET EVENTS
# ─────────────────────────────────────────────────────────────
@socketio.on('init')
def handle_init():
    tools = check_tools()
    reports = get_reports_list()
    emit('init_data', {'tools': tools, 'reports': reports})

@socketio.on('get_reports')
def handle_get_reports():
    emit('reports_list', {'reports': get_reports_list()})

@socketio.on('user_message')
def handle_message(data):
    text = data.get('text', '').strip()
    if not text:
        return

    # NLP processing
    result = detect_intent(text)
    intent_id = result['intent_id']
    lang = result['language']
    target = result['target']

    # Add to history
    session_data['history'].append({
        'text': text, 'intent': intent_id,
        'time': datetime.datetime.now().isoformat()
    })

    # Check for clarification needed
    clarify = needs_clarification(result)
    if clarify:
        emit('system_message', {'message': clarify, 'type': 'clarify'})
        return

    # Handle intent
    if intent_id == 'exit':
        emit('system_message', {'message': '🐴 Αντίο! Stay ethical. Κλείσε το tab για έξοδο.'})

    elif intent_id == 'show_help':
        emit('system_message', {'message': get_help_html(lang)})

    elif intent_id == 'show_tools':
        tools = check_tools()
        ok = [t for t, v in tools.items() if v]
        missing = [t for t, v in tools.items() if not v]
        msg = f'<span class="green">✓ Εγκατεστημένα ({len(ok)}):</span> {", ".join(ok)}<br>'
        if missing:
            msg += f'<span class="red">✗ Λείπουν ({len(missing)}):</span> {", ".join(missing)}'
        emit('system_message', {'message': msg})

    elif intent_id == 'generate_report':
        if session_data.get('last_scan_output'):
            path = generate_report(
                scan_type=session_data.get('last_scan_type', 'Scan'),
                target=session_data.get('last_target', ''),
                output=session_data['last_scan_output'],
            )
            if path and not path.startswith('[✗]'):
                emit('report_ready', {
                    'path': path,
                    'filename': Path(path).name
                })
            else:
                emit('error_msg', {'message': path})
        else:
            emit('system_message', {'message': 'Δεν υπάρχει scan output για report. Κάνε πρώτα μια σάρωση!'})

    elif intent_id == 'nmap_scan':
        # Show scan type options first (like terminal mode)
        emit('scan_options', {
            'action': 'nmap_scan',
            'target': target,
            'title': f'🔍 Τι είδους σάρωση θέλεις για <span class="cyan">{target or "localhost"}</span>;',
            'options': [
                'Γρήγορη — top 100 ports',
                'Κανονική — top 1000 ports + service detection',
                'Πλήρης — όλα τα ports + OS detection',
                'Vulnerability scan — nmap vuln scripts',
            ]
        })
    elif intent_id == 'web_scan':
        emit('scan_options', {
            'action': 'web_scan',
            'target': target,
            'title': f'🌐 Τι είδους web scan θέλεις για <span class="cyan">{target}</span>;',
            'options': [
                'Nikto — web vulnerability scan',
                'Gobuster — directory brute-force',
                'Και τα δύο',
            ]
        })
    elif intent_id in ('vuln_scan', 'sql_inject', 'password_attack',
                        'wifi_attack', 'packet_capture', 'recon_dns', 'smb_enum'):
        # Request consent first
        intent = result['intent']
        desc = intent[f'description_{lang}'] if intent else intent_id
        emit('consent_required', {
            'action': intent_id,
            'target': target,
            'description': desc,
            'result': result,
        })
    else:
        confirm = build_confirmation(result)
        if confirm:
            emit('system_message', {'message': confirm})
        else:
            emit('system_message', {
                'message': f'Δεν κατάλαβα πλήρως. Δοκίμασε: <em>"σκάναρε το 192.168.1.1"</em> ή <em>"βοήθεια"</em>'
            })

@socketio.on('consent_response')
def handle_consent(data):
    if not data.get('approved'):
        emit('system_message', {'message': '<span class="red">✗ Ακυρώθηκε.</span>'})
        return

    action = data.get('action', '')
    result = data.get('result', {})

    # Re-detect from stored session if needed
    # Execute in background thread
    def run_action():
        output, title = execute_action(action, data)
        if output:
            session_data['last_scan_output'] = output
            session_data['last_scan_type'] = title
            session_data['last_target'] = data.get('target', '')
            socketio.emit('scan_output', {
                'title': title,
                'output': output,
                'scan_type': action,
            })
        else:
            socketio.emit('error_msg', {'message': 'Δεν υπήρξε output.'})

    threading.Thread(target=run_action, daemon=True).start()

@socketio.on('generate_report')
def handle_generate_report(data):
    if session_data.get('last_scan_output'):
        path = generate_report(
            scan_type=session_data.get('last_scan_type', 'Scan'),
            target=session_data.get('last_target', ''),
            output=session_data['last_scan_output'],
        )
        if path and not path.startswith('[✗]'):
            emit('report_ready', {'path': path, 'filename': Path(path).name})
            emit('reports_list', {'reports': get_reports_list()})
        else:
            emit('error_msg', {'message': path})
    else:
        emit('system_message', {'message': 'Κάνε πρώτα μια σάρωση!'})

# ─────────────────────────────────────────────────────────────
#  ACTION EXECUTOR
# ─────────────────────────────────────────────────────────────
def execute_action(action: str, data: dict) -> tuple:
    """Execute the appropriate tool and return (output, title)"""
    target = data.get('target', '')

    def run(cmd, timeout=300):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return (result.stdout + result.stderr).strip()
        except FileNotFoundError:
            return f"[✗] Το εργαλείο '{cmd[0]}' δεν βρέθηκε. Εγκατάστησέ το: sudo apt install {cmd[0]}"
        except subprocess.TimeoutExpired:
            return "[!] Timeout — η εντολή διακόπηκε."
        except Exception as e:
            return f"[✗] Σφάλμα: {e}"

    if action == 'nmap_scan':
        cmd = ['nmap', '-sV', '-sC', '--open', target or 'localhost']
        return run(cmd), f"Nmap Scan — {target or 'localhost'}"

    elif action == 'vuln_scan':
        cmd = ['nmap', '-sV', '--script=vuln', target or 'localhost']
        return run(cmd, timeout=600), f"Vulnerability Scan — {target}"

    elif action == 'web_scan':
        url = target if target.startswith('http') else f'http://{target}'
        if shutil.which('nikto'):
            cmd = ['nikto', '-h', url, '-maxtime', '120']
        else:
            cmd = ['nmap', '-sV', '--script=http-enum,http-title', '-p', '80,443', target]
        return run(cmd, timeout=180), f"Web Scan — {url}"

    elif action == 'sql_inject':
        if not target:
            return "[✗] Χρειάζεται URL με παράμετρο π.χ. http://site.com/page?id=1", "SQLMap"
        url = target if target.startswith('http') else f'http://{target}'
        cmd = ['sqlmap', '-u', url, '--batch', '--level=1', '--dbs', '--timeout=30']
        return run(cmd, timeout=300), f"SQLMap — {url}"

    elif action == 'recon_dns':
        output = ""
        if shutil.which('whois') and target:
            output += "=== WHOIS ===\n" + run(['whois', target], timeout=30) + "\n\n"
        if shutil.which('dig') and target:
            for rtype in ['A', 'MX', 'NS', 'TXT']:
                output += f"=== {rtype} ===\n" + run(['dig', target, rtype, '+short'], timeout=15) + "\n"
        return output or "[✗] Δεν βρέθηκαν εργαλεία DNS", f"DNS Recon — {target}"

    elif action == 'smb_enum':
        if shutil.which('enum4linux') and target:
            return run(['enum4linux', '-a', target], timeout=300), f"SMB Enum — {target}"
        elif shutil.which('nmap') and target:
            return run(['nmap', '-p', '139,445', '--script=smb-enum-shares,smb-vuln-ms17-010', target]), f"SMB Nmap — {target}"
        return "[✗] Δεν βρέθηκε enum4linux ή nmap", "SMB Enum"

    elif action == 'packet_capture':
        if shutil.which('tcpdump'):
            return run(['sudo', 'tcpdump', '-i', 'any', '-c', '50', '-nn'], timeout=30), "Packet Capture"
        return "[✗] tcpdump δεν βρέθηκε", "Packet Capture"

    elif action == 'wifi_attack':
        return (
            "WiFi pentesting χρειάζεται:\n"
            "1. sudo airmon-ng start wlan0\n"
            "2. sudo airodump-ng wlan0mon\n"
            "3. sudo airodump-ng -c <CH> --bssid <BSSID> -w capture wlan0mon\n"
            "4. aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap",
            "WiFi Guide"
        )

    elif action == 'password_attack':
        return (
            "Password Attack Options:\n"
            "• Hash cracking: john hashfile.txt --wordlist=/usr/share/wordlists/rockyou.txt\n"
            "• Brute force SSH: hydra -l user -P rockyou.txt ssh://TARGET\n"
            "• Brute force FTP: hydra -l user -P rockyou.txt ftp://TARGET\n"
            "Δώσε περισσότερες λεπτομέρειες για να εκτελέσω.",
            "Password Attack Guide"
        )

    return f"[?] Άγνωστη ενέργεια: {action}", "Unknown"


def get_help_html(lang='el'):
    if lang == 'el':
        return """
<strong>🐴 Δούρειος Ίππος — Εντολές:</strong><br><br>
<span class="gold">[ Σάρωση Δικτύου ]</span><br>
• "σκάναρε το 192.168.1.1"<br>
• "βρες ανοιχτές πόρτες στο 10.0.0.5"<br><br>
<span class="gold">[ Web Testing ]</span><br>
• "κάνε web scan στο http://site.com"<br>
• "τρέξε sqlmap στο http://site.com?id=1"<br><br>
<span class="gold">[ Password ]</span><br>
• "σπάσε τους κωδικούς"<br>
• "brute force ssh στο 192.168.1.5"<br><br>
<span class="gold">[ Recon ]</span><br>
• "κάνε whois στο google.com"<br>
• "dns lookup για target.com"<br><br>
<span class="gold">[ Reports ]</span><br>
• "δημιούργησε report" — PDF από τελευταία σάρωση
"""
    return """
<strong>🐴 Doureios Ippos — Commands:</strong><br><br>
<span class="gold">[ Network Scanning ]</span><br>
• "scan 192.168.1.1"<br>
• "find open ports on 10.0.0.5"<br><br>
<span class="gold">[ Web Testing ]</span><br>
• "web scan http://site.com"<br>
• "sqlmap http://site.com?id=1"<br><br>
<span class="gold">[ Recon ]</span><br>
• "whois google.com"<br>
• "dns lookup target.com"<br><br>
<span class="gold">[ Reports ]</span><br>
• "generate report" — PDF from last scan
"""


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

@socketio.on('scan_option_selected')
def handle_scan_option(data):
    choice = int(data.get('choice', 1))
    action = data.get('action', 'nmap_scan')
    target = data.get('target', 'localhost') or 'localhost'

    # Map choice to description
    if action == 'nmap_scan':
        descriptions = [
            'Γρήγορη σάρωση (top 100 ports)',
            'Κανονική σάρωση (top 1000 + services)',
            'Πλήρης σάρωση (όλα τα ports + OS)',
            'Vulnerability scan',
        ]
    elif action == 'web_scan':
        descriptions = ['Nikto scan', 'Gobuster directory scan', 'Nikto + Gobuster']
    else:
        descriptions = [f'Ενέργεια {choice}']

    desc = descriptions[choice-1] if choice <= len(descriptions) else descriptions[0]

    emit('consent_required', {
        'action': action,
        'target': target,
        'description': desc,
        'scan_choice': choice,
        'result': {},
    })

def run_gui(host='127.0.0.1', port=5000, debug=False):
    import webbrowser
    import time
    print(f"\n🐴 Δούρειος Ίππος GUI ξεκινά στο http://{host}:{port}")
    print("   Πάτα Ctrl+C για έξοδο\n")
    if host == '127.0.0.1':
        threading.Timer(1.5, lambda: webbrowser.open(f'http://{host}:{port}')).start()
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_gui()
