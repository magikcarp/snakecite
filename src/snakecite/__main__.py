#!/usr/bin/env python3

"""

"""

import argparse
import os
import sys

from datetime import datetime
from urllib.request import HTTPError

from . import cite


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

def now_fmtd() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    args = get_args()

    # for url
    if cite.is_url(args.target):
        if cite.is_doi_url(args.target):
            try:
                print(cite.get_doi_bibtex(args.target))
            except HTTPError as e:
                sys.stderr.write(f"[WARN] {now_fmtd()}: {e}\n")
        elif cite.is_github_repo(args.target):
            try:
                print(cite.cite_github_repo(args.target))
            except HTTPError as e:
                sys.stderr.write(f"[WARN] {now_fmtd()}: {e} for {args.target}\n")
            except Exception as e:
                sys.stderr.write(f"[WARN] {now_fmtd()}: {e} for {args.target}\n")

    # for single file
    elif os.path.isfile(args.target):
        deps = cite.extract_dependencies_from_file(args.target)
        for dep in deps:
            try:
                link = cite.search_repositories(dep)
                if not link:
                    sys.stderr.write(f"[WARN] {now_fmtd()}: No available links for {dep}\n")
                    continue
                if cite.is_doi_url(link):
                    print(cite.get_doi_bibtex(cite))
                elif cite.is_github_repo(link):
                    print(cite.cite_github_repo(link))
                else:
                    sys.stderr.write(f"[WARN] {now_fmtd()}: Something went horribly wrong for {dep}\n")
            except HTTPError as e:
                sys.stderr.write(f"[WARN] {now_fmtd()}: {e} for {dep}\n")

    # for env directory 
    elif os.path.isdir(args.target):
        for file in os.listdir(args.target):
            ending = file.lower().split(".")[-1]
            if ending != "yaml" and ending != "yml":
                continue
            deps = cite.extract_dependencies_from_yaml(file)
            for dep in deps:
                try:
                    link = cite.search_repositories(dep)
                    if not link:
                        sys.stderr.write(f"[WARN] {now_fmtd()}: No available links for {dep}\n")
                        continue
                    if cite.is_doi_url(link):
                        print(cite.get_doi_bibtex(cite))
                    elif cite.is_github_repo(link):
                        print(cite.cite_github_repo(link))
                    else:
                        sys.stderr.write(f"[WARN] {now_fmtd()}: Something went horribly wrong for {dep}\n")
                except HTTPError as e:
                    sys.stderr.write(f"[WARN] {now_fmtd()}: {e} for {dep}\n")

    else:
        sys.stderr.write(
            f"[FATAL] {now_fmtd()}: {args.target} is unreachable. Target "
            "may be malformatted URL, a file that does not exist, or a "
            "directory that does not exist."
        )
        exit(1)


if __name__ == "__main__":
    main()
