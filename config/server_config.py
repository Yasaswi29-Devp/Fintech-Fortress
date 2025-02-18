class ServerConfig:
    SERVERS = [
        {
            'id': 0,
            'ip': '127.0.0.1',
            'port': 1069,
            'db': 'database1.db',
            'is_primary': True
        },
        {
            'id': 1,
            'ip': '127.0.0.1',
            'port': 1070,
            'db': 'database2.db',
            'is_primary': False
        }
    ]
    SYNC_INTERVAL = 5  # Seconds between database syncs
    MAX_CONNECTIONS = 10
    RECONNECT_TIMEOUT = 3
    BUFFER_SIZE = 1024
