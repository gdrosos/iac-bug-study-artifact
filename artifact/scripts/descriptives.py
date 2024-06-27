import os
import pandas as pd
import sys


def count_lines_in_csv(filepath):
    """Count the lines in a CSV file, ignoring the header."""
    with open(filepath, 'r') as file:
        return sum(1 for line in file) - 1 

def read_and_process_rq4_csv(filepath):
    """Read quantitative_metrics.csv and process it for statistics."""
    df = pd.read_csv(filepath, parse_dates=['Created At', 'Closed At'])
    # Group by Ecosystem
    grouped = df.groupby('Ecosystem')
    # Oldest and Most Recent Issues
    oldest_issue = grouped['Created At'].min()
    most_recent_issue = grouped['Created At'].max()
    return oldest_issue, most_recent_issue

def process_bugs_csv(filepath):
    """Process bugs.csv for counts of Configuration Unit and IaC Program bugs per Ecosystem."""
    df = pd.read_csv(filepath)
    grouped = df.groupby(['Ecosystem', 'Component']).size().unstack(fill_value=0)
    return grouped

def process_directory(directory):
    ecosystem_patterns = {
        'Puppet': ['puppet_bugs.csv', 'puppet_jira_issues.csv', 'puppet_urls.csv'],
        'Ansible': ['ansible_bugs.csv', 'ansible_builtin_bugs.csv', 'ansible_role_bugs.csv', 'ansible_extra_repo.csv', 'ansible_roles_urls.csv', 'ansible_urls.csv'],
        'Chef': ['chef_bugs.csv', 'chef_urls.csv']
    }

    results = {eco: {'bugs': 0, 'repositories': 0} for eco in ecosystem_patterns}

    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if file == 'quantitative_metrics.csv':
                oldest_issue, most_recent_issue = read_and_process_rq4_csv(filepath)
            elif file == 'bugs.csv':
                    bugs_counts_per_ecosystem = process_bugs_csv(filepath)
            else:
                for eco, patterns in ecosystem_patterns.items():
                    if file in patterns:
                        if 'urls.csv' in file or 'repo.csv' in file:
                            results[eco]['repositories'] += count_lines_in_csv(os.path.join(root, file))
                        else:
                            results[eco]['bugs'] += count_lines_in_csv(os.path.join(root, file))

    print(f"{'Ecosystem':<12}{'Total Repositories':<20}{'Total Issues':<15}{'Oldest':<25}{'Most Recent':<25}{'Config. Unit Bugs':<18}{'IaC Program Bugs':<18}")
    for eco in results:
        print(f"{eco:<12}{results[eco]['repositories']:<20}{results[eco]['bugs']:<15}"
              f"{oldest_issue[eco].strftime('%d %b %Y') if eco in oldest_issue else 'N/A':<25}"
              f"{most_recent_issue[eco].strftime('%d %b %Y') if eco in most_recent_issue else 'N/A':<25}"
              f"{bugs_counts_per_ecosystem.loc[eco, 'Code'] if eco in bugs_counts_per_ecosystem.index else 0:<18}"
              f"{bugs_counts_per_ecosystem.loc[eco, 'Configuration'] if eco in bugs_counts_per_ecosystem.index else 0:<18}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python descriptives.py <directory>")
        sys.exit(1)
    directory = sys.argv[1]
    process_directory(directory)