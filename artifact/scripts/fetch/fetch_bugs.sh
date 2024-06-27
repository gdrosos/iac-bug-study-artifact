# #!/bin/bash


# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <github_token> <base_directory>"
    echo "Make sure you have properly set up your GitHub token environment variable."
    exit 1
fi

# Arguments
GITHUB_TOKEN=$1
BASE_DIR=$2

# Check if the base directory exists, if not create necessary directories
if [ ! -d "$BASE_DIR/repositories" ]; then
    mkdir -p "$BASE_DIR/repositories"
fi
if [ ! -d "$BASE_DIR/bugs" ]; then
    mkdir -p "$BASE_DIR/bugs"
fi

# # Run Python scripts to fetch repositories and bugs
# echo "Fetching repositories of Ansible collections..."
# python scripts/fetch/fetch_ansible_repos.py $BASE_DIR/repositories/ansible_urls.csv
# echo "Fetching repositories of Ansible roles..."
# python scripts/fetch/fetch_ansible_roles.py $BASE_DIR/repositories/ansible_roles_urls.csv
# echo "Fetching repositories of Puppet modules..."
# python scripts/fetch/fetch_puppet_repos.py $BASE_DIR/repositories/puppet_urls.csv
# echo "Fetching repositories of Chef cookbooks..."
# python scripts/fetch/fetch_chef_repos.py $BASE_DIR/repositories/chef_urls.csv
echo "Fetching Puppet bugs from Jira..."
python scripts/fetch/fetch_fixed_puppet_jira_bugs.py $BASE_DIR/bugs/puppet_jira_bugs.csv

# # Append Ansible repository URL to the CSV file
# echo "ansible/ansible,https://github.com/ansible/ansible" >> $BASE_DIR/repositories/ansible_urls.csv

echo "Fetching urls of Chef bugs..."
python scripts/fetch/fetch_issues.py $BASE_DIR/repositories/chef_urls.csv $BASE_DIR/bugs/chef_bugs.csv  $GH_TOKEN
echo "Fetching urls of Ansible bugs..."
python scripts/fetch/fetch_issues.py $BASE_DIR/repositories/ansible_urls.csv $BASE_DIR/bugs/ansible_bugs.csv  $GH_TOKEN
python scripts/fetch/fetch_issues.py $BASE_DIR/repositories/ansible_roles_urls.csv $BASE_DIR/bugs/ansible_role_bugs.csv $GH_TOKEN
# echo "Fetching urls of Puppet bugs..."
python scripts/fetch/fetch_issues.py $BASE_DIR/repositories/puppet_urls.csv $BASE_DIR/bugs/puppet_bugs.csv  $GH_TOKEN

