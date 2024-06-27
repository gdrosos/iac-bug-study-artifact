import argparse
from datetime import datetime
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import numpy as np



plt.style.use('ggplot')
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (7, 3)
plt.rcParams['axes.labelsize'] = 17
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'

pd.set_option('display.max_colwidth', None)


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate rq3 figures')
    parser.add_argument("data", help="CSV with bugs.")
    parser.add_argument(
            "--output",
            default="system-state.pdf",
            help="Filename to save the System State Requirements figure.")
    parser.add_argument(
        "--os",
        action="store_true",
        help="Print data of OS Tree")
    parser.add_argument(
        "--not_managed",
        action="store_true",
        help="Print system state requirements of 'Not managed by code' Bugs")
    parser.add_argument(
        "--ecosystems",
        action="store_true",
        help="Print system state requirements across different ecosystems")
    parser.add_argument(
        "--test_inputs",
        action="store_true",
        help="Print distribution of test inputs")
    return parser.parse_args()


def construct_dataframe(filepath, os, not_managed, ecosystems, tests):
    dataframe = pd.read_csv(filepath)
    dataframe["Component"] = dataframe["Component"].replace("Code",
                                                    "Configuration unit")
    dataframe["Component"] = dataframe["Component"].replace("Configuration",
                                                    "IaC program")
    dataframe = dataframe[["Ecosystem", "Component",
                            "System state", "OS Sensitivity", "Operating System/Platform", "System State Observations", "Test Input"]]

    dataframe["System state"] = dataframe["System state"].replace("Out of the box",
                                                    "State agnostic")

    if not os and not not_managed and not ecosystems and not tests:
        # Then perform your grouping on the filtered DataFrame
        grouped = dataframe.groupby(["Component", 'System state']).size().reset_index(name='Frequency')
        level_counts = dataframe.groupby(["Component"]).size()
        # Correctly calculate the percentage using the 'level_counts' for each 'Ecosystem'
        grouped['Percentage'] = grouped.apply(lambda row: (row['Frequency'] / level_counts[row["Component"]]) * 100, axis=1).map(lambda x: '{:.2f}%'.format(x))
        print(grouped.to_string(index=False))
    elif ecosystems:
        grouped = dataframe.groupby(["Ecosystem", 'System state']).size().reset_index(name='Frequency')
        level_counts = dataframe.groupby(["Ecosystem"]).size()
        # Correctly calculate the percentage using the 'level_counts' for each 'Ecosystem'
        grouped['Percentage'] = grouped.apply(lambda row: (row['Frequency'] / level_counts[row["Ecosystem"]]) * 100, axis=1).map(lambda x: '{:.2f}%'.format(x))
        print(grouped.to_string(index=False))
    return dataframe

