"""
SOSFIC Peer Dashboard - Dashboard pour un peer du réseau
"""
from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    host_url = os.environ.get('SOSFIC_HOST_URL', '')
    return render_template('peer_dashboard.html', host_url=host_url) 