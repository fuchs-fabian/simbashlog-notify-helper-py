#!/usr/bin/env python3

import argparse
import os
import re
import json
import sys
import pandas as pd # type: ignore
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple, Type

class Severity(Enum):
    '''
    Enum to represent the severity levels of log messages based on [RFC 5424](https://tools.ietf.org/html/rfc5424) [Page 11]:

    | Numerical Code | Severity      | Description                      |
    |----------------|---------------|----------------------------------|
    | 0              | Emergency     | System is unusable               |
    | 1              | Alert         | Action must be taken immediately |
    | 2              | Critical      | Critical conditions              |
    | 3              | Error         | Error conditions                 |
    | 4              | Warning       | Warning conditions               |
    | 5              | Notice        | Normal but significant condition |
    | 6              | Informational | Informational messages           |
    | 7              | Debug         | Debug-level messages             |

    Attributes:
        EMERG (tuple):
            The tuple representing the severity level for emergencies.
        ALERT (tuple):
            The tuple representing the severity level for alerts.
        CRIT (tuple):
            The tuple representing the severity level for critical issues.
        ERROR (tuple):
            The tuple representing the severity level for errors.
        WARN (tuple):
            The tuple representing the severity level for warnings.
        NOTICE (tuple):
            The tuple representing the severity level for notices.
        INFO (tuple):
            The tuple representing the severity level for informational messages.
        DEBUG (tuple):
            The tuple representing the severity level for debug messages.

    Example:
        >>> Severity.ERROR
        ERROR
        >>> Severity.ERROR.name
        ERROR
        >>> Severity.ERROR.value
        (3, 'Error', 'Error conditions', '❗', '\u2757')
        >>> Severity.ERROR.rfc_5424_numerical_code
        3
        >>> Severity.ERROR.rfc_5424_severity
        Error
        >>> Severity.ERROR.rfc_5424_description
        Error conditions
        >>> Severity.ERROR.emoji
        ❗
        >>> Severity.ERROR.unicode # In case the emoji does not render properly
        \u2757
    '''

    EMERG = (
        0,
        "Emergency",
        "System is unusable",
        "🚑",
        "\U0001F691"
        )
    ALERT = (
        1,
        "Alert",
        "Action must be taken immediately",
        "🚨",
        "\U0001F6A8"
        )
    CRIT = (
        2,
        "Critical",
        "Critical conditions",
        "🔥",
        "\U0001F525"
        )
    ERROR = (
        3,
        "Error",
        "Error conditions",
        "❗",
        "\u2757"
        )
    WARN = (
        4,
        "Warning",
        "Warning conditions",
        "⚠️",
        "\u26A0\uFE0F"
        )
    NOTICE = (
        5,
        "Notice",
        "Normal but significant condition",
        "📝",
        "\U0001F4DD"
        )
    INFO = (
        6,
        "Informational",
        "Informational messages",
        "ℹ️",
        "\u2139\uFE0F"
        )
    DEBUG = (
        7,
        "Debug",
        "Debug-level messages",
        "🔍",
        "\U0001F50D"
        )

    def __init__(
            self,
            rfc_5424_numerical_code:int,
            rfc_5424_severity: str,
            rfc_5424_description: str,
            emoji: str,
            unicode: str
            ):
        self._rfc_5424_numerical_code = rfc_5424_numerical_code
        self._rfc_5424_severity = rfc_5424_severity
        self._rfc_5424_description = rfc_5424_description
        self._emoji = emoji
        self._unicode = unicode

    @property
    def rfc_5424_numerical_code(self):
        return self._rfc_5424_numerical_code

    @property
    def rfc_5424_severity(self):
        return self._rfc_5424_severity

    @property
    def rfc_5424_description(self):
        return self._rfc_5424_description

    @property
    def emoji(self):
        return self._emoji

    @property
    def unicode(self):
        return self._unicode
    
    @classmethod
    def get_by_code(cls, code: int) -> 'Severity':
        '''
        Returns the severity level based on the numerical code.

        Args:
            code (int): The numerical code of the severity level.

        Returns:
            Severity: The severity level.

        Raises:
            ValueError: If no matching severity level is found for the given code.
        '''
        for severity in cls:
            if severity.rfc_5424_numerical_code == code:
                return severity
        raise ValueError(f"No matching severity found for code '{code}'")

    @classmethod
    def get_by_name(cls, name: str) -> 'Severity':
        '''
        Returns the severity level based on the name.

        Args:
            name (str): The name of the severity level.

        Returns:
            Severity: The severity level.

        Raises:
            ValueError: If no matching severity level is found for the given name.
        '''
        for severity in cls:
            if severity.name == name:
                return severity
        raise ValueError(f"No matching severity found for name '{name}'")

    def __str__(self):
        return self.name

