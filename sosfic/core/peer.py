"""
SOSFIC Peer - Gestion des peers P2P.
"""

# TODO: Implémenter la logique de peer (connexion, découverte, échange de fragments)

class Peer:
    def __init__(self, peer_id, port=6881):
        self.peer_id = peer_id
        self.port = port

    def connect(self, peer_url):
        """Connecte ce peer à un autre peer via son URL."""
        pass 