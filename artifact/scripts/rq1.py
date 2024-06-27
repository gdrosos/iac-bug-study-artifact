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
plt.rcParams['figure.figsize'] = (5, 4)
plt.rcParams['axes.labelsize'] = 17
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'

pd.set_option('display.max_colwidth', None)


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate symptoms figure')
    parser.add_argument("data", help="CSV with bugs.")
    parser.add_argument(
            "--output",
            default="symtpoms.pdf",
            help="Filename to save the symptoms figure.")
    parser.add_argument(
            "--ecosystem",
            action="store_true",
            help="Group by IaC ecosystem.")
    return parser.parse_args()


def construct_dataframe(filepath, per_ecosystem: bool):
    dataframe = pd.read_csv(filepath)
    dataframe["Component"] = dataframe["Component"].replace("Code",
                                                    "Configuration unit")
    dataframe["Component"] = dataframe["Component"].replace("Configuration",
                                                    "IaC program")
    dataframe["Ecosystem"] = dataframe["Ecosystem"]
    if per_ecosystem:
        group_value = 'Ecosystem'
    else:
        group_value = 'Component'
    grouped = dataframe.groupby([group_value, 'Symptom']).size().reset_index(name='Frequency')
    level_counts = dataframe.groupby(group_value).size()
    grouped['Percentage'] = grouped.apply(lambda row: (row['Frequency'] / level_counts[row[group_value]]) * 100, axis=1).map(lambda x: '{:.2f}%'.format(x))
    print(grouped.to_string(index=False))
    return dataframe


def plot_diagram(dataframe, output, per_ecosystem: bool):
    color_pallette = ['#56B4E9', '#009E73']
    if per_ecosystem:
        color_pallette.insert(1, '#CC79A7')
    groupby = "Ecosystem" if per_ecosystem else "Component"
    legend = "Ecosystem" if per_ecosystem else "Component"
    symptom_counts = dataframe.groupby(['Symptom',
                                        groupby]).size().unstack()
    symptom_counts['Total'] = symptom_counts.sum(axis=1)
    symptom_counts_sorted = symptom_counts.sort_values(by='Total',
                                                       ascending=False)
    count = symptom_counts['Total'].sum()
    ax = symptom_counts_sorted.drop(columns='Total').plot(
        kind='barh', width=0.3, stacked=True, color=color_pallette)

    # Annotate total occurrences next to the bars
    for i, (index, row) in enumerate(symptom_counts_sorted.iterrows()):
        total = row['Total']
        ax.text(total, i, f' {int(total)}/{int(count)}', va='center',
                ha='left', size=10)

    # Move the legend inside the plot area in the bottom right corner
    ax.legend(title=legend, loc='lower right', frameon=True)
    plt.xlabel('')
    plt.ylabel('')
    plt.gca().invert_yaxis()  # To display the highest value at the top
    plt.savefig(output, format='pdf', bbox_inches='tight', pad_inches=0)


def main():
    args = get_args()
    dataframe = construct_dataframe(args.data, args.ecosystem)
    # print(dataframe.to_string(index=False))
    if not args.ecosystem:
        plot_diagram(dataframe, args.output, args.ecosystem)


if __name__ == "__main__":
    main()
