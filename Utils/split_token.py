#!/usr/bin/env python3
import os
from PyQt5.QtCore import QThread
from Utils.config import Config
from settings import DELIMITER, TOKEN_SIZE


class Split_Token(QThread):
    def __init__(self, input_path, command, signal, token_size=TOKEN_SIZE, delimiter=DELIMITER, parent=None):
        super(Split_Token, self).__init__(parent=parent)
        self.ip = input_path
        self.tk_size = token_size
        self.delimiter = delimiter
        self.command = command
        self.qs = signal

    def run(self) -> None:
        try:
            _config = Config(
                company_path=self.ip, command=self.command, token_size=self.tk_size
            )
            for item in os.listdir(self.ip):
                item_path = os.path.join(self.ip, item)
                if item.startswith('.') or not os.path.isdir(item_path):
                    continue
                _config._append(item_path)
            for content in _config.file_path_list:
                command = content['command']
                file_list_argument = f'{DELIMITER}'.join(content['file_list'])
                image_dst_distributed = content['distination']
                passed_command = f'{command} --file-list "{file_list_argument}" --image-dst-distributed "{image_dst_distributed}"'
                self.qs.emit(passed_command)
        except Exception as e:
            print(e)
        finally:
            print('finished')
