import requests
import re
import csv
import argparse
import time


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate rq3 figures')
    parser.add_argument("data", help="CSV with bugs.")
    parser.add_argument("gh_token", help="Github Access Token")
    parser.add_argument(
            "--output",
            default="quantitative_metrics.csv",
            help="Filename to save the qualitative metrics.")
    return parser.parse_args()



def get_jira_date(url):
    """
    Fetches the creation and resolution dates for a JIRA issue given its URL.

    Parameters:
    - url: The URL of the JIRA issue.

    Returns:
    A tuple containing the creation date and resolution date (or 'Not Resolved' if not applicable).
    """
    issue_key = url.split('/')[-1]

    # JIRA REST API endpoint for issue details
    domain = 'puppet.atlassian.net'  # Replace with your JIRA domain
    api_url = f'https://{domain}/rest/api/3/issue/{issue_key}'

    # Replace with your JIRA username and API token
    # username = 'your_username'
    # api_token = 'your_api_token'
    # auth = HTTPBasicAuth(username, api_token)

    headers = {
       "Accept": "application/json"
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        issue_data = response.json()
        created_date = issue_data['fields']['created'].split('T')[0]  # Extracting just the date part
        # Closed date might be in a different field or might not be set if the issue is not closed
        resolution_date = issue_data['fields'].get('resolutiondate')
        if resolution_date:
            resolution_date = resolution_date.split('T')[0]  # Extracting just the date part
        else:
            resolution_date = 'Not Resolved'
        return created_date, resolution_date
    else:
        print(f"Failed to fetch issue details. Status code: {response.status_code}")
        return None, None


def save_to_csv(issue_details, output):
    """
    Saves the collected issue details to a CSV file.

    Parameters:
    - issue_details: A dictionary containing issue URLs as keys and their details as values.
    """
    headers = ['Issue URL', 'Fix URL', 'Ecosystem', 'Created At', 'Closed At',
               'Config Unit Files Count', 'Config Unit Lines Added', 'Config Unit Lines Removed',
               'IAC Program Unit Files Count', 'IAC Program Unit Lines Added', 'IAC Program Unit Lines Removed',
               'Test Unit Files Count', 'Test Unit Lines Added', 'Test Unit Lines Removed',
               'Template Unit Files Count', 'Template Unit Lines Added', 'Template Unit Lines Removed']

    with open(output, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for issue, details in issue_details.items():
            row = {
                'Issue URL': issue,
                'Fix URL': details['fix_url'],
                'Ecosystem': details['ecosystem'],
                'Created At': details['created_at'].split('T')[0],
                'Closed At': details['closed_at'].split('T')[0],
                'Config Unit Files Count': details['config_units']['files'],
                'Config Unit Lines Added': details['config_units']['lines_added'],
                'Config Unit Lines Removed': details['config_units']['lines_removed'],
                'IAC Program Unit Files Count': details['iac_program_units']['files'],
                'IAC Program Unit Lines Added': details['iac_program_units']['lines_added'],
                'IAC Program Unit Lines Removed': details['iac_program_units']['lines_removed'],
                'Test Unit Files Count': details['test_units']['files'],
                'Test Unit Lines Added': details['test_units']['lines_added'],
                'Test Unit Lines Removed': details['test_units']['lines_removed'],
                'Template Unit Files Count': details['template_units']['files'],
                'Template Unit Lines Added': details['template_units']['lines_added'],
                'Template Unit Lines Removed': details['template_units']['lines_removed'],
            }
            writer.writerow(row)


def get_category(ecosystem, file_path):
    """
    Determines the category of a file based on its path and the ecosystem.
    Parameters:
    - ecosystem (str): The name of the ecosystem (Ansible, Puppet, Chef).
    - file_path (str): The path of the file within the repository.
    Returns:
    - str: The category of the file ('config_units', 'iac_program_units', 'test_units', 'template_units', or None).
    """
    if ecosystem == "Ansible":
        return get_ansible_category(file_path)
    elif ecosystem == "Puppet":
        return get_puppet_category(file_path)
    elif ecosystem ==  "Chef":
        return get_chef_category(file_path)
    else:
        print("Error", file_path)


def get_ansible_category(file_path):
    """
    Classifies Ansible-related files into categories based on their file paths.
    Parameters:
    - file_path (str): The path of the file within the Ansible repository.
    Returns:
    - str: The category of the file ('config_units', 'iac_program_units', 'test_units', 'template_units', or None).
    """
    if any(x in file_path for x in ['test/', "tests/", 'molecule']):
        category = 'test_units'
    elif any(substring in file_path for substring in ["changelog", "doc/", "docs/"]) or file_path.endswith('.md') or file_path.endswith('.bugfix') or file_path.endswith('.rst'):
        category = None
    elif "modules" in file_path or  file_path.endswith('.py'):
        category = 'config_units'
    elif "templates/" in file_path:
        category = 'template_units'
    elif file_path.endswith('.yaml') or file_path.endswith('.yml') or "roles" in file_path or "files/"in file_path:
        category = 'iac_program_units'
    else:
        print(f"Unclassified file: {file_path}")
        category = None
    return category

def get_puppet_category(file_path):
    """
    Classifies Puppet-related files into categories based on their file paths.
    Parameters:
    - file_path (str): The path of the file within the Puppet repository.
    Returns:
    - str: The category of the file ('config_units', 'iac_program_units', 'test_units', 'template_units', or None).
    """
    if any(x in file_path for x in ['spec/']):
        category = 'test_units'
    elif any(x in file_path for x in ["provider", "lib/", "tasks/"]):
        category = 'config_units'
    elif "templates/" in file_path:
        category = 'template_units'
    elif any(x in file_path for x in ['manifests/', "types/", "data/"]):
        category = 'iac_program_units'
    elif any(substring in file_path for substring in ["changelog", "doc", "github", "Guardfile", "Modulefile", "Gemfile", "metadata.json",".fixtures.yml", ".gitignore"]) or file_path.endswith('.md') or file_path.endswith('.bugfix') or file_path.endswith('.rst') or "/" not in file_path:
        category = None
    else:
        print(f"Unclassified file: {file_path}")
        category = None
    return category


def get_chef_category(file_path):
    """
    Classifies Chef-related files into categories based on their file paths.
    Parameters:
    - file_path (str): The path of the file within the Chef repository.
    Returns:
    - str: The category of the file ('config_units', 'iac_program_units', 'test_units', 'template_units', or None).
    """
    if any(x in file_path for x in ['test', 'spec/']) and not file_path.startswith("roles"):
        category = 'test_units'
    elif any(x in file_path for x in ['resources/', 'libraries/', "providers/"]):
        category = 'config_units'
    elif "templates/" in file_path:
        category = 'template_units'
    elif any(x in file_path for x in ['recipes/', 'attributes/', "metadata.rb", "files/"]):
        category = 'iac_program_units'
    elif any(substring in file_path for substring in ["changelog", "doc", "github", "deployments/"]) or file_path.endswith('.md') or file_path.endswith('.bugfix') or file_path.endswith('.rst') or file_path.endswith(".yml") or "/" not in file_path:
        category = None
    else:
        print(f"Unclassified file: {file_path}")
        category = None
    return category

def get_commit_details(commit_url, ecosystem, headers):
    """
    Fetches details for a given commit URL within a specific ecosystem.
    Parameters:
    - commit_url (str): The URL of the commit.
    - ecosystem (str): The ecosystem to which the commit belongs.
    Returns:
    - dict: A dictionary containing details of the commit categorized by unit type.
    """
    match = re.search(r"github\.com/(.+)/(.+)/commit/([0-9a-f]{40})", commit_url)
    if not match:
        return "Invalid commit URL", commit_url

    owner, repo, commit_sha = match.groups()

    # Fetch commit details
    commit_details_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
    commit_response = requests.get(commit_details_url, headers=headers)
    commit_data = commit_response.json()

    # Check if the commit data has the 'files' key
    if 'files' not in commit_data:
        return None, None, None  # Or handle error as needed

    files_data = commit_data['files']
    details = {
        'config_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},
        'iac_program_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},
        'test_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},
        'template_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},

    }
    for file in files_data:
        file_path = file['filename']
        additions = file['additions']
        deletions = file['deletions']

        category = get_category(ecosystem, file_path)
        if category:
            # Update counters
            details[category]['files'] += 1
            details[category]['lines_added'] += additions
            details[category]['lines_removed'] += deletions

    return details

def get_pr_details(pr_url, ecosystem, headers):
    """
    Fetches details for a given pull request URL within a specific ecosystem.
    Parameters:
    - pr_url (str): The URL of the pull request.
    - ecosystem (str): The ecosystem to which the pull request belongs.
    Returns:
    - dict: A dictionary containing details of the pull request categorized by unit type.
    """
    match = re.search(r"github\.com/(.+)/(.+)/pull/(\d+)", pr_url)
    if not match:
        return "Invalid PR URL", pr_url

    owner, repo, pull_number = match.groups()

    # Fetch files touched by the PR
    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
    files_response = requests.get(files_url, headers=headers)
    files_data = files_response.json()
    details = {
        'config_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},
        'iac_program_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},
        'test_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},
        'template_units': {'files': 0, 'lines_added': 0, 'lines_removed': 0},

    }
    for file in files_data:
        file_path = file['filename']
        additions = file['additions']
        deletions = file['deletions']
        category = get_category(ecosystem, file_path)
        if category:
            # Update counters
            details[category]['files'] += 1
            details[category]['lines_added'] += additions
            details[category]['lines_removed'] += deletions

    return details


def parse_url(url):
    """
    Parses a GitHub issue URL to extract the owner, repository, and issue number.
    Parameters:
    - url (str): The URL of the GitHub issue.
    Returns:
    - tuple: A tuple containing the owner, repository, and issue number (as integer), or (None, None, None) if parsing fails.
    """
    match = re.search(r"github\.com/(.+)/(.+)/issues/(\d+)", url)
    if match:
        return match.group(1), match.group(2), int(match.group(3))
    return None, None, None


def get_urls_from_csv(filepath):
    """
    Reads a CSV file and extracts issue URLs and pull request URLs.

    Parameters:
    - filepath (str): The path to the CSV file.

    Returns:
    - list of tuples: A list where each tuple contains an issue URL and the corresponding pull request URL.
    """
    urls = []
    with open(filepath, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            issue_url = row['Issue URL']
            pr_url = row['Fix URL']
            ecosystem = row["Ecosystem"]
            urls.append((issue_url, pr_url, ecosystem))
    return urls


def get_closure_info(owner, repo, issue_number, headers):
    """
    Fetches closure information for a GitHub issue given the owner, repository, and issue number.
    Parameters:
    - owner (str): The owner of the repository.
    - repo (str): The name of the repository.
    - issue_number (int): The number of the issue.
    Returns:
    - tuple: A tuple containing the type of closure (PR/Commit), closure URL, creation date, and closure date.
    """
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
        createdAt
        closedAt
          timelineItems(last: 1, itemTypes: [CLOSED_EVENT]) {
            nodes {
              __typename
              ... on ClosedEvent {
                closer {
                  __typename
                  ... on PullRequest {
                    url
                  }
                  ... on Commit {
                    oid
                    url
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {
        'owner': owner,
        'repo': repo,
        'number': issue_number,
    }

    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    data = response.json()
    if "errors" not in data:
        closure_info = data['data']['repository']['issue']['timelineItems']['nodes'][0] if data['data']['repository']['issue']['timelineItems']['nodes'] else None

        if closure_info and closure_info['__typename'] == 'ClosedEvent':
            if closure_info["closer"] and "url" in closure_info["closer"]:
                closer_type = closure_info['closer']['__typename']
                closure_url = closure_info['closer']['url']
                created_at = data['data']['repository']['issue']['createdAt']
                closed_at = data['data']['repository']['issue']['closedAt']
                return closer_type, closure_url, created_at, closed_at
            # else:
            #     print("Error", closure_info, owner, repo, issue_number)
    else:
        rate_limit_reset = int(response.headers.get('X-RateLimit-Reset'))
        sleep_time = max(rate_limit_reset - int(time.time()), 0) + 10
        print(f"GitHub API rate limit exceeded. Waiting for {int(sleep_time/60)} minutes...")
        time.sleep(sleep_time)
        return get_closure_info(owner, repo, issue_number, headers)
    return None, None, None, None


def main():
    args = get_args()
    gh_headers = {
    'Authorization': f'Bearer {args.gh_token}',
    'Content-Type': 'application/json'
    }
    issue_details = {} 
    urls = get_urls_from_csv(args.data)
    for issue_url, fix_url, ecosystem in urls:
        # # Special case handling for a specific issue URL.
        if issue_url == "https://github.com/ansible/ansible/issues/70589": 
            issue_details[issue_url] = {
                'fix_url': fix_url,
                "ecosystem": ecosystem,
                "created_at": "2020-11-13T10:36:22Z",
                "closed_at": "2020-11-21T10:36:22Z",
                }
            continue
        # elif url =="https://github.com/sous-chefs/docker/issues/158":
        #     issue_details[url] = {
        #         'fix_url': "https://github.com/sous-chefs/docker/pull/160",
        #         "ecosystem": ecosystem,
        #         "created_at": "2014-5-23T10:36:22Z",
        #         "closed_at": "2014-7-24T10:36:22Z",
        #         }
        #     # Skip further processing for this URL.
        #     continue
        # if url == "https://github.com/sous-chefs/golang/issues/54": 
        #     issue_details[url] = {
        #         'fix_url': "https://github.com/sous-chefs/golang/pull/55",
        #         "ecosystem": ecosystem,
        #         "created_at": "2016-06-20T10:36:22Z",
        #         "closed_at": "2016-06-21T10:36:22Z",
        #         }
        #     continue
        # Extract the owner, repo, and issue number from the GitHub issue URL.
        owner, repo, issue_number = parse_url(issue_url)
        # If a valid issue number is found, fetch closure information for the issue.
        if issue_number:
            closer_type, closure_url, created_at, closed_at = get_closure_info(owner, repo, issue_number, gh_headers)
            issue_details[issue_url] = {
                'fix_url': fix_url,
                "ecosystem": ecosystem,
                "created_at": created_at,
                "closed_at": closed_at
            }

        # Handle JIRA URLs separately.
        elif issue_url.startswith("https://puppet.atlassian.net/"):
            # Fetch creation and closure dates using the JIRA API.
            created_at, closed_at = get_jira_date(issue_url)
            issue_details[issue_url] = {
                    'fix_url': fix_url,
                    "ecosystem": ecosystem,
                    "created_at": created_at,
                    "closed_at": closed_at,
                }

        else: 
            print(f"Could not parse URL: {issue_url}")
    # Update the issue details with information fetched from PRs or commits.
    for issue in issue_details:
        if "/pull/" in issue_details[issue]["fix_url"]:
            issue_details[issue].update(get_pr_details(issue_details[issue]["fix_url"], issue_details[issue]["ecosystem"], gh_headers))
        else: 
            issue_details[issue].update(get_commit_details(issue_details[issue]["fix_url"],issue_details[issue]["ecosystem"], gh_headers))
    save_to_csv(issue_details, args.output)


if __name__ == "__main__":
    main()
