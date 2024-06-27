import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


plt.style.use('ggplot')
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (5, 4)
plt.rcParams['axes.labelsize'] = 17
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'


root_cause_mapping = {
    'Incorrect command construction/execution': 'System interaction bugs',
    'Missing system operations': 'System interaction bugs',
    'Unsound system operations': 'System interaction bugs',
    'Incorrect identification of system state deviations': 'State handling bugs',
    'Incorrect conversion/serialization of system state': 'State handling bugs',
    'Incorrect identification of current system state': 'State handling bugs',
    'Template bugs': 'Template bugs',
    'Incorrect conversion/serialization of user input': 'Input handling bugs',
    'Incorrect validation of user input': 'Input handling bugs',

    'API inconsistency bugs': 'API-related bugs',
    'Incorrect data type': 'API-related bugs',

    'Compatibility issue with the OS/platform': 'Compatibility bugs',
    'Compatibility issue with dependency': 'Compatibility bugs',
    'Resilience bugs': 'Resilience bugs',

    'Bugs related to hardcoded values': 'Bugs related to hardcoded values',
    'Dependency bugs': 'Dependency bugs',
    'Invalid DSL': 'Invalid DSL',

}
pd.set_option('display.max_colwidth', None)


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate root cause figure')
    parser.add_argument("data", help="CSV with bugs.")
    parser.add_argument(
            "--output",
            default="root_causes.pdf",
            help="Filename to save the symptoms figure.")
    parser.add_argument(
            "--component",
            choices=["conf", "iac"],
            default="conf",
            help="Component associated with the bug")

    return parser.parse_args()


def construct_dataframe(filepath, component):
    dataframe = pd.read_csv(filepath)
    dataframe["Component"] = dataframe["Component"].replace("Code",
                                                    "Configuration unit")
    dataframe["Component"] = dataframe["Component"].replace("Configuration",
                                                    "IaC program")
    dataframe["Ecosystem"] = dataframe["Ecosystem"]
    dataframe['Root Cause Category'] = dataframe['Root cause'].map(root_cause_mapping)

    if component == "conf":
        filtered = dataframe[dataframe["Component"]=="Configuration unit"]
    else:
       filtered = dataframe[dataframe["Component"]=="IaC program"]

    # Calculate the total counts for each 'Ecosystem' in the filtered DataFrame
    level_counts = filtered['Ecosystem'].value_counts()
    # Then perform your grouping on the filtered DataFrame
    grouped = filtered.groupby(["Ecosystem", 'Root Cause Category']).size().reset_index(name='Frequency')

    # Correctly calculate the percentage using the 'level_counts' for each 'Ecosystem'
    grouped['Percentage'] = grouped.apply(lambda row: (row['Frequency'] / level_counts[row["Ecosystem"]]) * 100, axis=1).map(lambda x: '{:.2f}%'.format(x))
    # Printing the DataFrame
    print(grouped.to_string(index=False))
    return dataframe


def plot_diagram(dataframe, component, output):
    _map = {
        "conf": "Configuration unit",
        "iac": "IaC program"
    }
    component = _map[component]
    df_filtered = dataframe[dataframe['Component'] == component]
    rc_counts = df_filtered.groupby(['Root Cause Category',
                                     'Ecosystem']).size().unstack()
    rc_counts['Total'] = rc_counts.sum(axis=1)
    rc_counts_sorted = rc_counts.sort_values(by='Total', ascending=False)
    # Unstack to get 'Ecosystem' as columns
    count = rc_counts['Total'].sum()
    ax = rc_counts_sorted.drop(columns='Total').plot(
        kind='barh', width=0.3, stacked=True,
        color=['#56B4E9', '#009E73', '#CC79A7'])

    # Annotate total occurrences next to the bars
    for i, (index, row) in enumerate(rc_counts_sorted.iterrows()):
        total = row['Total']
        ax.text(total, i, f' {int(total)}/{int(count)}', va='center',
                ha='left', size=10)

    # Move the legend inside the plot area in the bottom right corner
    ax.legend(title='Ecosystem', loc='lower right', frameon=True)

    plt.xlabel('')
    plt.ylabel('')
    # plt.xlim([0, 65])
    if component == "Configuration unit":
        plt.xlim([0, 65])
    else:
        plt.xlim([0, 45])
    plt.gca().invert_yaxis()
    plt.savefig(output, format='pdf', bbox_inches='tight', pad_inches=0)


def main():
    args = get_args()
    dataframe = construct_dataframe(args.data, args.component)
    plot_diagram(dataframe, args.component, args.output)


if __name__ == "__main__":
    main()
