#!/usr/bin/env python3

import simbashlog_notify_helper as snh # type: ignore

def main():

    print()
    print("┌─────────────────────┬──────────────────────┐")
    print("│                   ENUMS                    │")
    print("└─────────────────────┴──────────────────────┘")
    print()

    print("`snh.Severity`:")

    for severity in snh.Severity:
        print(f"\n\t`snh.Severity.{severity.name}`: {severity}")
        print(f"\t`snh.Severity.{severity.name}.name`: {severity.name}")
        print(f"\t`snh.Severity.{severity.name}.value`: {severity.value}")
        print(f"\t`snh.Severity.{severity.name}.rfc_5424_numerical_code`: {severity.rfc_5424_numerical_code}")
        print(f"\t`snh.Severity.{severity.name}.rfc_5424_severity`: {severity.rfc_5424_severity}")
        print(f"\t`snh.Severity.{severity.name}.rfc_5424_description`: {severity.rfc_5424_description}")
        print(f"\t`snh.Severity.{severity.name}.emoji`: {severity.emoji}")
        print(f"\t`snh.Severity.{severity.name}.unicode`: {severity.unicode}")

    print("\n\tFunctions:\n")

    for i in range(0, 9):
        try:
            severity = snh.Severity.get_by_code(i)
            print(f"\t\t`snh.Severity.get_by_code({i})`: {severity.name}")
        except ValueError as e:
            print(f"\t\t`snh.Severity.get_by_code({i})`: {e}")

    print("\n")

    for severity in snh.Severity:
        try:
            severity = snh.Severity.get_by_name(severity.name)
            print(f"\t\t`snh.Severity.get_by_name({severity.name})`: {severity.name}")
        except ValueError as e:
            print(f"\t\t`snh.Severity.get_by_name({severity.name})`: {e}")

    invalid_severity_name = "INVALID"
    try:
        severity = snh.Severity.get_by_name(invalid_severity_name)
        print(f"\t\t`snh.Severity.get_by_name({invalid_severity_name})`: {severity.name}")
    except ValueError as e:
        print(f"\t\t`snh.Severity.get_by_name({invalid_severity_name})`: {e}")

    print("\n`snh.LogField`:")

    for log_field in snh.LogField:
        print(f"\n\t`snh.LogField.{log_field.name}`: {log_field}")
        print(f"\t`snh.LogField.{log_field.name}.name`: {log_field.name}")
        print(f"\t`snh.LogField.{log_field.name}.value`: {log_field.value}")


    print("\n`snh.DataFrameField`:")

    for df_field in snh.DataFrameField:
        print(f"\n\t`snh.DataFrameField.{df_field.name}`: {df_field}")
        print(f"\t`snh.DataFrameField.{df_field.name}.name`: {df_field.name}")
        print(f"\t`snh.DataFrameField.{df_field.name}.value`: {df_field.value}")

    print()
    print("┌─────────────────────┬──────────────────────┐")
    print("│             STORED LOG INFO                │")
    print("└─────────────────────┴──────────────────────┘")
    print()

    print("To process the arguments and get the stored log info: `stored_log_info = snh.process_arguments()`")
    stored_log_info = snh.process_arguments()

    print(stored_log_info)

    print("\nDataFrames:")

    print(f"\n\t`stored_log_info.data_df`:\n\n{stored_log_info.data_df}")

    print(f"\n\t`stored_log_info.summary_df`:\n\n{stored_log_info.summary_df}")

    print(f"\n\t`stored_log_info.get_summarized_log_entries_df()`:\n")
    try:
        print(stored_log_info.get_summarized_log_entries_df())
    except ValueError as e:
        print(e)


    print("\nOther helpful functions:")

    number_of_unique_pids_str = "\n\t`stored_log_info.get_number_of_unique_pids()`:"
    try:
        print(f"{number_of_unique_pids_str} {stored_log_info.get_number_of_unique_pids()}")
    except ValueError as e:
        print(f"{number_of_unique_pids_str} {e}")

    number_of_log_entries_str = "\n\t`stored_log_info.get_number_of_log_entries()`:"
    try:
        print(f"{number_of_log_entries_str} {stored_log_info.get_number_of_log_entries()}")
    except ValueError as e:
        print(f"{number_of_log_entries_str} {e}")

    number_of_log_entries_by_severity_for_critical_str = "\n\t`stored_log_info.get_number_of_log_entries_by_severity(snh.Severity.CRIT)`:"
    try:
        print(f"{number_of_log_entries_by_severity_for_critical_str} {stored_log_info.get_number_of_log_entries_by_severity(snh.Severity.CRIT)}")
    except ValueError as e:
        print(f"{number_of_log_entries_by_severity_for_critical_str} {e}")

    highest_severity_str = "\n\t`stored_log_info.get_highest_severity()`:"
    try:
        print(f"{highest_severity_str} {stored_log_info.get_highest_severity()}")
    except ValueError as e:
        print(f"{highest_severity_str} {e}")

    print()
    print("┌─────────────────────┬──────────────────────┐")
    print("│                   HELPER                   │")
    print("└─────────────────────┴──────────────────────┘")
    print()

    print("`snh.Helper.Unicode`:\n")

    for i in range(0, 11):
        print(f"\t`snh.Helper.Unicode.get_representation_for_number({i})`: {snh.Helper.Unicode.get_representation_for_number(i)}")

    print("\n`snh.Helper.Emoji`:")

    for emoji in snh.Helper.Emoji:
        print(f"\n\t`snh.Helper.Emoji.{emoji.name}`: {emoji}")
        print(f"\t`snh.Helper.Emoji.{emoji.name}.name`: {emoji.name}")
        print(f"\t`snh.Helper.Emoji.{emoji.name}.value`: {emoji.value}")
        print(f"\t`snh.Helper.Emoji.{emoji.name}.emoji`: {emoji.emoji}")
        print(f"\t`snh.Helper.Emoji.{emoji.name}.unicode`: {emoji.unicode}")

if __name__ == "__main__":
    main()