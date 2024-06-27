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
plt.rcParams['figure.figsize'] = (8, 5)
plt.rcParams['axes.labelsize'] = 19
plt.rcParams['xtick.labelsize'] = 17
plt.rcParams['ytick.labelsize'] = 17
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'

pd.set_option('display.max_colwidth', None)


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate RQ4 figures')
    parser.add_argument("data_qual", help="CSV with qualitative bug metrics.")

    parser.add_argument("data_quant", help="CSV with quantitative bug metrics.")
    parser.add_argument(
            "--directory",
            help="Directory to save the RQ4 figures.")

    return parser.parse_args()

def construct_dataframe(filepath_qual, filepath_quant):
    dataframe = pd.read_csv(filepath_quant)
    dataframe['Created At'] = pd.to_datetime(dataframe['Created At'])
    dataframe['Closed At'] = pd.to_datetime(dataframe['Closed At'])
    qual = pd.read_csv(filepath_qual)
    qual = qual[["Component", "Issue URL"]]
    dataframe = pd.merge(dataframe, qual)
    dataframe["Component"] = dataframe["Component"].replace("Code",
                                                    "Configuration unit")
    dataframe["Component"] = dataframe["Component"].replace("Configuration",
                                                    "IaC program")
    dataframe["Total Files"] = dataframe.apply(
        lambda row: row["Config Unit Files Count"]
        if row["Component"] == "Configuration unit" else 
        row["IAC Program Unit Files Count"] + row["Template Unit Files Count"], axis=1)
    dataframe["Total LoC"] = dataframe.apply(
        lambda row: row["Config Unit Lines Added"] + row["Config Unit Lines Removed"] 
        if row["Component"] == "Configuration unit" else 
        row["IAC Program Unit Lines Added"] + row["Template Unit Lines Added"] + 
        row["IAC Program Unit Lines Removed"] + row["Template Unit Lines Removed"], axis=1)

    return dataframe

def get_fractions(x, total=360, print_all_points=False):
    x_dict = defaultdict(lambda: 0)
    for l in x:
        x_dict[l] += 1
    number_of_x = sorted(x_dict.keys())
    number_of_bugs = [x_dict[k] for k in number_of_x]
    x_fractions = [(sum(number_of_bugs[:i]) / total) * 100
                for i in range(1, len(number_of_bugs)+1)]
    if print_all_points:
        for fr, l in zip(x_fractions, number_of_x):
            print(l, fr)
    return number_of_x, x_fractions

def plot_loc_cumulative_distribution_per_component(dataframe, output):
    f, ax = plt.subplots()
    all_files, all_fractions = get_fractions( dataframe["Total LoC"], 360, False) 
    config_dataset =   dataframe[dataframe["Component"]=="Configuration unit"]
    iac_dataset =   dataframe[dataframe["Component"]=="IaC program"]
    # print(len(dataframe[dataframe["Total LoC"]<100]))
    # print(len(dataframe[dataframe["Total LoC"]<5]))

    config_unit_files,  config_unit_fractions = get_fractions(config_dataset["Config Unit Lines Added"]+config_dataset["Config Unit Lines Removed"], len(config_dataset), False)
    iac_unit_files,  iac_unit_fractions = get_fractions(iac_dataset["IAC Program Unit Lines Added"]+iac_dataset["Template Unit Lines Added"]+iac_dataset["IAC Program Unit Lines Removed"]+iac_dataset["Template Unit Lines Removed"], len(iac_dataset), False)

    conf = ax.plot( config_unit_files, config_unit_fractions, marker=None, linestyle="--", c="#56B4E9", linewidth=2.5,  label="Configuration Unit")
    iac = ax.plot( iac_unit_files, iac_unit_fractions, marker=None, linestyle=":", c="#009E73", linewidth=2.5, label="IaC Program Unit")
    total = ax.plot(all_files, all_fractions, label="All", linewidth=4, linestyle="-", c="#FFA726")
    ax.set_xlabel('LoC in a Fix')
    ax.set_ylabel('Bug Prevalence (%)')
    ax.set_xscale('log')

    ax.legend(loc="lower right", fontsize=16)
    ax.set_xticks([1, 3, 5, 10, 25, 50, 100, 200, 1000, 3000])
    ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    plt.ylim([0, 100])
    plt.xlim([1, 3000])

    dest = output+"/lines.pdf"
    plt.savefig(dest, format='pdf', bbox_inches='tight', pad_inches=0)

