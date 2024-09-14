# `simbashlog-notify-helper-py`: A Python3 package that is a helper for [`simbashlog` notifiers](https://github.com/fuchs-fabian/simbashlog-notifiers)

<p align="center">
  <a href="./LICENSE">
    <img alt="GPL-3.0 License" src="https://img.shields.io/badge/GitHub-GPL--3.0-informational">
  </a>
</p>

<div align="center">
  <table>
    <tr>
      <td>
        <a href="https://github.com/fuchs-fabian/simbashlog-notify-helper-py">
          <img src="https://github-readme-stats.vercel.app/api/pin/?username=fuchs-fabian&repo=simbashlog-notify-helper-py&theme=holi&hide_border=true&border_radius=10" alt="Repository simbashlog notify helper (Python)"/>
        </a>
      </td>
    </tr>
  </table>
</div>

## Description

`simbashlog-notify-helper` is a Python3 package designed to simplify the process of handling arguments for [`simbashlog` notifiers](https://github.com/fuchs-fabian/simbashlog-notifiers).

<div align="left">
  <table>
    <tr>
      <td>
        <a href="https://github.com/fuchs-fabian/simbashlog-notifiers">
          <img src="https://github-readme-stats.vercel.app/api/pin/?username=fuchs-fabian&repo=simbashlog-notifiers&theme=holi&hide_border=true&border_radius=10" alt="Repository simbashlog-notifiers"/>
        </a>
      </td>
    </tr>
  </table>
</div>

By importing this package, you can focus solely on the logic of your notifier without worrying how to handle the arguments passed to it and how to process them.

### Features

- Automatically handles and parses command-line arguments passed by `simbashlog`.
- Supports loading from both `*.log` files and `*_log.json` files.
  - Provides access to log data in a structured format using [pandas](https://pandas.pydata.org/) DataFrames.
  - Summary generation.
- Provides access to log severity levels and their details based on [RFC 5424](https://tools.ietf.org/html/rfc5424) to create a more informative notifier.

> **Note:** This package is designed to be used with [`simbashlog`](https://github.com/fuchs-fabian/simbashlog). If you are not familiar with `simbashlog`, please have a look at the "core" repository:

<div align="left">
  <table>
    <tr>
      <td>
        <a href="https://github.com/fuchs-fabian/simbashlog">
          <img src="https://github-readme-stats.vercel.app/api/pin/?username=fuchs-fabian&repo=simbashlog&theme=holi&hide_border=true&border_radius=10" alt="Repository simbashlog"/>
        </a>
      </td>
    </tr>
  </table>
</div>

## Getting Started

> It is possible that `pip` is not yet installed. If this is not the case, you will be prompted to install it. Confirm the installation.

### Installation with `pip` (GitHub)

```bash
pip install git+https://github.com/fuchs-fabian/simbashlog-notify-helper-py
```

### Installation with `pip` (Local)

Download the repository and navigate to the directory containing the [`setup.py`](setup.py) file.

```bash
pip install .
```

### Check Installation

```bash
pip list
```

```bash
pip show simbashlog-notify-helper
```

### Usage

```python
#!/usr/bin/env python3

import simbashlog_notify_helper as snh

def main():
    # Process command-line arguments
    stored_info = snh.process_arguments()

    # Your notifier logic here
    # ...

if __name__ == "__main__":
    main()
```

#### Example usage / notifier (symbolic)

```python
#!/usr/bin/env python3

import sys
import simbashlog_notify_helper as snh

def main():
    # Process command-line arguments
    stored_info = snh.process_arguments()

    print("---------------------------------------------------------------------------------")

    # Print the stored log information
    print("\nStored Log Information:")
    print(stored_info)

    print("---------------------------------------------------------------------------------\n")

    # Print all severity levels and details for ERROR severity
    for severity in snh.Severity:
        print(severity)

    # Access details for ERROR severity
    print(f"\n{snh.Severity.ERROR}")

    print(f"\nName: {snh.Severity.ERROR.name}")
    print(f"RFC 5424 Numerical Code: {snh.Severity.ERROR.rfc_5424_numerical_code}")
    print(f"RFC 5424 Severity: {snh.Severity.ERROR.rfc_5424_severity}")
    print(f"RFC 5424 Description: {snh.Severity.ERROR.rfc_5424_description}")
    print(f"Emoji: {snh.Severity.ERROR.emoji}")
    print(f"Unicode: {snh.Severity.ERROR.unicode}")

    print("---------------------------------------------------------------------------------")

    # Optionally, access DataFrame if available
    if stored_info.data_df is not None:
        print("\nData DataFrame:")
        print(stored_info.data_df)
        
        # Example: Count how many logs have the same message
        message_counts = stored_info.data_df[snh.LogField.MESSAGE.value].value_counts()
        print("\nMessage Counts:")
        print(message_counts)

        # Example: Count how many ERRORs are logged
        error_count = stored_info.data_df[stored_info.data_df[snh.LogField.LEVEL.value] == snh.Severity.ERROR.name].shape[0]
        print(f"\nNumber of ERROR logs: {error_count}")

        # Example: Count how many unique PIDs are in the DataFrame
        unique_pids_count = stored_info.data_df[snh.LogField.PID.value].nunique()
        print(f"\nNumber of unique PIDs: {unique_pids_count}")

        print("---------------------------------------------------------------------------------")

    # Optionally, print summary DataFrame if available
    if stored_info.summary_df is not None:
        print("\nSummary DataFrame:")
        print(stored_info.summary_df)
        
        # Example: Total counts of each severity level in the summary DataFrame
        severity_totals = stored_info.summary_df.drop(columns=snh.LogField.PID.value).sum()
        print("\nTotal counts of each severity level:")
        for severity, count in severity_totals.items():
            print(f"{severity}: {count}")

        # Example: Number of unique PIDs in the summary DataFrame
        unique_pids_in_summary = stored_info.summary_df[snh.LogField.PID.value].nunique()
        print(f"\nNumber of unique PIDs in summary DataFrame: {unique_pids_in_summary}")

        print("---------------------------------------------------------------------------------")

    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Uninstall

```bash
pip uninstall simbashlog-notify-helper
```

## Bugs, Suggestions, Feedback, and Needed Support

> If you have any bugs, suggestions or feedback, feel free to create an issue or create a pull request with your changes.

## Support Me

If you like `simbashlog`'s ecosystem, you think it is useful and saves you a lot of work and nerves and lets you sleep better, please give it a star and consider donating.

<a href="https://www.paypal.com/donate/?hosted_button_id=4G9X8TDNYYNKG" target="_blank">
  <!--
    https://github.com/stefan-niedermann/paypal-donate-button
  -->
  <img src="https://raw.githubusercontent.com/stefan-niedermann/paypal-donate-button/master/paypal-donate-button.png" style="height: 90px; width: 217px;" alt="Donate with PayPal"/>
</a>