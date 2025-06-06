# snakecite
This script automatically retrieves the citation information for packages in
a snakemake workflow and saves them in a Bibtex or json file. If a citation
cannot be found, then the Bibtex citation will be generated using the
associated Github repository. 

## About this package
The use of packages and dependencies in large workflows, such as those
incorporated using Snakemake, often go without proper citations of the 
dependent packages. The process of manually citing each tool listed in a
workflow remains laborious, tedious, and potentially error prone, further
disincentivizing the process. To address this, the Snakecite tool 

## Features
- Able to cite DOI or journal URLs 
- Extracts package names from `requirements.txt`, `environment.yaml` or
directories of yaml files from Snakemake workflows. 
- Retrieves DOI or Github repo if available on PyPI, Bioconda, or Anaconda.
- Uses author information on Github repository if unable to locate the DOI.
- "All batteries included"--only uses the standard Python library. 

## Installation
For the most up-to-date version, use pipx to install the Github repository.
```
git clone https://github.com/magikcarp/snakecite
cd snakecite
pipx install . snakecite
```

## Usage
### Installed
The following methods assume snakecite has been installed using pipx or an
equivalent tool. 

To cite a single paper DOI:
```
snakecite https://doi.org/10.1093/bioinformatics/bts480
```

To cite a `requirements.txt`, such as one generated by `pip freeze`:
```
snakecite requirements.txt
```

### Cloned
If the Snakecite repository is instead simply cloned to the desired system
and not installed using pipx or another method, the library can instead be
called using relative or absolute paths.

It is strongly encouraged to use a Github API token to prevent rate limiting 
when generating citations. This can be achieved following [these instructions](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). 
Your API token can be employed using the `--github-token` flag. For example:
```
snakecite environment.yaml --github-token TOKEN
```

To append snakecite output to a bibliography file using shell:
```
snakecite requirements.txt >> bibliography.bib
```

## Future additions
- [ ] Create command-line argument to augment the repositories searched
- [ ] Provide ability to cite non-DOI journal URLs
- [ ] Implement global number of retries and max wait time for spotty network
services
- [ ] Increase depth of search in Github repositories
- [ ] Create citation using `meta.yaml` when present in Github repository
- [ ] Allow for citation of specific package version
- [ ] Refactor functions to not log errors on their own and instead place
the onus of logging on the caller
- [ ] Upload Snakecite to PyPi for installation using pip
- [ ] Improve test coverage

## Contributing
If you'd like to contribute to this project, please open an issue or submit
a pull request.
