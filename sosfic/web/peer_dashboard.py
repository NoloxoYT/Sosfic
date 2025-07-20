"""
SOSFIC Peer Dashboard - Dashboard pour un peer du réseau
"""
from flask import Flask, render_template, request, redirect
import os
import socket
import requests

app = Flask(__name__)

def get_peer_id():
    return os.environ.get('CODESPACE_NAME') or socket.gethostname()

def register_to_host(host_url, peer_id):
    try:
        r = requests.post(f"{host_url}/api/register_peer", json={'peer_id': peer_id}, timeout=5)
        return r.json()
    except Exception as e:
        return {'error': str(e)}

def get_index_from_host(host_url):
    try:
        r = requests.get(f"{host_url}/api/index", timeout=5)
        return r.json().get('fragments', [])
    except Exception as e:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    peer_id = get_peer_id()
    host_url = os.environ.get('SOSFIC_HOST_URL', '')

    # Permettre de changer d'host via le formulaire
    if request.method == 'POST':
        host_url = request.form.get('host_url', '').strip()
        os.environ['SOSFIC_HOST_URL'] = host_url

    fragments = []
    host_status = None
    if host_url:
        host_status = register_to_host(host_url, peer_id)
        fragments = get_index_from_host(host_url)

    return render_template(
        'peer_dashboard.html',
        host_url=host_url,
        peer_id=peer_id,
        host_status=host_status,
        fragments=fragments
    )

if __name__ == '__main__':
    app.run(debug=True) 