# `simbashlog-example-notifier`: Example notifier (template)

<!-- Description -->

This is a kind of template for creating a notifier for `simbashlog`.

## Installation

<!-- Installation with `pip` (GitHub) -->

```bash
pip install git+https://github.com/fuchs-fabian/simbashlog-notify-helper-py.git#subdirectory=template
```

<!--
If the repository is `simbashlog-notifiers`, the following will be used: 

```bash
pip install git+https://github.com/fuchs-fabian/simbashlog-notifiers.git#subdirectory=src/python/<your subdirectory name>
```

<your subdirectory name> is the same as the name in `REPOSITORY_PYTHON_SUBDIRECTORY_NAME`.
-->

## Configuration

<!-- Location of the configuration file -->

```plain
~/.config/simbashlog-notifier/simbashlog-example-notifier/config.json
```

<!-- Default configuration -->

```json
{
    "min_required_log_level": "6",
    "show_in_console_sent_message": "true",
    "show_in_header_pid": "false",
    "show_in_body_log_file_result": "false",
    "show_in_body_log_file_content": "false",
    "show_in_body_summary_for_pid": "false",
    "show_in_body_summary_for_log_file": "false",
    "show_in_footer_log_file_names": "false",
    "show_in_footer_host": "false",
    "show_in_footer_notifier_name": "true",
    "example_key": "example_value"
}
```

<!-- Optional: Usage -->