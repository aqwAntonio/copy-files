# This Python file uses the following encoding: utf-8
import os
import sys
import psutil
import shutil
import logging

from datetime import datetime
from configparser import ConfigParser
from PySide2.QtWidgets import QApplication
from PyQt5.uic import loadUiType


app_folder = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(
    filename=os.path.join(app_folder, 'error.log'),
    encoding='utf-8',
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)


class FirstStep:
    def __init__(self, devices, window):
        self.window = window
        self.devices = devices

    def run(self):
        if len(self.devices) > 1:
            self.window.stackedWidget.setCurrentIndex(0)
            self.shown_device_list()
        elif len(self.devices) == 1:
            self.window.stackedWidget.setCurrentIndex(1)
            self.hidden_device_list()
        else:
            self.empty_device_list()

    def shown_device_list(self):
        config_object = Config()
        config_object.update_value('current_device', '')
        source_folder = config_object.get_value('source_folder')

        self.window.stackedWidget.setCurrentIndex(0)
        self.window.listWidget.clear()
        for i in range(len(self.devices)):
            self.window.listWidget.addItem(self.devices[i].mountpoint)
        self.window.listWidget.show()

        self.window.plainTextEdit.clear()
        self.window.plainTextEdit.appendPlainText(source_folder)

    def hidden_device_list(self):
        config_object = Config()
        config_object.update_value('current_device', self.devices[0].mountpoint)
        source_folder = config_object.get_value('source_folder')

        self.window.plainTextEdit_2.clear()
        self.window.plainTextEdit_2.appendPlainText(source_folder)
        self.window.stackedWidget.setCurrentIndex(1)

    def empty_device_list(self):
        self.window.stackedWidget.setCurrentIndex(2)
        config_object = Config()
        config_object.update_value('current_device', '')


class SecondStep:
    def __init__(self, window, source_folder, destination_folder):
        self.window = window
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.file_list = os.listdir(self.source_folder)

    def run(self):
        self.window.stackedWidget.setCurrentIndex(3)
        self.window.progressBar.setValue(0)
        os.makedirs(self.destination_folder, exist_ok=True)

        for n, item in enumerate(self.file_list):
            percent = (n + 1) / len(self.file_list) * 100
            source_path = os.path.join(self.source_folder, item)
            destination_path = os.path.join(self.destination_folder, item)
            self.window.progressBar.setValue(int(percent))
            if os.path.isfile(source_path):
                result = self.copy_file(source_path, destination_path)
                if not result:
                    return False
        return True

    def copy_file(self, source_path, destination_path):
        try:
            shutil.move(source_path, destination_path)
            return True
        except shutil.Error as e:
            logging.error(e)
            return False
        except OSError as e:
            logging.error(e)
            return False


class ThirdStep:
    def __init__(self, window, folder, count):
        self.window = window
        self.folder = folder
        self.count = count

    def run(self):
        self.window.stackedWidget.setCurrentIndex(4)
        self.window.label_3.setText(
            '<p align="center">Скопировано ' + str(self.count) +
            ' файлов в папку <strong>' + self.folder + '</strong></p><p align="center">Можно вынуть флешку</p>')


class Config:
    def __init__(self):
        self.config_file = os.path.join(app_folder, 'config.ini')

    def update_value(self, key, value):
        config_object = ConfigParser()
        config_object.read(self.config_file)
        # Get the USERINFO section
        userinfo = config_object["USERINFO"]

        # Update the property
        userinfo[key] = value
        with open(self.config_file, 'w') as conf:
            config_object.write(conf)

    def get_value(self, key):
        config_object = ConfigParser()
        config_object.read(self.config_file)
        # Get the USERINFO section
        return config_object["USERINFO"][key]


class MainApplication:

    def __init__(self, args):
        self.devices = []
        self.destination_folder = None

        self.app = QApplication(args)
        # setting application display name

        self.app.setApplicationName('UsbAqwantonio')

        if sys.platform.startswith('linux'):
            self.app.setDesktopFileName("usb_aqwantonio.desktop")

        self.window = loadUiType(os.path.join(app_folder, 'form.ui'))
        self.window.pushButton.clicked.connect(self.second_stage)
        self.window.pushButton_2.clicked.connect(self.second_stage)
        self.window.pushButton_3.clicked.connect(self.first_stage)
        self.window.plainTextEdit.textChanged.connect(self.update_folder)
        self.window.plainTextEdit_2.textChanged.connect(self.update_folder2)
        self.window.listWidget.itemClicked.connect(self.update_current_device)

    def start(self):
        self.first_stage()
        self.window.show()
        self.app.exec()

    def first_stage(self):
        self.init_devices()
        first_step = FirstStep(self.devices, self.window)
        first_step.run()

    def second_stage(self):
        config_object = Config()
        current_device = config_object.get_value('current_device')
        source_folder = config_object.get_value('source_folder')
        print_folder = datetime.strftime(datetime.now(), "На печать %d-%m-%Y")
        self.destination_folder = os.path.join(current_device, print_folder)
        if self.check_device(current_device) and self.check_folder(source_folder):
            second_step = SecondStep(self.window, source_folder, self.destination_folder)
            result = second_step.run()
            if result:
                self.third_stage(print_folder, len(second_step.file_list))
        else:
            self.first_stage()

    def third_stage(self, folder, count):
        third_step = ThirdStep(self.window, folder, count)
        third_step.run()

    def init_devices(self):
        """Go through the usb-bus and find devices(and most likely controllers) by vendor-id"""
        partitions = psutil.disk_partitions()
        self.devices = []
        for p in partitions:
            if 'media' in p.mountpoint:
                self.devices.append(p)
                # print(p.mountpoint, psutil.disk_usage(p.mountpoint).percent)

    def update_folder(self):
        config_object = Config()
        config_object.update_value('source_folder', self.window.plainTextEdit.toPlainText())

    def update_folder2(self):
        config_object = Config()
        config_object.update_value('source_folder', self.window.plainTextEdit_2.toPlainText())

    def update_current_device(self, current_row):
        config_object = Config()
        config_object.update_value('current_device', current_row.text())

    def check_device(self, current_device):
        for i in range(len(self.devices)):
            if current_device == self.devices[i].mountpoint:
                return True
        return False

    def check_folder(self, value):
        return os.path.isdir(value)


def main():
    application = MainApplication(sys.argv)
    application.start()


if __name__ == "__main__":
    main()
