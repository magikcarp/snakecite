#!/usr/bin/env python3

"""

"""

import argparse
from datetime import datetime
import os
import sys
import time

import snakecite.cite as cite


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        help="file or directory listing dependencies",
    )
    parser.add_argument(
        "-g",
        "--github-token",
        help="Github API token", 
        default=None,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    if cite.is_url(args.target):
        if cite.is_doi_url(args.target):
            if citation := cite.get_doi_bibtex(args.target):
                print(citation)
            else:
                sys.stderr.write(f"[WARNING] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Error requesting {args.target}\n")
        elif cite.is_github_repo(args.target):
            print(cite.cite_github_repo(args.target))
        else:
            sys.stderr.write(f"[WARNING] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Unable to cite {args.target}")
        
    elif os.path.isfile(args.target):
        deps = cite.extract_dependencies_from_file(args.target)
        for dep in deps:
            link = cite.search_repositories(dep)
            if cite.is_doi_url(link):
                citation = cite.get_doi_bibtex(link)
                print(citation) if citation else None
            elif cite.is_github_repo(link):
                citation = cite.cite_github_repo(link, token=args.github_token)
                print(citation) if citation else None
            else:
                sys.stderr.write(f"[WARNING] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: No citable source found for {dep}\n")

    elif os.path.isdir(args.target):
        for file in os.listdir():
            ending = file.lower().split(".")[-1]
            if ending == "yaml" or ending == "yml":
                deps = cite.extract_dependencies_from_yaml(file)
                for dep in deps:
                    time.sleep(1)
                    link = cite.search_repositories(dep)
                    if cite.is_doi_url(link):
                        print(cite.get_doi_bibtex(link))
                    elif cite.is_github_repo(link):
                        print(cite.cite_github_repo(link))
                    else:
                        sys.stderr.write(f"[WARNING] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: No citable source found for {dep}\n")

    else:
        print(
            f"[WARNING] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: {args.target} is unreachable. Target may be malformatted"
            " URL, a file that does not exist, or a directory that does not"
            " exist."
        )
        exit(1)


if __name__ == "__main__":
    main()
