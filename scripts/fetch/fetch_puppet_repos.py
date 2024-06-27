import requests
import time
import pprint
import json
import csv
import argparse


# Function to fetch repository urls from Puppet Forge
def fetch_puppet_forge_repo_urls():
    # Base URL of the Puppet Forge API
    base_url = 'https://forgeapi.puppet.com/v3/modules'
    # Placeholder for the repositories' URLs
    repo_info = [] 
    # Pagination parameters
    limit = 100  # number of results per request, 100 is currently the maximum
    offset = 0   # offset for pagination, start with 0
    headers = {
        'User-Agent': 'ResearchProject/1.0'
    }
    counter = 0
    while True:
        # Update the request URL with the current offset
        request_url = f"{base_url}?limit={limit}&offset={offset}"
        # Send an HTTP request to the Puppet Forge API
        response = requests.get(request_url, headers=headers)
        
        # Break the loop if the request was not successful
        if response.status_code != 200:
            # print(f"Failed to retrieve data: {response.status_code}")
            break
        
        # Load the response data as JSON
        data = response.json()
        # Extract the repository URLs from the response data
        flag = True
        for module in data['results']:
            try:
                counter +=1
                flag = False
                # Add the repository URL to our list
                # with open('data.json', 'w') as f:
                #     json.dump(module, f, indent=2)
                name = module['current_release']['metadata']['name']
                source_url = None
                if module['issues_url']:
                    if "github.com" in module['issues_url']:
                        source_url = module['issues_url'].split("/issues")[0]
                if not source_url:
                    source_url = module['current_release']['metadata']['source']
                    if source_url == "UNKNOWN":
                        source_url =  module['homepage_url']
                repo_info.append((name, source_url))
            except KeyError:
                # If the 'source' key doesn't exist, skip this module
                # print("Error", name)
                continue
        # if flag:
        #     print(data)
        #     break
        # Check if we have reached the last page of the results
        if data['pagination']["next"] is None:
            break
        else:
            # Update the offset for the next request (paginate)
            offset += limit
            # Respect rate limits and avoid overwhelming the server
            time.sleep(1)  # sleep for 1 second before making a new request
    return repo_info

def main(output):
    repository_info = fetch_puppet_forge_repo_urls()

    # Write the data to a CSV file
    with open(output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(['Name', 'Source URL'])
        # Write the project data
        for info in repository_info:
            writer.writerow(info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch GitHub repositories of Puppet Modules.')
    parser.add_argument('output_csv', type=str, help='Output CSV file path to save the repository URLs.')
    args = parser.parse_args()

    main(args.output_csv)