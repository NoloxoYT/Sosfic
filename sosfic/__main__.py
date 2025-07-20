import sys
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="SOSFIC - Self-hosted Online Storage Fragmented In Codespaces")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--host', action='store_true', help='Lancer le dashboard en mode HOST')
    group.add_argument('--peer', action='store_true', help='Lancer le dashboard en mode PEER')
    parser.add_argument('--host-url', type=str, help='URL du host à rejoindre (mode peer)')
    parser.add_argument('--port', type=int, default=5000, help='Port du dashboard (défaut: 5000)')
    args = parser.parse_args()

    if args.host:
        from sosfic.web.host_dashboard import app
        app.run(host='0.0.0.0', port=args.port, debug=True)
    elif args.peer:
        os.environ['SOSFIC_HOST_URL'] = args.host_url or ''
        from sosfic.web.peer_dashboard import app
        app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main() 