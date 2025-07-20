"""
SOSFIC Host Dashboard - Dashboard pour l'host du réseau
"""
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
import socket
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'sosfic-secret-key'
UPLOAD_FOLDER = Path("fragments")
UPLOAD_FOLDER.mkdir(exist_ok=True)
CHUNK_SIZE = 10 * 1024 * 1024  # 10 Mo

# Liste des peers connectés (en mémoire)
connected_peers = {}

@app.route('/', methods=['GET', 'POST'])
def index():
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
        fragment_streaming(file, file.filename)
        flash('Fichier importé et fragmenté avec succès.', 'success')
        return redirect(url_for('index'))

    fragments = sorted([f.name for f in UPLOAD_FOLDER.glob('*.bin')])
    storage_gb = sum(f.stat().st_size for f in UPLOAD_FOLDER.glob('*.bin')) / (1024**3)
    num_peers = len(connected_peers)
    return render_template(
        'host_dashboard.html',
        join_url=join_url,
        peer_id=peer_id,
        storage_gb=round(storage_gb, 3),
        num_peers=num_peers,
        fragments=fragments,
        peer_ids=list(connected_peers.keys())
    )

@app.route('/api/register_peer', methods=['POST'])
def register_peer():
    data = request.get_json()
    peer_id = data.get('peer_id')
    if not peer_id:
        return jsonify({'error': 'peer_id required'}), 400
    connected_peers[peer_id] = {'id': peer_id, 'ip': request.remote_addr}
    return jsonify({'status': 'ok', 'peer_id': peer_id})

@app.route('/api/peers', methods=['GET'])
def get_peers():
    return jsonify(list(connected_peers.values()))

@app.route('/api/index', methods=['GET'])
def get_index():
    fragments = sorted([f.name for f in UPLOAD_FOLDER.glob('*.bin')])
    return jsonify({'fragments': fragments})

@app.route('/delete_fragments', methods=['POST'])
def delete_fragments():
    for frag in Path(UPLOAD_FOLDER).glob('*.bin'):
        frag.unlink()
    flash('Tous les fragments ont été supprimés.', 'success')
    return ('', 204)

def fragment_streaming(file_storage, original_filename):
    i = 0
    fragment_paths = []
    while True:
        chunk = file_storage.stream.read(CHUNK_SIZE)
        if not chunk:
            break
        frag_name = f"{Path(original_filename).stem}_chunk_{i:04d}.bin"
        frag_path = UPLOAD_FOLDER / frag_name
        with open(frag_path, 'wb') as frag:
            frag.write(chunk)
        fragment_paths.append(str(frag_path))
        i += 1
    if fragment_paths:
        generate_torrent(UPLOAD_FOLDER, f"{Path(original_filename).stem}.torrent")

# Génération du .torrent
import libtorrent as lt

def generate_torrent(fragments_dir, output_torrent):
    fs = lt.file_storage()
    for fname in sorted(os.listdir(fragments_dir)):
        if fname.endswith('.bin'):
            lt.add_files(fs, os.path.join(fragments_dir, fname))
    t = lt.create_torrent(fs, piece_size=1024*1024)  # 1 Mo par pièce
    lt.set_piece_hashes(t, str(fragments_dir))
    torrent = t.generate()
    with open(os.path.join(fragments_dir, output_torrent), 'wb') as f:
        f.write(lt.bencode(torrent))
    print(f".torrent généré : {output_torrent}") 