def plot_file_cumulative_distribution_per_component(dataframe, output):
    f, ax = plt.subplots()
    all_files, all_fractions = get_fractions( dataframe["Total Files"], 360, False) 
    config_dataset =   dataframe[dataframe["Component"]=="Configuration unit"]
    iac_dataset =   dataframe[dataframe["Component"]=="IaC program"]
    config_unit_files,  config_unit_fractions = get_fractions(config_dataset["Config Unit Files Count"], len(config_dataset), False)
    iac_unit_files,  iac_unit_fractions = get_fractions(iac_dataset["IAC Program Unit Files Count"]+iac_dataset["Template Unit Files Count"], len(iac_dataset), False)
    # print(len(dataframe[dataframe["Total Files"]==1]))
    # print(len(dataframe[dataframe["Total Files"]<=3]))
    conf = ax.plot( config_unit_files, config_unit_fractions, marker=None, linestyle="--", c="#56B4E9", linewidth=2.5,  label="Configuration Unit")
    iac = ax.plot( iac_unit_files, iac_unit_fractions, marker=None, linestyle=":", c="#009E73", linewidth=2.5, label="IaC Program Unit")
    total = ax.plot(all_files, all_fractions, label="All", linewidth=4, linestyle="-", c="#FFA726")

    ax.set_xlabel('Number of Files in a Fix')
    ax.set_ylabel('Bug Prevalence (%)')
    ax.set_xscale('log')

    ax.legend(loc="lower right", fontsize=16)
    ax.set_xticks([1, 2, 3, 4, 5, 8, 10, 18])
    ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    plt.ylim([0, 100])
    plt.xlim([1, 19])

    dest = output+"/files.pdf"
    plt.savefig(dest, format='pdf', bbox_inches='tight', pad_inches=0)

def plot_test_file_cumulative_distribution_per_ecosystem(dataframe, output):
    f, ax = plt.subplots() 
    # Calculate the fraction of bugs with zero test files affected
    zero_test_files_fraction = (dataframe["Test Unit Files Count"] == 0).sum() / len(dataframe) * 100
    # Get fractions for the rest
    test_unit_files, test_unit_fractions = get_fractions(dataframe["Test Unit Files Count"], len(dataframe), False)

    # Include the zero count by appending it to the beginning of your lists
    test_unit_files = np.insert(test_unit_files, 0, 0)  # Insert a 0 at the start for no files
    test_unit_fractions = np.insert(test_unit_fractions, 0, zero_test_files_fraction)  # Start from the fraction with zero files
    ansible = dataframe[dataframe["Ecosystem"] == "Ansible"]
    puppet = dataframe[dataframe["Ecosystem"] == "Puppet"]
    chef = dataframe[dataframe["Ecosystem"] == "Chef"]
    puppet_test_unit_files, puppet_test_unit_fractions = get_fractions(puppet["Test Unit Files Count"], len(puppet), False)
    ansible_test_unit_files, ansible_test_unit_fractions = get_fractions(ansible["Test Unit Files Count"], len(ansible), False)
    chef_test_unit_files, chef_test_unit_fractions = get_fractions(chef["Test Unit Files Count"], len(chef), False)
    # print(len(dataframe[dataframe["Test Unit Files Count"]==0]))
    # print(len(chef[chef["Test Unit Files Count"]==0]))

    # Plotting the line for test files
    puppet = ax.plot(puppet_test_unit_files, puppet_test_unit_fractions, marker=None, linewidth=2.5, label="Puppet", linestyle="-.", c="#CC79A7")
    ansible = ax.plot(ansible_test_unit_files, ansible_test_unit_fractions, marker=None, linewidth=2.5, label="Ansible", linestyle="-.", c="#56B4E9")
    chef = ax.plot(chef_test_unit_files, chef_test_unit_fractions, marker=None, linewidth=2.5, label="Chef", linestyle=":", c="#009E73",)
    total = ax.plot(test_unit_files, test_unit_fractions, marker=None, linewidth=4, label="All", c= "#FFA726")


    ax.set_xlabel('Number of Test Files in a Fix')
    ax.set_ylabel('Bug Prevalence (%)')
    ax.set_xscale('symlog')
    
    # Customize x-ticks
    ax.set_xticks([0, 1, 2, 3, 4, 5, 8, 10, 15])
    ax.set_yticks([0, 10, 40, 60, 80 , 90, 100])

    ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    ax.legend(loc="lower right", fontsize=16)

    # Customize y-axis limits
    plt.ylim([0, 100])
    plt.xlim([0, 15])

    dest = output+"/test_files.pdf"
    plt.savefig(dest, format='pdf', bbox_inches='tight', pad_inches=0)

