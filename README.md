# When you Infrastructure is a Buggy Program: Understanding Faults in Infrastructure as Code Ecosystems

This is the artifact for the conditionally accepted paper submitted to OOPSLA'24 titled:
"When you Infrastructure is a Buggy Program:
Understanding Faults in Infrastructure as Code Ecosystems".


# Table of Contents

- [When you Infrastructure is a Buggy Program: Understanding Faults in Infrastructure as Code Ecosystems](#when-you-infrastructure-is-a-buggy-program-understanding-faults-in-infrastructure-as-code-ecosystems)
- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Requirements](#requirements)
- [Bug Collection Dataset](#bug-collection-dataset)
- [Selected Bugs](#selected-bugs)
- [Getting Started](#getting-started)
  - [Setup](#setup)
  - [Option1: Ubuntu/Debian Installation](#option1-ubuntudebian-installation)
  - [Option2: Docker Image Installation (Recommended)](#option2-docker-image-installation-recommended)
- [Important Note](#important-note)
  - [Downloading Bug \& Fixes from Sources (Optional)](#downloading-bug--fixes-from-sources-optional)
    - [Collecting Puppet Module Repositories](#collecting-puppet-module-repositories)
    - [Collecting Chef Cookbook Repositories](#collecting-chef-cookbook-repositories)
    - [Collecting Ansible Collection Repositories](#collecting-ansible-collection-repositories)
    - [Collecting Ansible Role Repositories](#collecting-ansible-role-repositories)
    - [Collecting Bugs from GitHub Repositories](#collecting-bugs-from-github-repositories)
    - [Collecting Puppet Bugs from Jira](#collecting-puppet-bugs-from-jira)
  - [Quantitative Analysis (Section 3.2) (Optional)](#quantitative-analysis-section-32-optional)
- [Step-by-Step Instructions](#step-by-step-instructions)
  - [Collecting Bugs \& Fixes (Section 3.1)](#collecting-bugs--fixes-section-31)
  - [RQ1: Symptoms (Section 4.1)](#rq1-symptoms-section-41)
  - [RQ2: Root Causes (Section 4.2)](#rq2-root-causes-section-42)
  - [RQ3: System State Requirements and Input Characteristics (Section 4.3)](#rq3-system-state-requirements-and-input-characteristics-section-43)
    - [Operating System Requirements](#operating-system-requirements)
    - [State Reachability](#state-reachability)
  - [RQ4: Bug Fixes (Section 4.4)](#rq4-bug-fixes-section-44)

# Overview

The purpose of this artifact is
(1) to replicate the results
produced in our paper,
and (2) to record our dataset
and the proposed classification.
In particular,
the structure of the artifact is organized as follows:

* `scripts/`: This directory contains the scripts necessary to
replicate the findings, figures, and tables introduced in our study.

* `scripts/fetch/`:  This directory contains the scripts required
to assemble the dataset of IaC bugs
as outlined in Section 3.1 of our study
(that is, this directory includes the code for our repository collection gathering
and bug collection stages).
* `data/`: This is the "pre-baked" dataset of the 360 IaC bugs
  under study.
* `figures/`: A directory which is going to store the produced paper figures.
* `requirements.txt`: A textual file declaring the required PyPI libraries to run our analysis


# Requirements


* An installation of Python version **3.8+**.
* (Optionally) A GitHub access token (see [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)) for interacting with the GitHub API. You will need this access token only if you decide to execute the qualitative analysis of our artifact.

# Bug Collection Dataset

The directory  `data/collections` hosts the dataset in the bug collection phase.
It is organized as follows:
* `data/collections/repositories/`: This subdirectory houses the data obtained after the repository collection (RP) step. Specifically:
  * `ansible_roles.csv`: Lists the GitHub URLs of the collected Ansible roles.
  * `ansible_urls.csv`: Provides module names alongside their corresponding GitHub URLs of the collected Ansible modules.
  * `chef_urls.csv`: Details the names of Chef cookbooks and their respective GitHub URLs.
  * `puppet_urls.csv`: Includes names and GitHub URLs of the obtained Puppet module repositories.
* `data/collections/bugs/`: This directory holds CVS files containing GitHub or Jira URLs of the bugs identified after applying the bug collection (BG) step. Specifically:
  * `ansible_bugs.csv`: Contains URLs to GitHub issues of Ansible modules.
  * `ansible_builtin_bugs.csv`: Contains URLs to GitHub issues of Ansible built-in modules.
  * `ansible_role_bugs.csv`: Contains URLs to GitHub issues of Ansible roles.
  * `chef_bugs.csv`: Documents bugs found in Chef cookbooks, including GitHub issue URLs for each identified bug.
  * `puppet_bugs.csv`: Contains Puppet module bugs, with links to their respective GitHub issues.
  * `puppet_jira_bugs.csv`: Specifically lists Puppet bugs tracked through JIRA, with issue URLs.

# Selected Bugs

Now, we provide details regarding the 360 IaC bugs
studied in our paper.
These details can be found in the `data/` directory,
which has the following structure:

* `data/bugs.csv`: This document contains all 360 bugs examined in our study
                    and their categorization.
                    Each bug row has the following fields:
    * `Issue URL`: The url of the issue report.     
    * `Fix URL`: The url of the GitHub commit or Pull Request of the fix. 
    * `Ecosystem`: The IaC ecosystem of the bug.
    * `Symptom`: The bug's symptom.
    * `Root Cause`: The bug's symptom.
    * `Operating System/Platform`:  `Independent` if the bug is reproducible across multiple supported Operating Systems
    In cases the bug is reproduced only on one OS, this OS is included.
    * `OS Sensitivity`: Indicates whether the bug is OS-sensitive (for details, see Section 4.3.1 of the paper)
    Its value has the following options:
    `Insensitive` if the bug is os-insensitive. In case the bug is os sensitive, the value has the format of:
     `operating_system_name(True)` in case the bug is version sensitive, or  `operating_system_name(Fasle)` otherwise,
     where the `operating_system_name` is the name of the os to which the bug is reproducible.
    * `System State`: The system state reachability of the bug. (e.g. `State agnostic`, `Unmanaged state` or `Managed state`)
    * `System State Observations`: In case the bug is state-dependent, this attribute includes the specific system state requirements.
    Multiple values are separated by semicolons.
    * `Test Input`: The test input characteristics of the bug. Multiple values are separated by semicolons.
    * `Component`: The component in which the bug is located. (e.g. `Code` for Configuration Units  or `Configuration` for `IaC Programs`)


* `data/quantitative_metrics.csv`: This CSV file encapsulates the data retrieved from GitHub API for the qualitative analysis conducted for RQ4, incorporating the following fields for each bug analyzed:
  * `Issue URL`: Direct link to the issue report.
  * `Fix URL`: URL of the GitHub commit or Pull Request that resolved the issue.
  * `Ecosystem`: The Infrastructure as Code ecosystem to which the bug belongs, such as Ansible, Puppet, or Chef.
  * `Created At`: The creation date of the issue.
  * `Closed At`: The date when the issue was closed.
  * `Config Unit Files Count`: The number of configuration unit files affected by the fix.
  * `Config Unit Lines Added`: The number of lines added to configuration unit files as part of the fix.
  * `Config Unit Lines Removed`: The number of lines removed from configuration unit files due to the fix.
  * `IAC Program Unit Files Count`: The count of IaC program unit files impacted by the fix.
  * `IAC Program Unit Lines Added`: The number of lines added to IaC program unit files as part of the fix.
  * `IAC Program Unit Lines Removed`: The number of lines removed from IaC program unit files during the fix.
  * `Test Unit Files Count`: The count of test unit files that were involved in the fix.
  * `Test Unit Lines Added`: The amount of code (in lines) added to test units as part of the fix.
  * `Test Unit Lines Removed`: The number of lines deleted from test units during the fix.
  * `Template Unit Files Count`: The number of template unit files affected by the fix.
  * `Template Unit Lines Added`: The count of lines added to template unit files as part of the fix.
  * `Template Unit Lines Removed`: The number of lines removed from template unit files during the fix.



# Getting Started


This section includes documentation and instruction in order to (1) setup the necessary environment in order to run our scripts, (2)  re-collecting  IaC bugs from the issue trackers of the projects of each ecosystem, namely Ansible, Chef and Puppet and (3) run the wualitative analysis of the sampled 360 bugs to produce the metrics sued to aanswer RQ4.

First, obtain the artifact by cloning the repository and navigating to the artifact's root directory:

```bash
   git clone https://github.com/gdrosos/iac-bug-study-artifact ~/iac-bug-study-artifact
   cd ~/iac-bug-study-artifact
```

## Setup

To replicate the environment needed to run our  scripts, you can choose between setting up a virtual environment directly on Ubuntu/Debian or using Docker, which is recommended.


## Option1: Ubuntu/Debian Installation

You need to install some packages through  `apt`  to run the
experiments of this artifact.
First, install git, python, pip and python3-venv:

```bash
sudo apt update
sudo apt install git python3 python3-pip python3-venv
```

**Important Note**
For convenience, throughout the documentation and scripts, we use the standard python command instead of python3. To ensure compatibility, please create a symbolic link to point python to python3 by running the following command:
```bash
ln -s /usr/bin/python3 /usr/bin/python
```

You also need to install some Python packages.
In a Python `virtualenv` run the following:
```bash
python -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
```

## Option2: Docker Image Installation (Recommended)

Use this option if you prefer a containerized environment or are not using an Ubuntu/Debian operating system.
We provide a `Dockerfile` to build an image that contains:

* The necessary `apt` packages (e.g., `git`, `python3`, `pip`) for running
  our experiments.
* The necessary Python packages (declared in the `requirements.txt` file).
* A user named `user` with `sudo` privileges.

To build the Docker image named `iac-bug-study-artifact` from source,
run the following command (estimated running time: ~5 minutes):

```bash
docker build -t iac-bug-study-artifact .
```
Then, you can run  the docker container by executing the following command:

```bash
docker run -it --rm \
    -v $(pwd)/scripts:/home/user/scripts \
    -v $(pwd)/data:/home/user/data \
    -v $(pwd)/figures:/home/user/figures \
    iac-bug-study-artifact /bin/bash
```
After executing the command, you will be able to enter the home directory
(i.e., `/home/user`). This directory contains:
1) the scripts for reproducing the results of the paper (see `scripts/`),
2)  the data of our bug study (see `data/`),
3) a dedicated directory for storing the generated figures (see `figures/`),


This setup uses volume mounting (-v) to ensure that scripts, data, and figures directories are persisted outside of the container for ease of access and modification on your local machine (e.g. they will not be lost upon the container's exit).

# Important Note
In order to run some parts of our methodology, you will need a Github access token (see [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)).
Once you obtain it,
please assign it to a shell variable named `GH_TOKEN`.

```bash
export GH_TOKEN=<your Github access token>
```

## Downloading Bug & Fixes from Sources (Optional)

In this section we provide instructions on collecting the IaC bugs and their fixes which correspond to Section 3.1 of our paper.

**NOTE #1**: This step requires approximatelly 24 hours. For this reason, we already provide you with the "pre-baked" data of the selected bugs used in our study, along with the proposed categorization (see the directory `data/`). However, if you still want to re-fetch the bugs from the corresponding sources and create the initial bug dataset on your own, please continue reading this section. Otherwise, you can go directly to the next Section ([Quantitative Analysis](#quantitative-analysis-section-32-optional)).

**NOTE #2**: The generated dataset may contain more bugs than those described in the paper because new bugs might have been fixed since our initial data collection.


**NOTE #3**: You will also need a GitHub access token (see [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)).
Once you obtain it,
please assign it to a shell variable named `GH_TOKEN`.

```bash
export GH_TOKEN=<your GitHub access token>
```

To run the Data Collection, and store the collected data in a new directory (e.g. in `data/collection_new`), execute the following script (Estimated run time: 20-24 hours):


```bash
sh scripts/fetch/fetch_bugs.sh $GH_TOKEN data/collection_new
```

This shell script is a wrapper that invokes the following scripts:


```
scripts/fetch/fetch_puppet_repos.py
scripts/fetch/fetch_chef_repos.py
scripts/fetch/fetch_ansible_repos.py
scripts/fetch/fetch_ansible_roles.py
scripts/fetch/fetch_issues.py
scripts/fetch/fetch_fixed_puppet_jira_bugs.py
```

The first four scripts retrieve the URLs of GitHub repositories containing the bugs, while the last two obtain the bugs.
Below, we provide additional details regarding each script.

### Collecting Puppet Module Repositories

```
python scripts/fetch/fetch_puppet_repos.py data/collection_new/puppet_urls.csv
```

This script queries the Puppet Forge REST-API ([https://forgeapi.puppet.com/v3/modules](https://forgeapi.puppet.com/v3/modules)) to fetch Puppet modules with their corresponding GitHub URLs and stores them in a CSV file named `data/collection_new/puppet_urls.csv`.

### Collecting Chef Cookbook Repositories

```
python scripts/fetch/fetch_chef_repos.py data/collection_new/chef_urls.csv
```

This script queries the Supermarket Chef REST-API ([https://supermarket.chef.io/api/v1/cookbooks/](https://supermarket.chef.io/api/v1/cookbooks/)) to fetch Chef cookbooks with their corresponding repository URL and stores them in a CSV file named `data/collection_new/chef_urls.csv`.


### Collecting Ansible Collection Repositories


```
python scripts/fetch/fetch_ansible_repos.py data/collection_new/ansible_urls.csv
```
This script queries the Ansible Galaxy REST-API ([https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/](https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/)) to fetch Ansible collections with their corresponding repository URL and stores them in a CSV file named `data/collection_new/ansible_urls.csv`.


### Collecting Ansible Role Repositories


```
python scripts/fetch/fetch_ansible_roles.py data/collection_new/ansible_roles_urls.csv
```
This script queries the Ansible Galaxy REST-API ([https://galaxy.ansible.com/api/v1/roles/](https://galaxy.ansible.com/api/v1/roles/)) to fetch Ansible collections with their corresponding repository url and stores them in a CSV file named `data/collection_new/ansible_roles_urls.csv`.

### Collecting Bugs from GitHub Repositories

Having obtained the CSV files with the GitHub repositories, we use the same approach for each ecosystem.
Specifically, we run the `scripts/fetch/fetch_issues.py` script which reads a CSV file with the GitHub repositories and uses the GitHub API (specifically the  GraphQL database [https://api.github.com/graphql](https://api.github.com/graphql)) to find all closed issues containing a closing Pull Request or a Commit indicating a fix. Then, we store the URL of each found Issue in a CSV file.
The script for each ecosystem is invoked as follows:


```
python scripts/fetch/fetch_issues.py data/collection_new/repositories/chef_urls.csv \
data/collection_new/bugs/chef_bugs.csv  $GH_TOKEN

python scripts/fetch/fetch_issues.py data/collection_new/repositories/ansible_urls.csv \
data/collection_new/bugs/ansible_bugs.csv $GH_TOKEN

python scripts/fetch/fetch_issues.py data/collection_new/repositories/ansible_roles_urls.csv \
data/collection_newR/bugs/ansible_role_bugs.csv $GH_TOKEN

python scripts/fetch/fetch_issues.py data/collection_new/repositories/puppet_urls.csv \
data/collection_new/bugs/puppet_bugs.csv  $GH_TOKEN
```


### Collecting Puppet Bugs from Jira

```
python scripts/fetch/fetch_fixed_puppet_jira_bugs.py $BASE_DIR/bugs/puppet_jira_bugs.csv
```

This script fetches all closed issues in the Puppet Jira Issue Tracker([https://puppet.atlassian.net](https://puppet.atlassian.net)) using the query:
```
project in (PUP, MODULES) 
and type = Bug and status in (Closed, Resolved)
ORDER BY created DESC
```
It then filters out issues that do not have at least one comment containing a URL of a GitHub Commit or Pull Request indicating a potential fix, and stores the filtered issues in a CSV file named `data/collection_new/bugs/puppet_jira_bugs.csv`.

## Quantitative Analysis (Section 3.2) (Optional)

Optionally, you can run the quantitative analysis of the 360 sampled bugs to produce the `data/quantitative_metrics.csv` which is used to answer RQ4 (See Section [Selected Bugs](#selected-bugs) for file contents).
Simply run (Estimated Run Time: ~7 minutes, can increase depending on current GitHub API Rate Limit of given user):

```bash
python scripts/quantitative_analysis.py data/bugs.csv $GH_TOKEN \
 --output data/quantitative_metrics.csv
```
Initially, the script retrieves the issue creation and resolution dates for each bug via the GitHub API and, for some Puppet issues, through the Jira REST API. Then, for each fix URL, it sends a GitHub API request to obtain metadata about the number and size in Lines of Code (LoC) of the files affected by the fix.


# Step-by-Step Instructions

In the following section, we provide instructions
for reproducing the results
presented in the paper using the "pre-baked" data coming from the `data/` directory.



 ## Collecting Bugs & Fixes (Section 3.1)

Run this script to produce the descriptive statistics of our bug collection and analysis,
and more specifically the data shown in Table 2.

```bash
python scripts/descriptives.py data
```

The above script prints the following:

```
Ecosystem   Total Repositories  Total Issues   Oldest                   Most Recent              Config. Unit Bugs IaC Program Bugs  
Puppet      7471                6750           06 Aug 2013              02 Feb 2023              42                78                
Ansible     35236               16916          19 Sep 2014              03 Oct 2023              94                26                
Chef        2818                1141           23 Aug 2011              09 Mar 2023              76                44              
```

## RQ1: Symptoms (Section 4.1)

In the first research question,
we compute the distribution of bug symptoms.
To do so, please run:

```bash
python scripts/rq1.py data/bugs.csv --output figures/symptoms_comp.pdf
```

The above script produces
Figure 4, which is stored in the`symptoms_comp.pdf` file in the `figures/` directory.
The script also prints the distribution of symptoms for each IaC Component in a tabular format.
Specifically, it prints
the following:

```
         Component                        Symptom  Frequency Percentage
Configuration unit External configuration failure         76     35.85%
Configuration unit              Idempotency issue         18      8.49%
Configuration unit         Internal error (crash)         63     29.72%
Configuration unit               Misconfiguration         37     17.45%
Configuration unit              Misleading report         13      6.13%
Configuration unit              Performance issue          5      2.36%
       IaC program External configuration failure         56     37.84%
       IaC program              Idempotency issue          5      3.38%
       IaC program         Internal error (crash)         26     17.57%
       IaC program               Misconfiguration         61     41.22%
```

Optionally, to also observe the distribution of symptoms per Ecosystem, run:

```bash
python scripts/rq1.py data/bugs.csv --ecosystem
```

The above script prints the distribution of symptoms for each Ecosystem in a tabular format.
Specifically, it prints:
```
Ecosystem                        Symptom  Frequency Percentage
  Ansible External configuration failure         46     38.33%
  Ansible              Idempotency issue          6      5.00%
  Ansible         Internal error (crash)         35     29.17%
  Ansible               Misconfiguration         23     19.17%
  Ansible              Misleading report          7      5.83%
  Ansible              Performance issue          3      2.50%
     Chef External configuration failure         45     37.50%
     Chef              Idempotency issue          8      6.67%
     Chef         Internal error (crash)         31     25.83%
     Chef               Misconfiguration         33     27.50%
     Chef              Misleading report          3      2.50%
   Puppet External configuration failure         41     34.17%
   Puppet              Idempotency issue          9      7.50%
   Puppet         Internal error (crash)         23     19.17%
   Puppet               Misconfiguration         42     35.00%
   Puppet              Misleading report          3      2.50%
   Puppet              Performance issue          2      1.67%
```

## RQ2: Root Causes (Section 4.2)

For the second research question, we compute the per Ecosystem distribution
of causes for bugs found in Configuration Units.
The below script produces Figures 6a and 6b.
As in the first research question,
our script also reports the distributions
in a tabular format.

To produce Figure 6a, simply run:
```bash
 python scripts/rq2.py data/bugs.csv --component conf --output figures/root_causes_conf.pdf
```

The above command produces the figure `figures/root_causes_conf.pdf` (Figure 6a)
and prints the following table in the standard output:

```
Ecosystem     Root Cause Category  Frequency Percentage
  Ansible        API-related bugs          7      7.45%
  Ansible      Compatibility bugs         16     17.02%
  Ansible     Input handling bugs         17     18.09%
  Ansible         Resilience bugs          6      6.38%
  Ansible System interaction bugs         26     27.66%
  Ansible     State handling bugs         22     23.40%
     Chef        API-related bugs          5      6.58%
     Chef      Compatibility bugs         17     22.37%
     Chef     Input handling bugs          9     11.84%
     Chef         Resilience bugs          6      7.89%
     Chef System interaction bugs         22     28.95%
     Chef     State handling bugs         17     22.37%
   Puppet        API-related bugs          3      7.14%
   Puppet      Compatibility bugs          9     21.43%
   Puppet     Input handling bugs          4      9.52%
   Puppet         Resilience bugs          6     14.29%
   Puppet System interaction bugs         10     23.81%
   Puppet     State handling bugs         10     23.81%
```

In the same manner, to produce Figure 7b run the following command:

```bash
python scripts/rq2.py data/bugs.csv --component iac --output figures/root_causes_iac.pdf
```

The above command produces the figures `figures/root_causes_iac.pdf` (Figure 6b)
and prints the following table in the standard output:

```
Ecosystem              Root Cause Category  Frequency Percentage
  Ansible               Compatibility bugs          9     34.62%
  Ansible                      Invalid DSL          2      7.69%
  Ansible                  Resilience bugs          1      3.85%
  Ansible          System interaction bugs         12     46.15%
  Ansible              State handling bugs          1      3.85%
  Ansible                    Template bugs          1      3.85%
     Chef Bugs related to hardcoded values          7     15.91%
     Chef               Compatibility bugs         15     34.09%
     Chef                  Dependency bugs          2      4.55%
     Chef              Input handling bugs          1      2.27%
     Chef                  Resilience bugs          1      2.27%
     Chef          System interaction bugs          8     18.18%
     Chef              State handling bugs          2      4.55%
     Chef                    Template bugs          8     18.18%
   Puppet                 API-related bugs          4      5.13%
   Puppet Bugs related to hardcoded values         10     12.82%
   Puppet               Compatibility bugs         17     21.79%
   Puppet                  Dependency bugs         12     15.38%
   Puppet              Input handling bugs          9     11.54%
   Puppet                      Invalid DSL          3      3.85%
   Puppet                  Resilience bugs          2      2.56%
   Puppet          System interaction bugs          9     11.54%
   Puppet                    Template bugs         12     15.38%
```

## RQ3: System State Requirements and Input Characteristics (Section 4.3)
### Operating System Requirements
To reproduce the numbers presented in Figure 9, simply run:
```bash
python scripts/rq3.py data/bugs.csv --os
```

The above script will produce the following table:

```
Category                          Version Agnostic                  Version Dependent   Total               
----------------------------------------------------------------------------------------------------
Debian Family                     16                                15                  31                  
RedHat Family                     13                                14                  27                  
Other Linux                       3                                 0                   3                   
----------------------------------------------------------------------------------------------------
Total Linux (Subtotal)            32                                29                  61                  
Windows                           16                                2                   18                  
Other OS                          4                                 2                   6                   
----------------------------------------------------------------------------------------------------
Total OS Sensitive (Subtotal)     52                                33                  85                  
Single OS Support                 37                                0                   37                  
Multiple OS Support               238                               0                   238                 
----------------------------------------------------------------------------------------------------
Grand Total                       327                               33                  360                 
```

### State Reachability

To produce the first diagram of Figure 10, simply run:
```bash
python scripts/rq3.py data/bugs.csv --output figures/state_components.pdf
```

The above command produces the figure `figures/state_components.pdf` (Figure 10)
and prints the following table in the standard output:

```
         Component    System state  Frequency Percentage
Configuration unit   Managed state         45     21.23%
Configuration unit  State agnostic         72     33.96%
Configuration unit Unmanaged state         95     44.81%
       IaC program   Managed state         24     16.22%
       IaC program  State agnostic        100     67.57%
       IaC program Unmanaged state         24     16.22%
```

To produce the second Plot of Figure 10, which represents the system state requirements of state dependent bugs,
run:

```bash
python scripts/rq3.py data/bugs.csv --output figures/system_state.pdf --not_managed
```

The above command produces the figure `figures/system_state.pdf` (Figure 10b)
and prints the following table in the standard output:

```
Distribution of system state requirements of state dependent bugs:
----------------------------------------
Requirements  Frequency
     Service         79
        File         60
       Other         51
     Package         33
 IaC Runtime         19
 Remote host          9
```

Moreover, to produce Table 3, which depicts the five most frequent input types appearing in the bug-triggering test cases, simply run:

```bash
 python scripts/rq3.py data/bugs.csv --test_inputs
```

The above command prints the data of Table 3 (Section 4.3.3) as follows:

```
Data type                          Occ (%)
-----------------------------------------
Network (IP, port, firewall)        28%
File system (path, attrs)           19%
Package (name, version)             15%
Authentication (token, login info)  10%
Command (shell)                     4%
```

Finally, to reproduce the distribution numbers of state reachability across ecosystems, (Section 4.3.4), simply run:


```bash
python scripts/rq3.py data/bugs.csv --ecosystems
```

The above command prints the following table in the standard output:

```
Ecosystem    System state  Frequency Percentage
  Ansible   Managed state         15     12.50%
  Ansible  State agnostic         42     35.00%
  Ansible Unmanaged state         63     52.50%
     Chef   Managed state         18     15.00%
     Chef  State agnostic         75     62.50%
     Chef Unmanaged state         27     22.50%
   Puppet   Managed state         36     30.00%
   Puppet  State agnostic         55     45.83%
   Puppet Unmanaged state         29     24.17%
```

## RQ4: Bug Fixes (Section 4.4)

In the fourth research question, we study the duration and the fixes of the bugs. We produce Figures 11, 12 and 13.  We also report the mean, median, standard deviation, max, and min of the following metrics:

* Cumulative distribution of lines of code in a fix per Component (Figure 11a)
* Cumulative distribution of files in a fix per Component (Figure 11b)
* Cumulative distribution of test files in a fix per Ecosystem (Figure 12a)
* Cumulative distribution of test files in a fix per Component (Figure 12b)


To produce the aforementioned figures and metrics, please run:

```bash
python scripts/rq4.py data/bugs.csv data/quantitative_metrics.csv --directory figures
```

The aforementioned command takes as input 3 arguments. The first argument is the filepath of the csv file storing the qualitative results of the bug study. The second argument is the filepath of the csv file storing the quantitative results for RQ4. Finally, the last argument is the directory in which the figures are stored.
Specifically, after the execution of the script, the following files will be created in the target directory:

* `lines.pdf` (Figure 11a)
* `files.pdf` (Figure 11b)
* `test_files.pdf` (Figure 12a)
* `test_files_component.pdf` (Figure 12b)

In addition, the script also prints the following tables:
```
         Number of Lines of Code (LoC) in a Fix per Component
======================================================================
                          Mean    Median        SD       Min       Max
----------------------------------------------------------------------
Configuration unit       31.99      8.00    144.97      0.00   1964.00
IaC program              38.64      7.00    242.27      0.00   2904.00
All                      34.72      8.00    190.78      0.00   2904.00
----------------------------------------------------------------------

         Number of Source Files in a Fix per Component
======================================================================
                          Mean    Median        SD       Min       Max
----------------------------------------------------------------------
Configuration unit        1.36      1.00      1.00      0.00     10.00
IaC program               1.95      1.00      2.40      0.00     17.00
All                       1.60      1.00      1.74      0.00     17.00
----------------------------------------------------------------------

         Number of Test Files in a Fix per Ecosystem
======================================================================
                          Mean    Median        SD       Min       Max
----------------------------------------------------------------------
Ansible                   1.18      0.00      2.16      0.00     11.00
Puppet                    0.98      1.00      1.74      0.00     12.00
Chef                      0.86      0.00      1.55      0.00      8.00
All                       1.01      0.00      1.84      0.00     12.00
----------------------------------------------------------------------

         Number of Test Files in a Fix per Component
======================================================================
                          Mean    Median        SD       Min       Max
----------------------------------------------------------------------
Configuration unit        1.10      0.00      1.92      0.00     11.00
IaC program               0.87      0.00      1.71      0.00     12.00
All                       1.01      0.00      1.84      0.00     12.00
----------------------------------------------------------------------
```