def print_os_tree(dataframe):
    different_rows = dataframe[dataframe['Operating System/Platform'] != dataframe['OS Sensitivity'].str.replace(" \(version\)", "", regex=True).str.replace("Insensitive", "Independent", regex=True)]
    single_os_support_cnt = different_rows["Operating System/Platform"].count()
    os_insensitive_cnt = dataframe[dataframe['OS Sensitivity']=="Insensitive"]["Operating System/Platform"].count()
    multiple_os_support_cnt = os_insensitive_cnt-single_os_support_cnt
    buggy_os = dataframe[dataframe['OS Sensitivity']!="Insensitive"]["OS Sensitivity"]
    debian_cnt=0
    debian_cnt_version = 0
    redhat_cnt=0
    redhat_cnt_version = 0
    others_linux_cnt=0
    others_linux_cnt_version=0

    windows_cnt=0
    windows_cnt_version = 0
    others_cnt=0
    others_cnt_version=0
    for i in buggy_os:
        if "Windows" in i:
            if "(version)" in i:
                windows_cnt_version+=1
            else:
                windows_cnt+=1
        elif any(os in i for os in ["Debian", "Ubuntu"]):
            if "(version)" in i:
                debian_cnt_version+=1
            else:
                debian_cnt+=1     
        elif any(os in i for os in ["RHEL", "CentOS", "OracleLinux", "Fedora", "RedHat"]):
            if "(version)" in i:
                redhat_cnt_version+=1
            else:
                redhat_cnt+=1 
        elif any(os in i for os in ["Linux", "amazon", "Suse", "Archlinux"]):
            if "(version)" in i:
                others_linux_cnt_version+=1
            else:
                others_linux_cnt+=1    
        else:
            if "(version)" in i:
                others_cnt_version+=1
            else:
                others_cnt+=1   

    linux_cnt = others_linux_cnt + debian_cnt + redhat_cnt
    linux_cnt_version = others_linux_cnt_version + debian_cnt_version + redhat_cnt_version
    os_sensitive_version_cnt = linux_cnt_version+windows_cnt_version+others_cnt_version
    os_sensitive_cnt =  linux_cnt+windows_cnt+others_cnt
    print(f"{'Category':<34}{'Version Agnostic':<34}{'Version Dependent':<20}{'Total':<20}")
    print("-" * 100)
    print(f"{'Debian Family':<34}{debian_cnt:<34}{debian_cnt_version:<20}{debian_cnt+debian_cnt_version:<20}")
    print(f"{'RedHat Family':<34}{redhat_cnt:<34}{redhat_cnt_version:<20}{redhat_cnt+redhat_cnt_version:<20}")
    print(f"{'Other Linux':<34}{others_linux_cnt:<34}{others_linux_cnt_version:<20}{others_linux_cnt+others_linux_cnt_version:<20}")
    print("-" * 100)
    print(f"{'Total Linux (Subtotal)':<34}{linux_cnt:<34}{linux_cnt_version:<20}{linux_cnt+linux_cnt_version:<20}")
    print(f"{'Windows':<34}{windows_cnt:<34}{windows_cnt_version:<20}{windows_cnt+windows_cnt_version:<20}")
    print(f"{'Other OS':<34}{others_cnt:<34}{others_cnt_version:<20}{others_cnt+others_cnt_version:<20}")
    print("-" * 100)
    print(f"{'Total OS Sensitive (Subtotal)':<34}{os_sensitive_cnt:<34}{os_sensitive_version_cnt:<20}{os_sensitive_cnt+os_sensitive_version_cnt:<20}")
    # print("-" * 100)
    print(f"{'Single OS Support':<34}{single_os_support_cnt:<34}{'0':<20}{single_os_support_cnt:<20}")
    print(f"{'Multiple OS Support':<34}{multiple_os_support_cnt:<34}{'0':<20}{multiple_os_support_cnt:<20}")
    print("-" * 100)
    # print(f"{'Total OS Insensitive (Subtotal)':<34}{os_insensitive_cnt:<34}{'0':<20}{os_insensitive_cnt:<20}")
    # print("-" * 100)
    print(f"{'Grand Total':<34}{os_sensitive_cnt+os_insensitive_cnt:<34}{os_sensitive_version_cnt:<20}{os_sensitive_cnt+os_insensitive_cnt+os_sensitive_version_cnt:<20}")

def plot_diagram(dataframe, output):
    color_pallette = ['#56B4E9', '#009E73', '#CC79A7']
    groupby = "Component"
    legend = "Component"
    system_state_counts = dataframe.groupby(['System state',
                                        groupby]).size().unstack()
    system_state_counts['Total'] = system_state_counts.sum(axis=1)
    system_state_counts_sorted = system_state_counts.sort_values(by='Total',
                                                       ascending=False)
    count = system_state_counts['Total'].sum()
    ax = system_state_counts_sorted.drop(columns='Total').plot(
        kind='barh', width=0.3, stacked=True, color=color_pallette)

    # Annotate total occurrences next to the bars
    for i, (index, row) in enumerate(system_state_counts_sorted.iterrows()):
        total = row['Total']
        ax.text(total, i, f' {int(total)}/{int(count)}', va='center',
                ha='left', size=10)

    # Move the legend inside the plot area in the bottom right corner
    ax.legend(title=legend, bbox_to_anchor=(0.9, 0.38), frameon=True)
    plt.xlabel('')
    plt.ylabel('')
    plt.gca().invert_yaxis()  # To display the highest value at the top
    plt.savefig(output, format='pdf', bbox_inches='tight', pad_inches=0, dpi=300)