def plot_test_file_cumulative_distribution_per_component(dataframe, output):
    f, ax = plt.subplots()

    config_dataset =   dataframe[dataframe["Component"]=="Configuration unit"]
    iac_dataset =   dataframe[dataframe["Component"]=="IaC program"]

    config_unit_files,  config_unit_fractions = get_fractions(config_dataset["Test Unit Files Count"], len(config_dataset), False)
    iac_unit_files,  iac_unit_fractions = get_fractions(iac_dataset["Test Unit Files Count"], len(iac_dataset), False)
    # print(len(iac_dataset[iac_dataset["Test Unit Files Count"]==0])/len(iac_dataset))
    # print(len(config_dataset[config_dataset["Test Unit Files Count"]==0])/len(config_dataset))
    iac = ax.plot( iac_unit_files, iac_unit_fractions, marker=None, linestyle="--", c="#009E73", linewidth=2.5, label="IaC Program Unit")
    conf = ax.plot( config_unit_files, config_unit_fractions, marker=None, linestyle="--", c="#56B4E9", linewidth=2.5,  label="Configuration Unit")

    ax.set_xlabel('Number of Test Files in a Fix')
    ax.set_ylabel('Bug Prevalence (%)')
    ax.set_xscale('symlog')
    
    # Customize x-ticks
    ax.set_xticks([0, 1, 2, 3, 4, 5, 8, 10, 15])
    ax.set_yticks([0, 10, 40, 60, 80 , 90, 100])

    ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    ax.legend(loc="lower right", fontsize=16)

    # Customize y-axis limits
    plt.ylim([0, 100])
    plt.xlim([0, 15])

    dest = output+"/test_files_component.pdf"
    plt.savefig(dest, format='pdf', bbox_inches='tight', pad_inches=0)


def print_distribution(dataframe, groupby, column):
    ecosystems = dataframe[groupby].unique()
    stats = pd.DataFrame(columns=['Mean', 'Median', 'SD', 'Min', 'Max'])
    ecosystems = np.append(ecosystems, "All")
    for eco in ecosystems:
        if eco == 'All':
            metric = dataframe[column]
        else:
            metric = dataframe[dataframe[groupby] == eco][column]
        stats.loc[eco] = [
            metric.mean(),
            metric.median(),
            metric.std(),
            metric.min(),
            metric.max()
        ]

    if column == "Total Files":
        print("         Number of Source Files in a Fix per "+groupby)
    elif column == "Total LoC":
        print("         Number of Lines of Code (LoC) in a Fix per "+groupby)
    else:
        print("         Number of Test Files in a Fix per "+groupby)
    print("======================================================================")
    print("                          Mean    Median        SD       Min       Max")
    print("----------------------------------------------------------------------")
    for eco, row in stats.iterrows():
        print(f"{eco:<20}{row['Mean']:>10.2f}{row['Median']:>10.2f}{row['SD']:>10.2f}{row['Min']:>10.2f}{row['Max']:>10.2f}")
    print("----------------------------------------------------------------------")
    print()



def main():
    args = get_args()
    dataframe = construct_dataframe(args.data_qual, args.data_quant)
    plot_loc_cumulative_distribution_per_component(dataframe, args.directory)
    plot_file_cumulative_distribution_per_component(dataframe, args.directory)
    plot_test_file_cumulative_distribution_per_ecosystem(dataframe, args.directory)
    plot_test_file_cumulative_distribution_per_component(dataframe, args.directory)
    print_distribution(dataframe, "Component", "Total LoC")
    print_distribution(dataframe, "Component", "Total Files")
    print_distribution(dataframe, "Ecosystem", "Test Unit Files Count")
    print_distribution(dataframe, "Component", "Test Unit Files Count")
    


if __name__ == "__main__":
    main()
