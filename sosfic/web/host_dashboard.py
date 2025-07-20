"""
SOSFIC Host Dashboard - Dashboard pour l'host du réseau
"""
from flask import Flask, render_template, url_for
import socket
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Détection de l'URL publique (pour Codespaces, à adapter si besoin)
    codespace_name = os.environ.get('CODESPACE_NAME', '')
    if codespace_name:
        join_url = f"https://{codespace_name}.github.dev"
    else:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        join_url = f"http://{local_ip}:5000"
    return render_template('host_dashboard.html', join_url=join_url) 