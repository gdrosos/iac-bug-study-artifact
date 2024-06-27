import requests
import time
import os
import csv
import argparse


API_URL = 'https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/'


def get_collections(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        # print(f'Failed to retrieve collections: {response.status_code}')
        return None

def get_repo_url(url):
    base_url = 'https://galaxy.ansible.com'
    page_url = f'{base_url}{url}' 
    response = requests.get(page_url)
    if response.status_code == 200:
        json_obj = response.json()
        repo_url = json_obj["metadata"]['repository']
        return repo_url
    else:
        # print(f'Failed to retrieve collections: {response.status_code}')
        return None

    return github_link.get_attribute('href') if github_link else None

def main(output):
    next_page_url = API_URL + '?limit=100'
    all_collections = []
    final_urls = []

    while next_page_url:
        result = get_collections(next_page_url)
        if result is not None:
            all_collections.extend(result['data'])
            next_page_url = result['links']['next']  # Get the next page URL
            # print("Fetched", len(all_collections), "Ansible collections so far...")
            if next_page_url:
                next_page_url = 'https://galaxy.ansible.com' + next_page_url
            time.sleep(2)  # Sleep to avoid hitting rate limit
        else:
            break

    # At this point, all_collections contains all the collections
    count = 0
    for collection in all_collections:
        count +=1
        namespace = collection['namespace']
        name = collection['name']
        version_url = collection["highest_version"]["href"]
        repo_url = get_repo_url(version_url)
        if repo_url:
            if "github" in repo_url:
                final_urls.append((namespace+"/"+name, repo_url))
        if count % 30 == 0:
            time.sleep(1)

    with open(output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(['Name', 'Source URL'])
        # Write the project data
        for info in final_urls:
            writer.writerow(info)


if __name__ == "__main__":
        
    parser = argparse.ArgumentParser(description='Fetch GitHub repositories of Ansible Collections.')
    parser.add_argument('output_csv', type=str, help='Output CSV file path to save the repository URLs.')


    args = parser.parse_args()
    main(args.output