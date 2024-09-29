#!/usr/bin/env python

from enum import Enum
from setuptools import setup
from setuptools.command.install import install
import os
import json

# ░░░░░░░░░░░░░░░░░░░░░▓▓▓░░░░░░░░░░░░░░░░░░░░░░
# ░░                                          ░░
# ░░                                          ░░
# ░░    SIMBASHLOG NOTIFIER CONFIGURATION     ░░
# ░░                                          ░░
# ░░                                          ░░
# ░░░░░░░░░░░░░░░░░░░░░▓▓▓░░░░░░░░░░░░░░░░░░░░░░

class NotifierConfig(Enum):
    NAME = 'simbashlog-example-notifier'                # TODO: Replace with the name of your notifier but keep the prefix 'simbashlog-' and the suffix '-notifier'
    VERSION = '1.0.0'                                   # TODO: Replace with the version of your notifier
    DESCRIPTION = 'simbashlog-notifier for example'     # TODO: Replace with the description of your notifier
    AUTHOR = 'Fabian Fuchs'                             # TODO: Replace with your name
    PYTHON_VERSION = '>=3.10'                           # TODO: Replace with the required Python version of your notifier
    REPOSITORY_PYTHON_SUBDIRECTORY_NAME = 'example'     # TODO: Replace with the name of the subdirectory in the repository where the Python code of your notifier is located
    KEYWORDS = [                                        # TODO: Replace with the keywords of your notifier, at least add the notify type
        'example',
    ]
    INSTALL_REQUIRES = [                                # TODO: Add the required packages for your notifier that are not per default installed
    ]
    NOTIFY_HELPER_VERSION = '1.6.1'                     # TODO: Replace with the version of the simbashlog-notify-helper package that your notifier requires
    CONFIG_FILE_KEY_REPLACEMENTS = {                    # TODO: Add key replacements for the configuration file if you have changed the keys in a new version. It is kind of a migration for the configuration file
        #'old_config_file_key': 'new_config_file_key',
    }

    @classmethod
    def get_data_for_config_file(cls):
        # TODO: Define the default configuration values for your notifier. Replace the keys and values with the ones that are required for your notifier. This will be used to create later the json configuration file.
        return {
            # General
            'min_required_log_level': '6',                  # 0-7
            'show_in_console_sent_message': 'true',         # or 'false'
            # Header
            'show_in_header_pid': 'false',                  # or 'true'
            # Body
            'show_in_body_log_file_result': 'false',        # or 'true'
            'show_in_body_log_file_content': 'false',       # or 'true'
            'show_in_body_summary_for_pid': 'false',        # or 'true'
            'show_in_body_summary_for_log_file': 'false',   # or 'true'
            # Footer
            'show_in_footer_log_file_names': 'false',       # or 'true'
            'show_in_footer_host': 'false',                 # or 'true'
            'show_in_footer_notifier_name': 'true',         # or 'false'

            # Notifier specific
            'example_key': 'example_value',
        }

# ░░░░░░░░░░░░░░░░░░░░░▓▓▓░░░░░░░░░░░░░░░░░░░░░░
# ░░                                          ░░
# ░░                                          ░░
# ░░      DO NOT MODIFY ANYTHING BELOW!       ░░
# ░░                                          ░░
# ░░                                          ░░
# ░░░░░░░░░░░░░░░░░░░░░▓▓▓░░░░░░░░░░░░░░░░░░░░░░

class PostInstallCommand(install):
    CONFIG_PATH = os.path.expanduser(f'~/.config/simbashlog-notifier/{NotifierConfig.NAME.value}/config.json')

    def run(self):
        install.run(self)

        if os.path.exists(self.CONFIG_PATH):
            print(f"Configuration file already exists at '{self.CONFIG_PATH}'")
            self.update_config_file()
        else:
            self.create_config_file()

    def create_config_file(self):
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)

        new_config_data = NotifierConfig.get_data_for_config_file()

        with open(self.CONFIG_PATH, 'w') as config_file:
            json.dump(new_config_data, config_file, indent=4)

        print(f"Configuration file created at '{self.CONFIG_PATH}'")

    def update_config_file(self):
        with open(self.CONFIG_PATH, 'r') as config_file:
            current_config = json.load(config_file)

        config_data = NotifierConfig.get_data_for_config_file()

        for old_key, new_key in NotifierConfig.CONFIG_FILE_KEY_REPLACEMENTS.value.items():
            if old_key in current_config and new_key not in current_config:
                current_config[new_key] = current_config.pop(old_key)

        updated_config_data = {key: current_config.get(key, config_data[key]) for key in config_data.keys()}

        with open(self.CONFIG_PATH, 'w') as config_file:
            json.dump(updated_config_data, config_file, indent=4)

        print(f"Configuration file updated at '{self.CONFIG_PATH}'")

setup(
    name=NotifierConfig.NAME.value,
    version=NotifierConfig.VERSION.value,
    description=NotifierConfig.DESCRIPTION.value,
    author=NotifierConfig.AUTHOR.value,
    license='GPL-3.0-or-later',
    url=f'https://github.com/fuchs-fabian/simbashlog-notifiers/tree/main/src/python/{NotifierConfig.REPOSITORY_PYTHON_SUBDIRECTORY_NAME.value}',
    keywords=[
        'simbashlog',
        'notify',
        'notifier',
        *NotifierConfig.KEYWORDS.value
    ],
    platforms=['Linux'],
    python_requires=NotifierConfig.PYTHON_VERSION.value,
    install_requires=[
        f'simbashlog-notify-helper @ git+https://github.com/fuchs-fabian/simbashlog-notify-helper-py.git@v{NotifierConfig.NOTIFY_HELPER_VERSION.value}',
        *NotifierConfig.INSTALL_REQUIRES.value
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': [
            f'{NotifierConfig.NAME.value}={NotifierConfig.NAME.value.replace('-', '_')}:main',
        ],
    },
)