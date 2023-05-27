from setuptools import setup

setup(
    name='usb_aqwantonio',
    version='1.0',
    url='https://github.com/aqwAntonio/copy-files',
    license="GNU GENERAL PUBLIC LICENSE",
    author='anton',
    author_email='123987465951@mail.ru',
    description='GUI for copying files to USB',
    entry_points={
        'console_scripts': [
            'usb_aqwantonio=usb_aqwantonio.widget:main'
        ]
    },
    packages=['usb_aqwantonio'],
    package_data={'usb_aqwantonio': ['config.ini', 'error.log', 'form.ui']},
    include_package_data=True,
    install_requires=[
        'psutil',
        'datetime',
        'PyQt6',
        'PySide6',
        'configparser'
    ],
    data_files=[
        ('share/applications', ['data/usb_aqwantonio.desktop']),
        ('share/icons', ['data/usb_aqwantonio.png']),
    ],
)