def plot_not_managed(dataframe, output):
    dataframe = dataframe[dataframe["System state"] == "Unmanaged state"]
    file_count = 0
    service_count = 0
    db_count = 0
    host_count = 0
    package_count = 0
    mult_exec_cnt=0
    ds_cnt=0
    for i in dataframe['System State Observations']:
        requirements = str(i).split(";")    
        for x in requirements:
            if "file" in x:
                file_count+=1
            elif 'service' in x:
                service_count+=1
            elif 'host' in x:
                host_count+=1
            elif 'package' in x:
                package_count+=1
            else:
                # print(x)
                ds_cnt+=1

    maps = {
        "package": "Package",
        "file": "File",
        "IaC": "Runtime",
        "service": "Service",
        "object": "Other",
        "user": "Other",
        "process": "Other",
        "multiple execution": "Other",
        "multiple run": "Other",
        "PL": "Runtime",
        "host": "Remote host",
        # "SSH configuration": "Remote host",
    }


    elements = defaultdict(lambda: 0)
    for i in dataframe['System State Observations']:
        requirements = str(i).split(";")   
        freqs = set()
        for x in requirements:
            if x:
                flag = False
                for k, v in maps.items():
                    if k in x or k == x:
                        freqs.add(v)
                        flag = True
                if not flag:
                    print(x)
            for k in freqs:
                elements[k] += 1
    print (elements)
    data = {
        'Requirements': ['File', 'Service', 'Remote host', 'Other', 'Package', "IaC Runtime"],
        'Frequency': [file_count, service_count, host_count, ds_cnt, package_count, 19]
    }
    df2 = pd.DataFrame(data)
    df2['Frequency'] = df2['Frequency'].astype(int)
    df_sorted = df2.sort_values('Frequency', ascending=False)
    df_sorted['Percentage'] = df_sorted.apply(lambda row: (row['Frequency'] /119) * 100, axis=1).map(lambda x: '{:.2f}%'.format(x))
    print("Distribution of system state requirements of bugs whose system state is not managed by code:")
    print('-'*40)
    print(df_sorted.to_string(index=False))
    plt.subplots_adjust(bottom=0.1, top=0.9)
    ax = sns.barplot(x='Frequency', y='Requirements', data=df_sorted, color="#FFA726")
    for i, (index, row) in enumerate(df_sorted.iterrows()):
        total = row['Frequency']

        ax.text(total, i, f' {int(total)}/{119}', va='center', ha='left', size=10)

    plt.xlabel('')
    plt.ylabel('')
    plt.savefig(output, format='pdf', bbox_inches='tight', pad_inches=0, dpi=300)


def plot_tests(dataframe, output):
    maps = {
        "shell": "command",
        "uri": "network",
        "package": "package",
        "host": "network",
        "db": "db",
        "cloud": "cloud",
        "port": "network",
        "service connection": "auth",
        "command options": "command",
        "network": "network",
        "URI": "network",
        "glob": "fs",
        "file": "fs",
        "CLI options": "command",
        "auth": "auth",
        "protocol": "network",
        "docker": "docker",
        "ip": "network",
        "firewall rule": "network",
        "locales": "OS general",
        "service  connection": "auth",
        "regex": "regex",
        "ssh key": "auth",
        "OS": "OS general",
        "command": "command",
        "environment variables": "OS general",
        "firewall": "network",
        "NetworkManager": "network",
        "URL": "network",
        "IP": "network",
        "token": "auth",
        "DNS": "network",
        "FQDN": "network",
        "container": "docker",
        "interface": "network",
        "AWS": "cloud",
        "HPE": "cloud",
        "version": "package",
        "mysql": "db",
        "username": "OS general",
        "credentials": "auth",
        "url": "network",
        "fstype": "fs",
        "args": "args",
        "checksum": "auth"
    }



    elements = defaultdict(lambda: 0)
    for i in dataframe['Test Input'].dropna():
        requirements = i.replace("; ", ";").split(";")
        freqs = set()
        for elem in requirements:
            if elem:
                flag = False
                for k, v in maps.items():
                    if k in elem or k == elem:
                        freqs.add(v)
                        flag = True
                # if not flag:
                #     print(elem)
        for k in freqs:
            elements[k] += 1
                # if not flag:
                #     print(x)

    total = 360
    percentages = {k: (v / total) * 100 for k, v in elements.items()}

    # Define the mapping from internal names to display names
    display_names = {
        'network': 'Network (IP, port, firewall)',
        'fs': 'File system (path, attrs)',
        'package': 'Package (name, version)',
        'auth': 'Authentication (token, login info)',
        'command': 'Command (shell)'
    }

    # Create the output table
    output_table = []
    for key in ['network', 'fs', 'package', 'auth', 'command']:
        if key in percentages:
            output_table.append((display_names[key], f"{percentages[key]:.0f}%"))

    # Print the table
    print("Data type                          Occ (%)")
    print("-----------------------------------------")
    for row in output_table:
        print(f"{row[0]:<35} {row[1]}")

def main():
    args = get_args()
    dataframe = construct_dataframe(args.data, args.os, args.not_managed, args.ecosystems, args.test_inputs)
    if not args.ecosystems:
        if args.os:
            print_os_tree(dataframe)
        elif args.not_managed:
            plot_not_managed(dataframe, args.output)
        elif args.test_inputs:
            plot_tests(dataframe, args.output)
        else:
            plot_diagram(dataframe, args.output)


if __name__ == "__main__":
    main()
