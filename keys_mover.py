from keys_handler.src.DataBaseUtils import DataBaseUtils
import traceback
import shutil
import pexpect
from keys_handler.src.Config import Config
import logging
logging.basicConfig(format="%(asctime)s: %(levelname)s - %(message)s", level=logging.INFO)
logging.addLevelName(41, "FILE CREATED")
logging.addLevelName(42, "FILE MOVED")

class KeysMover():
    def __init__(self):
        self.in_folder = Config().return_config_keys_mover(keys_mover_enter_folder=True)
        self.out_folder = Config().return_config_keys_mover(keys_mover_exit_folder=True)
        self.beacon_api_endpoint = Config().return_config_keys_mover(keys_mover_beacon_api=True)
    
    def move_in(self, validator_keys, password, validator_filename):
        try:
            write_file(self.in_folder + validator_filename + ".json", validator_keys)
            write_file(self.in_folder + validator_filename + ".txt", password)
        except Exception as e:
            DataBaseUtils().insert_error(str(traceback.format_exc()), str(None), "keys_mover", e)
            raise e

    def move_out(self, validator_filename):
        try:
            move_file(self.in_folder + validator_filename + ".json", self.out_folder + validator_filename + ".json")
            move_file(self.in_folder + validator_filename + ".txt", self.out_folder + validator_filename + ".txt")
            child = pexpect.spawn('teku voluntary-exit --beacon-node-api-endpoint=' + self.beacon_api_endpoint + ' --validator-keys=' + self.out_folder + validator_filename + '.json:' + self.out_folder + validator_filename + '.txt')
            #child.expect('Please choose your language')
        except Exception as e:
            DataBaseUtils().insert_error(str(traceback.format_exc()), str(None), "keys_mover", e)
            raise e

def move_file(_from, _to):
    shutil.move(_from, _to)
    logging.log(42, 'FROM: ' + _from + ' -> TO: ' + _to)
    
"""
    @Notice: This function will write to a file
    @Dev:   We open and write the content to the file path
"""
def write_file(file_path: str, content: str):
    with open(file_path, 'w') as file:
        file.write(content)
    logging.log(41, file_path)