class LogField(Enum):
    '''
    Enum to represent the fields for a log entry.

    Attributes:
        TIMESTAMP (str):
            Represents the timestamp.
        SCRIPT_INFO (str):
            Represents the script information. This field provides context about the source of the log.
        PID (str):
            Represents the process ID. This field identifies the process that generated the log.
        LEVEL (str):
            Represents the severity level. This field indicates the importance or urgency of the log message.
        MESSAGE (str):
            Represents the actual log message content.
    '''

    TIMESTAMP = "timestamp"
    SCRIPT_INFO = "script_info"
    PID = "pid"
    LEVEL = "level"
    MESSAGE = "message"

    def __str__(self):
        return self.value

'''
Enum to represent all possible fields in a DataFrame:

| Field (...`.name`) | Value (...`.value`) |
|--------------------|---------------------|
| EMERG              | EMERG               |
| ALERT              | ALERT               |
| CRIT               | CRIT                |
| ERROR              | ERROR               |
| WARN               | WARN                |
| NOTICE             | NOTICE              |
| INFO               | INFO                |
| DEBUG              | DEBUG               |
| TIMESTAMP          | timestamp           |
| SCRIPT_INFO        | script_info         |
| PID                | pid                 |
| LEVEL              | level               |
| MESSAGE            | message             |
| SEVERITY_CODE      | severity_code       |
| COUNT              | count               |
'''
DataFrameField = Enum(
    'DataFrameField', {
        **{severity.name: severity.name for severity in Severity},
        **{log_field.name: log_field.value for log_field in LogField},
        'SEVERITY_CODE': 'severity_code',
        'COUNT': 'count'
    }
)

DataFrameField.__str__ = lambda self: self.value

