#!/usr/bin/env python3

"""
Provides the ability to produce citations for DOI or Github rpositories for
software enumerated as dependencies for a Snakemake workflow. 
"""

from datetime import datetime
import json
import urllib.request
from urllib.parse import urlparse
import re
import sys
from time import sleep, time


def is_url(url: str) -> bool:
    """ Checks if URL is valid. """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_doi_url(doi: str) -> bool:
    """ Checks if provided DOI URL is valid. """
    doi_regex = r"https?://doi\.org/10\.\d{4,9}/[-._;()/:A-Za-z0-9]+" # 99.3% accuracy per Crossref 
    if re.match(doi_regex, doi):
        return True
    else:
        return False
    

def is_github_repo(repo_url: str) -> bool:
    """ Checks if provided URL is valid Github repo. """
    github_regex = r"https?://github\.com/[\w\-]+/[\w\-]+"
    if re.match(github_regex, repo_url):
        return True
    else: 
        return False


def search_for_doi_or_github(url: str) -> str | None: 
    """ Searches page for URL, either DOI or Github repository, for citation.

    Args:
        url (str): page to be searched.

    Returns:
        (str | None): valid citable URL, None if no link is found or HTTPError.
    """
    doi_re = r"(https?://)?(doi\.org/)?(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+[0-9])"
    github_re = r"(https?://github\.com/[\w\-]+/[\w\-]+)"
    try: 
        with urllib.request.urlopen(url) as response:
            data = response.read().decode("utf-8")
            if (doi := re.search(doi_re, data)):
                return "https://doi.org/" + doi.group(3)
            elif (gh := re.search(github_re, data)):
                return gh.group(1)
            else:
                return None
    except urllib.request.HTTPError:
        return None


def search_repositories(dependency: str) -> str | None: 
    """
    Obtains the URL for DOI or Github repository for dependency for citation on 
    PyPI, Bioconda, and Anaconda. 

    Args:
        dependency (str): name of the dependency

    Returns:
        (str | None): URL if located, otherwise None. 
    """
    if url := search_for_doi_or_github(f"https://pypi.org/pypi/{dependency}/json"):
        return url
    elif url := search_for_doi_or_github(f"https://bioconda.github.io/recipes/{dependency}/README.html"):
        return url
    elif url := search_for_doi_or_github(f"https://anaconda.org/conda-forge/{dependency}"):
        return url
    else:
        sys.stderr.write(f"No available links for {dependency}\n")
        return None


def _query_github_api(
    api_request: urllib.request.Request,
    max_retries: int=3,
    max_wait: int=60,
) -> dict | None:
    """
    Returns decoded data from a Github API request with the ability to retry
    when the connection fails or request to retry after a certain period. 

    The protocol for handling is derived from recommendations set by Github at
    https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api?apiVersion=2022-11-28

    Args:
        api_request (urllib.request.Request): Request to Github API URL. To
            reduce the risk of rate limiting, ensure a Github token is
            included in the headers. 
        max_retries (int, optional): Number of times to retry request.
            Default of 3.
        max_wait (int, optional): Maximum wait time for retry in seconds.
            Default of 60 (one minute). 

    Returns:
        (dict | None) Returns the decoded request, or None if maximum number of
            retries is met.
    """
    for nth_try in range(max_retries):
        try:
            with urllib.request.urlopen(api_request) as request:
                return json.loads(request.read().decode("utf-8"))
        except urllib.request.HTTPError as e:
            match e.code:
                case 403 | 429:
                    if 'retry_after' in e.headers:
                         if max_wait < e.headers['retry_after']:
                             return None
                         sleep(e.headers(e.headers['retry_after'] + 1)) # +1 just in case
                    elif e.headers['X-RateLimit-Remaining'] == 0:
                        wait_length = e.headers['X-RateLimit-Reset'] - time()
                        if max_wait < wait_length:
                            return None
                    else:
                        sleep(60 * (nth_try + 1))
                case 404:
                    return None
                case _:
                    continue # idk, retry
    return None


