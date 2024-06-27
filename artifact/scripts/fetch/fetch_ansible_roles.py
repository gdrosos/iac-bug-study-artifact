import requests
import pprint
import csv
import argparse

API_URL = 'https://galaxy.ansible.com/api/v1/roles/'

def get_roles(url):
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

def main(output):
    next_page_url = API_URL
    all_roles = []

    while next_page_url:
        result = get_roles(next_page_url)
        if result is not None:
            for entry in result['results']:
                all_roles.append("https://github.com/"+entry["github_user"]+"/"+entry["github_repo"])
                # print("Fetched", len(all_roles), "roles so far...")
        if "next" in result:
            next_page_url = result['next']  # Get the next page URL
        else:
            break

    with open(output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(['Name'])
        # Write the project data
        for info in all_roles:
            writer.writerow([info])

    # driver.quit()  # Don't forget to quit the driver!


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch GitHub repositories of Ansible Roles.')
    parser.add_argument('output_csv', type=str, help='Output CSV file path to save the repository URLs.')
    args = parser.parse_args()

    main(args.output