class StoredLogInfo:
    '''
    A class to store and manage information related to `simbashlog` log processing.

    Attributes:
        pid (Optional[int]):
            The process ID.
        log_level (Optional[int]):
            The log level / severity number.
        message (Optional[str]):
            The log message.
        log_file (Optional[str]):
            The path to the log file.
        json_log_file (Optional[str]):
            The path to the JSON log file.
        data_df (Optional[pd.DataFrame]):
            The DataFrame containing the loaded data from log or JSON log file.
        summary_df (Optional[pd.DataFrame]):
            The DataFrame containing the summary information from log or JSON log file.
    '''

    def __init__(self):
        self.pid: Optional[int] = None
        self.log_level: Optional[int] = None
        self.message: Optional[str] = None
        self.log_file: Optional[str] = None
        self.json_log_file: Optional[str] = None
        self.data_df: Optional[pd.DataFrame] = None
        self.summary_df: Optional[pd.DataFrame] = None

    def _update(self, args: argparse.Namespace) -> None:
        self.pid = args.pid
        self.log_level = args.log_level
        self.message = args.message
        self.log_file = args.log_file
        self.json_log_file = args.json_log_file

        def _try_load_log_file() -> None:
            def _load_log_file_as_dataframe(log_file: str) -> pd.DataFrame:
                def _parse_log_line(line: str) -> Optional[dict]:
                    log_pattern = re.compile(r'(?P<timestamp>[\d-]+\s[\d:]+)\s-\s(?P<script>\[.*?\])\s-\s\[PID:\s(?P<pid>\d+)\]\s-\s\[(?P<level>\w+)\]\s-\s(?P<message>.+)')
                    match = log_pattern.match(line)
                    if match:
                        return {
                            LogField.TIMESTAMP.value: datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S'),
                            LogField.SCRIPT_INFO.value: match.group('script').strip('[]'),
                            LogField.PID.value: match.group('pid'),
                            LogField.LEVEL.value: match.group('level'),
                            LogField.MESSAGE.value: match.group('message').strip()
                        }
                    return None

                log_entries = []
                with open(log_file, 'r') as f:
                    for line in f:
                        log_entry = _parse_log_line(line)
                        if log_entry:
                            log_entries.append(log_entry)
                return pd.DataFrame(log_entries)

            def _generate_summary_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
                summary_df = df.groupby([LogField.PID.value, LogField.LEVEL.value]).size().unstack(fill_value=0)

                expected_levels = [severity.name for severity in Severity]
                for level in expected_levels:
                    if level not in summary_df.columns:
                        summary_df[level] = 0

                return summary_df[expected_levels].reset_index().rename_axis(None, axis=1)

            if self.log_file:
                try:
                    self.data_df = _load_log_file_as_dataframe(self.log_file)
                    if not self.data_df.empty:
                        self.summary_df = _generate_summary_from_dataframe(self.data_df)
                except Exception as e:
                    print(f"Error loading log file ('{self.log_file}'): '{e}'")

        def _try_load_json_file() -> None:
            def _load_json_file_as_dataframe(json_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
                with open(json_file, 'r') as f:
                    log_data = json.load(f)

                logs = []
                summaries = []

                for pid in log_data.get('pids', []):
                    for log in log_data[pid]['logs']:
                        log[LogField.PID.value] = pid
                        log[LogField.TIMESTAMP.value] = datetime.fromtimestamp(log[LogField.TIMESTAMP.value])
                        logs.append(log)

                    summary = log_data[pid]['summary']
                    summary_dict = {LogField.PID.value: pid}
                    for severity in Severity:
                        summary_dict[severity.name] = summary.get(severity.name, 0)
                    summaries.append(summary_dict)

                return pd.DataFrame(logs), pd.DataFrame(summaries)

            if self.json_log_file:
                try:
                    self.data_df, self.summary_df = _load_json_file_as_dataframe(self.json_log_file)
                except Exception as e:
                    print(f"Error loading JSON log file ('{self.json_log_file}'): '{e}'")
                    _try_load_log_file()

        def _cleanup_and_validate() -> None:
            if self.data_df is not None:
                required_columns = [field.value for field in LogField]
                missing_columns = [col for col in required_columns if col not in self.data_df.columns]
                if missing_columns:
                    print(f"Warning: Missing columns in log data DataFrame: {missing_columns}")

                for col in required_columns:
                    if col not in self.data_df.columns:
                        self.data_df[col] = pd.NA

                self.data_df = self.data_df[required_columns]

            if self.summary_df is not None:
                expected_columns = [LogField.PID.value] + [severity.name for severity in Severity]
                for col in expected_columns:
                    if col not in self.summary_df.columns:
                        self.summary_df[col] = 0

                self.summary_df = self.summary_df[expected_columns]
                extra_columns = [col for col in self.summary_df.columns if col not in expected_columns]
                if extra_columns:
                    self.summary_df = self.summary_df.drop(columns=extra_columns)

        # Try to load JSON log file first, then log file
        _try_load_json_file()
        if self.data_df is None or self.data_df.empty:
            _try_load_log_file()

        # Clean up and validate DataFrames
        _cleanup_and_validate()

    def get_summarized_log_entries_df(self) -> pd.DataFrame:
        '''
        Summarizes the log entries based on the log level and message.

        Returns:
            pd.DataFrame: The DataFrame containing the summarized log entries.

        Raises:
            ValueError: If no log data is available to summarize log entries.
        '''
        if self.data_df is None:
            raise ValueError("No log data available to summarize log entries")

        self.data_df[DataFrameField.SEVERITY_CODE.value] = self.data_df[LogField.LEVEL.value].apply(
            lambda level_name: (
                Severity.get_by_name(level_name).rfc_5424_numerical_code
                if Severity.get_by_name(level_name)
                else float('inf')
            )
        )

        return self.data_df.groupby([LogField.LEVEL.value, LogField.MESSAGE.value, DataFrameField.SEVERITY_CODE.value]).size().reset_index(name=DataFrameField.COUNT.value).sort_values(by=DataFrameField.SEVERITY_CODE.value)

    def get_number_of_unique_pids(self) -> Optional[int]:
        '''
        Determines the number of unique process IDs (PIDs) from the log data.

        Returns:
            Optional[int]: The number of unique PIDs.

        Raises:
            ValueError: If no log data is available to determine the number of unique PIDs.
        '''
        if self.data_df is None:
            raise ValueError("No log data available to determine number of unique PIDs")

        return self.data_df[LogField.PID.value].nunique()

    def get_number_of_log_entries(self) -> Optional[int]:
        '''
        Determines the number of log entries from the log data.

        Returns:
            Optional[int]: The number of log entries.

        Raises:
            ValueError: If no log data is available to determine the number of log entries.
        '''
        if self.data_df is None:
            raise ValueError("No log data available to determine number of log entries")

        return self.data_df.shape[0]

    def get_number_of_log_entries_by_severity(self, severity: Severity) -> Optional[int]:
        '''
        Determines the number of log entries for a specific severity level from the log data.

        Args:
            severity (Severity): The severity level.

        Returns:
            Optional[int]: The number of log entries for the specified severity level.

        Raises:
            ValueError: If no log data is available to determine the number of log entries for the specified severity level.
        '''
        if self.data_df is None:
            raise ValueError("No log data available to determine number of log entries by severity")

        return self.data_df[self.data_df[LogField.LEVEL.value] == severity.name].shape[0]

    def get_highest_severity(self) -> Optional[Severity]:
        '''
        Determines the highest severity level from the log data.

        Returns:
            Optional[Severity]: The highest severity level.

        Raises:
            ValueError: If no log data is available to determine the highest severity.
        '''
        if self.data_df is None:
            raise ValueError("No log data available to determine highest severity")
        
        severity_dict = {}

        for level_name in self.data_df[LogField.LEVEL.value].unique():
            try:
                severity = Severity.get_by_name(level_name)
                severity_dict[level_name] = severity.rfc_5424_numerical_code
            except ValueError as e:
                print(f"Warning: {e}")
                continue

        if not severity_dict:
            return None

        min_code = min(severity_dict.values())
        return Severity.get_by_code(min_code)

    def __str__(self) -> str:
        number_of_first_df_rows_to_show = 5

        df_for_log_data = None
        df_for_summary_data = None

        if self.data_df is not None:
            df_for_log_data = self.data_df.head(number_of_first_df_rows_to_show).to_string()

        if self.summary_df is not None:
            df_for_summary_data = self.summary_df.head(number_of_first_df_rows_to_show).to_string()

        return (f"Process ID: {self.pid}\n"
                f"Log Level: {self.log_level}\n"
                f"Message: {self.message}\n"
                f"Log File: {self.log_file}\n"
                f"JSON Log File: {self.json_log_file}\n\n"
                f"Log Data (max. first {number_of_first_df_rows_to_show} rows):\n{df_for_log_data if df_for_log_data else 'No log data available'}\n\n"
                f"Summary Data (max. first {number_of_first_df_rows_to_show} rows):\n{df_for_summary_data if df_for_summary_data else 'No summary data available'}")

def get_config_data(path: str, enum_class_for_config_fields: Type[Enum]) -> dict:
    '''
    Retrieves the configuration data from a specified path.

    Args:
        path (str): The path to the configuration file.
        enum_class_for_config_fields (Type[Enum]): The Enum class representing the required configuration fields.

    Returns:
        dict: The configuration data.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If a required configuration field is missing.

    Example:
        >>> from enum import Enum
        >>> class ConfigField(Enum):
        >>>    API_KEY = 'api_key'
        ...
        >>> config_data = get_config_data('~/config.json', ConfigField)
    '''
    config_path = os.path.expanduser(path)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at '{config_path}'")

    with open(config_path, 'r') as config_file:
        config_data = json.load(config_file)

        for field in enum_class_for_config_fields:
            if field.value not in config_data:
                raise ValueError(f"Required config field '{field.value}' is missing.")
            
    return config_data

class NotifierConfig:
    '''
    Represents the configuration of the notifier.
    '''
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def get_path(cls, notifier_name: str) -> str:
        '''
        Returns the path to the configuration file.

        Args:
            notifier_name (str): The name of the notifier.

        Returns:
            str: The path to the configuration file.
        '''
        return f"~/.config/simbashlog-notifier/{notifier_name}/config.json"
    
    @classmethod
    def get_data(cls, notifier_name: str, enum_class_for_config_fields: Type[Enum]) -> dict:
        '''
        Returns the configuration data.

        Args:
            notifier_name (str): The name of the notifier.
            enum_class_for_config_fields (Type[Enum]): The Enum class representing the required configuration fields.

        Returns:
            dict: The configuration data.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            ValueError: If a required configuration field is missing.
        '''
        return get_config_data(cls.get_path(notifier_name), enum_class_for_config_fields)

def process_arguments() -> StoredLogInfo:
    '''
    Processes the command-line arguments for a `simbashlog`-notifier.

    Officially supported `simbashlog`-notifier: https://github.com/fuchs-fabian/simbashlog-notifiers

    Returns:
        StoredLogInfo: Contains all important information transmitted by `simbashlog`.
    '''

    parser = argparse.ArgumentParser(description="Notifier for simbashlog.")

    parser.add_argument('--pid', type=int, help="The used process ID.")
    parser.add_argument('--log-level', type=int, help="The used log level (sourced simbashlog) / severity number (simbashlog called with arguments).")
    parser.add_argument('--message', type=str, help="The logged message (simbashlog called with arguments).")
    parser.add_argument('--log-file', type=str, help="The created *.log file.")
    parser.add_argument('--json-log-file', type=str, help="The created *_log.json file.")

    args = parser.parse_args()
    
    stored_log_info = StoredLogInfo()
    stored_log_info._update(args)

    return stored_log_info

@contextmanager
def suppress_output():
    '''
    Suppresses the output to stdout.

    This is useful when you want to suppress the output of a specific block of code you have no control over.

    Example:
        >>> with suppress_output():
            print("This will not be printed.")
    '''
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout     # Keep the old stdout
        old_stderr = sys.stderr     # Keep the old stderr
        try:
            sys.stdout = devnull    # Redirect stdout to devnull
            sys.stderr = devnull    # Optionally redirect stderr as well
            yield                   # Allow code to be run with the suppressed output
        finally:
            sys.stdout = old_stdout # Restore stdout
            sys.stderr = old_stderr # Restore stderr

def handle_unexpected_exceptions(func, *args):
    '''
    This function is used to handle unexpected exceptions that occur during the execution of the `simbashlog-notifier` script.

    If an unexpected exception occurs, the script will print an error message and exit with code 1.

    Args:
        func (function): The function that should be executed.
        *args: The arguments that should be passed to the function.

    Returns:
        The return value of the function.
    '''
    try:
        return func(*args)
    except Exception as e:
        print()
        print("┌────────────────────────────────────────────┐")
        print("│  UNEXPECTED SIMBASHLOG-NOTIFIER EXCEPTION  │")
        print("└────────────────────────────────────────────┘")
        print()

        print(f"An unexpected exception occurred while '{func.__name__}' was being processed:\n{e}")
        print()
        sys.exit(1)

def unexpected_exception_handler(func):
    '''
    Decorator to handle unexpected exceptions.

    If an unexpected exception occurs, the script will print an error message and exit with code 1.

    Args:
        func (function): The function that should be executed.

    Returns:
        function: The wrapper function that handles unexpected exceptions.

    Example:
        >>> @unexpected_exception_handler
        ... def your_function():
        ... # Your code here

        >>> your_function()
    '''
    def wrapper(*args, **kwargs):
        return handle_unexpected_exceptions(func, *args, **kwargs)
    return wrapper

class Helper:
    '''
    A helper class for various tasks.

    Attributes:
        Unicode (class):
            A class to provide Unicode representations for different purposes.
        Emoji (Enum):
            Enum to represent emojis for different meanings.
    '''
    class Unicode():
        '''
        A class to provide Unicode representations for different purposes.

        Attributes:
            get_representation_for_number (staticmethod):
                Converts a given number into its Unicode representation, where each digit is replaced by its Unicode counterpart combined with the combining enclosing keycap.
        '''
        @staticmethod
        def get_representation_for_number(number: int) -> str:
            '''
            Converts a given number into its Unicode representation, where each digit is replaced by its Unicode counterpart combined with the combining enclosing keycap.
            '''
            unicode_digits = {str(i): chr(0x0030 + i) for i in range(10)}
            unicode_number = ''.join(f"{unicode_digits[digit]}\uFE0F\u20E3" for digit in str(number))
            return unicode_number

    class Emoji(Enum):
        '''
        Enum to represent emojis for different meanings.

        Attributes:
            NOTIFIER (tuple):
                The tuple representing a notifier.
            HOST (tuple):
                The tuple representing a host.
            LOG_FILE (tuple):
                The tuple representing a log file.
            PID (tuple):
                The tuple representing a PID.
            SUMMARY (tuple):
                The tuple representing a summary.
            RESULT (tuple):
                The tuple representing a result.
        '''
        NOTIFIER = (
            "🤖",
            "\U0001F916"
            )
        HOST = (
            "🌐",
            "\U0001F310"
            )
        LOG_FILE = (
            "📄",
            "\U0001F4C4"
            )
        PID = (
            "🆔",
            "\U0001F194"
            )
        SUMMARY = (
            "📈",
            "\U0001F4C8"
            )
        RESULT = (
            "🎯",
            "\U0001F3AF"
            )

        def __init__(self, emoji, unicode):
            self._emoji = emoji
            self._unicode = unicode

        @property
        def emoji(self):
            '''
            Returns the actual emoji character.
            '''
            return self._emoji

        @property
        def unicode(self):
            '''
            Returns the Unicode character for the emoji.
            '''
            return self._unicode
        
        def __str__(self):
            return self.unicode

if __name__ == "__main__":
    process_arguments()