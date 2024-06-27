import requests
import re
import csv
import json
import time
from datetime import datetime, timezone
import argparse

# Input file path
# input_csv = '../../data/urls/ansible_roles_urls.csv'

# GitHub personal access token



def parse_github_url(url):
    if url.endswith('.git'):
        url = url[:-4]
    # Check if the URL is SSH format
    if url.startswith('git@github.com:'):
        url = url.replace('git@github.com:', 'https://github.com/')
    
    path = url.split('/')
    if len(path)>1:
      owner = path[-2]
      repo = path[-1]
      return owner, repo
    else:
      # print("Error", url)
      return None, None

def get_repo_issues(owner, repo, headers):
    issues = []
    cursor = None  # Used for pagination
    remaining_limit = 5000

    while True:
        # GraphQL query. Using triple quotes for multi-line string
        query = """
        {{
          rateLimit {{
            cost
            remaining
            resetAt
          }}
          repository(owner: "{owner}", name: "{repo}") {{
            issues(first: 100, after: {cursor}, states: CLOSED) {{
              edges {{
                node {{
                  title
                  body
                  url
                  closedAt
                  timelineItems(last: 1, itemTypes: [CLOSED_EVENT]) {{
                    edges {{
                      node {{
                        __typename
                        ... on ClosedEvent {{
                          closer {{
                            __typename
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
              }}
              pageInfo {{
                endCursor
                hasNextPage
              }}
            }}
          }}
        }}
        """.format(owner=owner, repo=repo, cursor=json.dumps(cursor))
        request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        result = request.json()
        # if "errors" in result:
        #   return "Stop", "Stop"
        # Handle rate limits
        rate_limit = result['data']['rateLimit']
        remaining = rate_limit['remaining']  # Remaining limit
        resetAt = rate_limit['resetAt']  # Time when the limit will reset
        if remaining < 1:  # Check if the remaining limit is less than 100
          reset_time_utc = datetime.fromisoformat(resetAt[:-1]).replace(tzinfo=timezone.utc)
          current_time_utc = datetime.now(timezone.utc)
          wait_time = (reset_time_utc - current_time_utc).total_seconds() + 1

          if wait_time > 0:  # If the reset time is in the future, sleep until reset
              print(f"Rate limit low. Waiting for {wait_time} seconds until rate limit reset.")
              time.sleep(wait_time)  # Sleep until the rate limit resets
        # Extract data from response
        if 'data' in result and 'repository' in result['data'] and result['data']['repository'] and 'issues' in result['data']['repository']:
            for edge in result['data']['repository']['issues']['edges']:
                issues.append(edge['node'])
  
            # Check for more pages
            if result['data']['repository']['issues']['pageInfo']['hasNextPage']:
                cursor = result['data']['repository']['issues']['pageInfo']['endCursor']
            else:
                break
        else:
            raise Exception(f"Error fetching issues for {owner}/{repo}: {result.get('errors')}")
    return issues

def contains_code_block(string):
    # Patterns for inline code and code blocks
    patterns = [
        r'```[\s\S]+?```'  # code blocks
    ]
    for pattern in patterns:
        if re.search(pattern, string):
            return True
    return False

def main(input_csv, output_csv, token):
  headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
  }
  processed_urls = set()
  count = 0

  with open(input_csv, mode='r') as infile:
      reader = csv.reader(infile)
      next(reader, None)  # Skip header

      with open(output_csv, mode='w', newline='') as outfile:
          writer = csv.writer(outfile)
          writer.writerow(["Issue URL"])

          for row in reader:
            # Assuming the second column contains the GitHub URL in the input CSV
            if (len(row)) == 2:
              repo_url = row[1]
            else:
              repo_url = row[0]
            if repo_url in processed_urls:
                # print(f"Skipping duplicate repo: {repo_url}")
                continue

            processed_urls.add(repo_url) 
            owner, repo = parse_github_url(repo_url)
            try:
                issues = get_repo_issues(owner, repo, headers)
                if issues:
                    for issue in issues:
                        closed_by = "Unknown"
                        if issue['timelineItems']['edges']:
                            closed_by_type = issue['timelineItems']['edges'][0]['node']['__typename']
                            if closed_by_type == 'ClosedEvent':
                                closer = issue['timelineItems']['edges'][0]['node']['closer']
                                if closer:
                                    closed_by = closer['__typename']
                        # contains_code = contains_code_block(issue['body'])
                        closed_at = issue['closedAt']
                        # if contains_code:
                        #     pprint.pprint(issue)
                        # print(count, issue["url"], closed_by, contains_code)
                        if (closed_by == "PullRequest" or closed_by == "Commit"):
                            count+=1
                            writer.writerow([issue['url']])
            except Exception as e:
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch closed issues from GitHub repositories.')
    parser.add_argument('input_csv', type=str, help='Input CSV file path containing GitHub repository URLs.')
    parser.add_argument('output_csv', type=str, help='Output CSV file path to save the issue URLs.')
    parser.add_argument('gh_token', type=str, help='Your GitHub access token.')


    args = parser.parse_args()
    main(args.input_csv, args.output_csv, args.gh_token)