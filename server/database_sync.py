import sqlite3
import time
import os
import threading
import logging
from datetime import datetime

class DatabaseSync:
    def __init__(self):
        self.running = True
        self.sync_interval = 2  # 2 seconds interval
        self.primary_db = "server/database1.db"
        self.backup_db = "server/database2.db"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename='db_sync.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def sync_databases(self):
        while self.running:
            try:
                # Connect to both databases
                primary_conn = sqlite3.connect(self.primary_db)
                backup_conn = sqlite3.connect(self.backup_db)

                # Sync CUSTOMERS table
                self._sync_table(primary_conn, backup_conn, 'CUSTOMERS')
                # Sync TRANSACTIONS table
                self._sync_table(primary_conn, backup_conn, 'TRANSACTIONS')
                # Sync AUTH table
                self._sync_table(primary_conn, backup_conn, 'AUTH')

                primary_conn.close()
                backup_conn.close()
                logging.info("Database synchronization completed successfully")

            except Exception as e:
                logging.error(f"Synchronization error: {e}")
            
            time.sleep(self.sync_interval)

    def _sync_table(self, primary_conn, backup_conn, table_name):
        try:
            primary_cursor = primary_conn.cursor()
            backup_cursor = backup_conn.cursor()

            # Get schema from primary
            primary_cursor.execute(f"SELECT * FROM {table_name}")
            schema = [description[0] for description in primary_cursor.description]
            columns = ", ".join(schema)

            # Get all records from both databases
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
                logging.info(f"Added record to backup: {record}")

            # Update primary with new records
            for record in to_add_to_primary:
                placeholders = ",".join(["?" for _ in record])
                primary_cursor.execute(
                    f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                    record
                )
                logging.info(f"Added record to primary: {record}")

            # Commit changes
            primary_conn.commit()
            backup_conn.commit()

            if to_add_to_backup or to_add_to_primary:
                logging.info(
                    f"Sync completed for {table_name}. "
                    f"Added {len(to_add_to_backup)} records to backup, "
                    f"{len(to_add_to_primary)} records to primary"
                )

        except Exception as e:
            logging.error(f"Error syncing table {table_name}: {e}")
            raise

    def start(self):
        """Start the synchronization process in a background thread"""
        self.sync_thread = threading.Thread(target=self.sync_databases)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        logging.info("Database synchronization started")

    def stop(self):
        """Stop the synchronization process"""
        self.running = False
        if hasattr(self, 'sync_thread'):
            self.sync_thread.join()
        logging.info("Database synchronization stopped")

# Global sync instance
db_sync = None
