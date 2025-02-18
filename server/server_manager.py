import os
import sys
import socket
import threading
import sqlite3
import time
from cache_manager import CacheManager

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import configuration and other modules
from config.server_config import ServerConfig
import dbs_view as dbv
import dbs_exec as dbe

class DatabaseSync:
    def __init__(self):
        self.running = True
        self.sync_interval = 2  # 2 seconds interval
        self.primary_db = os.path.join(current_dir, "database1.db")
        self.backup_db = os.path.join(current_dir, "database2.db")
        print(f"Database paths: Primary={self.primary_db}, Backup={self.backup_db}")
        # Initialize Redis cache
        self.cache = CacheManager()

    def sync_databases(self):
        while self.running:
            try:
                # Connect to both databases
                primary_conn = sqlite3.connect(self.primary_db)
                backup_conn = sqlite3.connect(self.backup_db)

                # Tables to sync
                tables = ['CUSTOMERS', 'TRANSACTIONS', 'AUTH']
                
                for table in tables:
                    self._sync_table(primary_conn, backup_conn, table)
                    # After syncing, update cache
                    self._update_cache(table, primary_conn)

                primary_conn.close()
                backup_conn.close()
                print("Database synchronization cycle completed")

            except Exception as e:
                print(f"Synchronization error: {e}")
            
            time.sleep(self.sync_interval)

    def _update_cache(self, table_name: str, conn: sqlite3.Connection):
        """Update Redis cache after sync"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            records = cursor.fetchall()
            
            # Cache the entire table
            cache_key = f"table_{table_name}"
            self.cache.set_cache(cache_key, records)
            print(f"Cache updated for table: {table_name}")
        except Exception as e:
            print(f"Cache update error for {table_name}: {e}")

    def _sync_table(self, primary_conn, backup_conn, table_name):
        try:
            primary_cursor = primary_conn.cursor()
            backup_cursor = backup_conn.cursor()

            # Get records from both databases
            primary_cursor.execute(f"SELECT * FROM {table_name}")
            primary_records = primary_cursor.fetchall()
            
            backup_cursor.execute(f"SELECT * FROM {table_name}")
            backup_records = backup_cursor.fetchall()

            # Convert to sets for comparison
            primary_set = set(primary_records)
            backup_set = set(backup_records)

            # Find differences
            to_add_to_backup = primary_set - backup_set
            to_add_to_primary = backup_set - primary_set

            # Update backup with new records
            for record in to_add_to_backup:
                placeholders = ",".join(["?" for _ in record])
                backup_cursor.execute(
                    f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                    record
                )

            # Update primary with new records
            for record in to_add_to_primary:
                placeholders = ",".join(["?" for _ in record])
                primary_cursor.execute(
                    f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                    record
                )

            # Commit changes
            primary_conn.commit()
            backup_conn.commit()

            if to_add_to_backup or to_add_to_primary:
                print(f"Synced {table_name}: Added {len(to_add_to_backup)} to backup, {len(to_add_to_primary)} to primary")
                # Clear cache for this table as data has changed
                self.cache.delete_cache(f"table_{table_name}")

        except Exception as e:
            print(f"Error syncing table {table_name}: {e}")
            raise

    def start(self):
        """Start the synchronization process in a background thread"""
        # Clear cache on start
        try:
            print("Clearing Redis cache...")
            self.cache.clear_cache()
            print("Redis cache cleared successfully")
        except Exception as e:
            print(f"Error clearing Redis cache: {e}")

        self.sync_thread = threading.Thread(target=self.sync_databases)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        print("Database synchronization started")

    def stop(self):
        """Stop the synchronization process"""
        self.running = False
        if hasattr(self, 'sync_thread'):
            self.sync_thread.join()
        print("Database synchronization stopped")

class ServerManager:
    def __init__(self, server_id):
        self.server_id = server_id
        self.servers = [
            {'id': 0, 'ip': '127.0.0.1', 'port': 1069, 'db': 'database1.db', 'is_primary': True},
            {'id': 1, 'ip': '127.0.0.1', 'port': 1070, 'db': 'database2.db', 'is_primary': False}
        ]
        self.config = next(s for s in self.servers if s['id'] == server_id)
        self.backup_config = next(s for s in self.servers if s['id'] != server_id)
        self.is_running = False
        self.db_sync = None
        # Initialize Redis cache
        self.cache = CacheManager()

    def start(self):
        try:
            print("Initializing Redis cache...")
            self.cache.clear_cache()  # Clear any existing cache
            print("Redis cache initialized")

            # Load menus first
            print("Loading menus...")
            dbv.loadMenus()
            print("Menus loaded successfully")

            # Initialize database
            print("Initializing database...")
            db_path = os.path.join(current_dir, self.config['db'])
            status = dbe.createDatabase(db_path)
            if not status[0]:
                print(f"Failed to initialize database: {status[1]}")
                return False
            print("Database initialized successfully")

            # Create backup database if this is primary server
            if self.config['is_primary']:
                backup_path = os.path.join(current_dir, self.backup_config['db'])
                status = dbe.createDatabase(backup_path)
                if not status[0]:
                    print(f"Failed to initialize backup database: {status[1]}")
                    return False
                print("Backup database initialized successfully")

            # Start database synchronization if primary server
            if self.config['is_primary']:
                print("Starting database synchronization...")
                self.db_sync = DatabaseSync()
                self.db_sync.start()
                print("Database synchronization active")

            # Start server socket
            print(f"Starting server {self.server_id}...")
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config['ip'], self.config['port']))
            self.server_socket.listen(10)
            self.is_running = True
            
            print(f"Server {self.server_id} started on {self.config['ip']}:{self.config['port']}")
            
            while self.is_running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"New connection from {address}")
                    threading.Thread(target=self.handle_client, 
                                  args=(client_socket, address)).start()
                except KeyboardInterrupt:
                    print("\nServer shutting down...")
                    break
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    continue
                
        except Exception as e:
            print(f"Server startup error: {e}")
            return False
        finally:
            if hasattr(self, 'server_socket'):
                self.server_socket.close()
            if self.db_sync:
                self.db_sync.stop()
        
        return True
    
    def handle_client(self, client_socket, address):
        try:
            dbv.handleClient(client_socket, address)
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            if client_socket:
                client_socket.close()
    
    def stop(self):
        self.is_running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        if self.db_sync:
            self.db_sync.stop()

def main():
    if len(sys.argv) != 2:
        print("Usage: python server_manager.py <server_id>")
        sys.exit(1)
        
    try:
        server_id = int(sys.argv[1])
        if server_id not in [0, 1]:
            raise ValueError("Server ID must be 0 or 1")
        
        server = ServerManager(server_id)
        server.start()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
