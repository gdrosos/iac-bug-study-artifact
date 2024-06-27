import requests
import time
import csv
import argparse

def get_all_cookbooks(start, items):
    cookbooks = []
    base_url = "https://supermarket.chef.io/api/v1/cookbooks"
    params = {
        'start': start,
        'items': items,
    }
    cookbooks = []

    while True:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            for cookbook in data['items']:
                cookbooks.append(cookbook['cookbook'])
            if len(data['items']) < items:
                break  # We've reached the end of the cookbooks list
            params['start'] += items  # Prepare the 'start' for the next batch of cookbooks
        else:
            # print(f"Failed to retrieve cookbooks: {response.status_code}")
            break  # Exit the loop if there's an error
        time.sleep(1)  # Pause to avoid hitting rate limits

    return cookbooks

def get_cookbook_source_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['source_url']
    else:
        return None

def main(output):
    cookbooks = get_all_cookbooks(0, 100)
    count = 0
    repo_urls = []
    for cookbook in cookbooks:
        count+=1
        source_url = get_cookbook_source_url(cookbook)
        name = cookbook.split("https://supermarket.chef.io/api/v1/cookbooks/")[1]
        if source_url:
            if "github" in source_url:
                repo_urls.append((name, source_url))
        if count % 100 == 0:
            time.sleep(1)
    
    with open(output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(['Name', 'Source URL'])
        # Write the project data
        for info in repo_urls:
            writer.writerow(info)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch GitHub repositories of Chef Cookbooks.')
    parser.add_argument('output_csv', type=str, help='Output CSV file path to save the repository URLs.')
    args = parser.parse_args()

    main(args.output_csv)
