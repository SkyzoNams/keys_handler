from datetime import datetime
from keys_handler.src.Secrets import Encrypt
from keys_handler.src.DatabaseDriver import DatabaseDriver
import logging
import os

class DataBaseUtils(object):
    def __init__(self):
        self.encryptor = Encrypt()
        self.db = DatabaseDriver()

    """
     @Notice: This function with select all the item stored in the database
     @Dev:    We first connect to the database, then we execute the SELECT query.
              Finally we use the fetchall method to get the items, we disconnect to the database and return the items
    """
    def select_all(self, table_name):
        query = "SELECT * FROM " + table_name
        items = self.db.execute(execution_string=query, fetch_all=True)
        return items

    """
     @Notice: This function will update the event_type column from the table
     @Dev:    We first build the update query using the pub_key as key and update the event_type value
              regarding the status passed in parameter
    """
    def update_event_type(self, pubkey, status):
        query = "UPDATE data_store SET event_type = '" + self.encryptor.encrypt_message(status) + "' WHERE public_key = '" + pubkey + "'"
        self.db.execute(execution_string=query, commit=True)

    """
     @Notice: This function will select from the database an item with the given parameters
     @Dev:    We first build our query using the row hash generate by the hash_list() function and then execute it with the tupple arguments
    """
    def select_by_row_hash(self, table_name: str, args_list: list):
        try:
            row_hash = self.encryptor.hash_list(args_list)
            query = """SELECT * FROM """ + table_name + \
                """ WHERE row_hash = '{row_hash}'""".format(row_hash=row_hash)
            return self.db.execute(execution_string=query, fetch_all=True)
        except Exception as e:
            raise e

    def update_column(self, table_name, column_name, id_name, id_value, col_value, encrypt=True):
        update_val = self.encryptor.encrypt_message(col_value)
        if encrypt is False:
            update_val = col_value
        query = "UPDATE " + table_name + " SET " + column_name + " = '" + str(update_val) + "' WHERE " + id_name + " = '" + str(id_value) + "'"
        self.db.execute(execution_string=query, commit=True)
        logging.info('column ' + column_name + ' updated with value ' + str(col_value) + ' for record ' + str(id_name) + " " + str(id_value) + ' on table ' + table_name)
    
    def insert_error(self, error, contract_address, name, raised_error):
        env = "test"
        if os.path.exists("/mnt/backend") is True:
            env = "prod"
        item = self.select_by_row_hash("scripts_errors", [raised_error, contract_address, name, env])
        if len(item) == 0 or item[0][3] is True:
            insert_query = """INSERT INTO scripts_errors (error, contract_address, created, row_hash, name, env) VALUES (%s, %s, %s, %s, %s, %s)"""
            item_tuple = (self.encryptor.encrypt_message(error),
                        contract_address,
                        self.encryptor.encrypt_message(
                            str(datetime.now())),
                        self.encryptor.hash_list([raised_error, contract_address, name, env]),
                        self.encryptor.encrypt_message(name),
                        self.encryptor.encrypt_message(env)
                        )
            self.db.execute(execution_string=insert_query, item_tuple=item_tuple, commit=True)
            logging.info('error inserted to database')            
