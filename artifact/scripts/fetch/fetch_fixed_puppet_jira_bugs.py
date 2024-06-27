import requests
from requests.auth import HTTPBasicAuth
import re
import argparse



def has_github_url_in_comments(issue_key):
    jira_url = "https://puppet.atlassian.net"
    headers = {"Accept": "application/json"}
    comments_url = f"{jira_url}/rest/api/3/issue/{issue_key}/comment"
    comments_response = requests.get(comments_url, headers=headers)
    if comments_response.status_code == 200:
        comments_json = comments_response.json()
        
        # Function to recursively search for GitHub URLs in the document structure
        def search_for_github_url(node):
            # Check if this node contains the text with a GitHub URL
            if node.get('type') == 'text' and 'text' in node:
                if re.search(r'https://github\.com/[^\s]+/(commit|pull)/[^\s]+', node['text']):
                    return True
            # Recursively search in nested content
            if 'content' in node:
                for child in node['content']:
                    if search_for_github_url(child):
                        return True
            return False
        
        for comment in comments_json.get('comments', []):
            if search_for_github_url(comment['body']):
                return True
    return False




def main(output):
    # Define your JIRA instance URL, JQL query, API endpoint, authentication details, and headers
    start_at = 0
    max_results = 100
    total_issues_fetched = 0
    jql = "project in (PUP, MODULES)  and type = Bug and status in (Closed, Resolved) ORDER BY created DESC"
    jira_url = "https://puppet.atlassian.net"
    search_api = "/rest/api/3/search"
    headers = {"Accept": "application/json"}
    with open(output, 'w') as file:
        file.write("Issue URL" + '\n')
        while True:
            params = {'jql': jql, 'startAt': start_at, 'maxResults': max_results}
            response = requests.request("GET", jira_url + search_api, headers=headers, params=params)

            if response.status_code == 200:
                response_json = response.json()

                issues = response_json['issues']
                total_issues = response_json['total']

                for issue in issues:
                    issue_key = issue['key']
                    # Check each issue for comments with GitHub URLs
                    if has_github_url_in_comments(issue_key):
                        issue_url = f"{jira_url}/browse/{issue_key}"
                        file.write(issue_url + '\n')
                        total_issues_fetched += 1

                if not issues:
                    break

                start_at += max_results
            else:
                # print(f"Failed to fetch issues: {response.status_code}")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch closed issues from Puppet Modules on Jira.')
    parser.add_argument('output_csv', type=str, help='Output CSV file path to save the issue URLs.')

    args = parser.parse_args()
    main(args.output_csv)