def get_repo_authors(
    repo_url: str,
    token: str=None,
    filter_bot: bool=True,
) -> list[str] | None:
    """
    Uses Github API to retrieve list of authors for a given repository. 

    Args:
        repo_url (str): URL where the repository is stored. 
        token (str, optional): Github API token to increase number of API calls.
            Maxes at 60 API calls/hour without token, up to 5000 with token.
        filter_bot (bool, optional): remove authors ending in '[bot]'. True by
            default. 
    
    Returns:
        (list[str] | None): list of author names or usernames, None if unable
            to retrieve list of authors. 
    """
    repo = re.search(r'https?://github\.com/([\w\-]+/[\w\-]+)', repo_url).group(1)

    if token:
        headers = {"Authorization": f"token {token}",}
    else:
        headers = {}
        
    contrib_req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/contributors",
        headers=headers
    )
    
    authors_api_list = _query_github_api(contrib_req)
    if not authors_api_list:
        return None

    author_names = []
    for author in authors_api_list:
        author_username = author["login"]
        author_request = urllib.request.Request(author["url"], headers=headers)
        author_data = _query_github_api(author_request)
        if author_data:
            author_name = author_data["name"]
            author_names.append(author_name if author_name else author_username)
        else:
            author_names.append(author_username)

    if filter_bot:
        author_names = [author for author in author_names if not author.endswith("[bot]")]
        
    return author_names


def cite_github_repo(repo_url: str, token: str=None) -> str | None:
    """
    Generates citation for Python package using Github repository. 

    Args:
        repo_url (str): url to Github repository.
        token (str, optional): Github token to increase number of API calls.

    Returns:
        (str | None): Bibtex citation for the Python package.
    """
    authors = get_repo_authors(repo_url, token)
    if not authors:
        return None # could consider citing without authors
    
    mch = re.search(r'https?://github\.com/([\w\-]+/([\w\-]+))', repo_url)
    repo_loc = mch.group(1)
    repo_name = mch.group(2)

    if token:
        headers = {"Authorization": f"token {token}",}
    else:
        headers = {}
        
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo_loc}",
        headers=headers
    )
    repo_data = _query_github_api(request)
    if not repo_data:
        return None
    pub_year = repo_data["updated_at"][:4]
        
    return f"""@misc{{{repo_name.lower()}, 
    title = {{{repo_name}}}, 
    author = {{{" and ".join(authors)}}},
    url = {{{repo_url}}},
    date = {{{pub_year}}},
    urldate = {{{datetime.now().strftime("%Y-%m-%d")}}}
}}"""


def get_doi_bibtex(doi_url: str) -> str | None:
    """
    Produces Bibtex citation for given DOI URL.

    Args:
        doi_url (str): DOI for article to be cited. 

    Returns:
        (str | None): Bibtex citation for DOI, None if error. 
    """
    r = urllib.request.Request(doi_url, headers={"Accept": "application/x-bibtex"})
    try:
        with urllib.request.urlopen(r) as response:
            return response.read().decode("utf-8")
    except urllib.request.HTTPError:
        return None


def find_and_cite(url: str) -> str | None:
    link_found = search_for_doi_or_github(url)
    if not link_found:
        return None
    if is_doi_url(link_found):
        return get_doi_bibtex(link_found)
    elif is_github_repo(link_found):
        return cite_github_repo(link_found)
    else:
        return None


def extract_dependencies_from_file(filepath: str) -> list[str]:
    if filepath.lower().endswith(".yaml") or filepath.lower().endswith(".yml"):
        results = extract_dependencies_from_yaml(filepath)
    else: # assume it is a dependency text file
        results = extract_dependencies_from_txt(filepath)
    return results


def extract_dependencies_from_yaml(filepath: str) -> list[str]:
    deps = []
    in_dependencies = False
    dependency_regex = re.compile(r"- ([\w][\w\-\_]+)")
    with open(filepath) as file: 
        for line in file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped == "dependencies:":
                in_dependencies = True
                continue
            if in_dependencies:
                hit = dependency_regex.search(line)
                library = hit.group(1)
                deps.append(library)
    return deps

def extract_dependencies_from_txt(filepath: str) -> list[str]:
    deps = []
    dependency_regex = re.compile(r"^([\w\-\_]+)")
    with open(filepath) as file:
        for line in file:
            hit = dependency_regex.search(line)
            if not hit:
                continue 
            library = hit.group(1)
            deps.append(library)
    return deps
