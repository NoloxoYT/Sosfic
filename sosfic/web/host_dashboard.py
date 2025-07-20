"""
SOSFIC Host Dashboard - Dashboard pour l'host du réseau
"""
from flask import Flask, render_template, url_for, request, redirect, flash
import socket
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'sosfic-secret-key'
UPLOAD_FOLDER = Path("fragments")
UPLOAD_FOLDER.mkdir(exist_ok=True)
CHUNK_SIZE = 10 * 1024 * 1024  # 10 Mo

@app.route('/', methods=['GET', 'POST'])
def index():
    # Détection de l'URL publique (pour Codespaces, à adapter si besoin)
    codespace_name = os.environ.get('CODESPACE_NAME', '')
    if codespace_name:
        join_url = f"https://{codespace_name}.github.dev"
    else:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        join_url = f"http://{local_ip}:5000"

    peer_id = codespace_name or hostname

    # Gestion de l'upload et fragmentation à la volée
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(url_for('index'))
        # Fragmentation à la volée
        fragment_streaming(file, file.filename)
        flash('Fichier importé et fragmenté avec succès.', 'success')
        return redirect(url_for('index'))

    # Infos dynamiques
    fragments = sorted([f.name for f in UPLOAD_FOLDER.glob('*.bin')])
    storage_gb = sum(f.stat().st_size for f in UPLOAD_FOLDER.glob('*.bin')) / (1024**3)
    num_peers = 1  # Pour l'instant, juste l'host
    return render_template(
        'host_dashboard.html',
        join_url=join_url,
        peer_id=peer_id,
        storage_gb=round(storage_gb, 3),
        num_peers=num_peers,
        fragments=fragments
    )

@app.route('/delete_fragments', methods=['POST'])
def delete_fragments():
    for frag in Path(UPLOAD_FOLDER).glob('*.bin'):
        frag.unlink()
    flash('Tous les fragments ont été supprimés.', 'success')
    return ('', 204)

def fragment_streaming(file_storage, original_filename):
    """Fragmenter le fichier uploadé à la volée, sans jamais le stocker en entier."""
    i = 0
    while True:
        chunk = file_storage.stream.read(CHUNK_SIZE)
        if not chunk:
            break
        frag_name = f"{Path(original_filename).stem}_chunk_{i:04d}.bin"
        frag_path = UPLOAD_FOLDER / frag_name
        with open(frag_path, 'wb') as frag:
            frag.write(chunk)
        i += 1 