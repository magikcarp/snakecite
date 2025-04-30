#!/usr/bin/env python3

"""

To run tests, use the following command from the parent `snakecite` directory:
```
$ python -m tests.test_cite
```
"""

import unittest
from unittest.mock import patch

from src.snakecite import cite

class TestURLs(unittest.TestCase):
    # testing cite.is_url
    def test_is_url_with_google(self):
        self.assertTrue(cite.is_url("https://www.google.com"))
    
    def test_is_url_with_github(self):
        self.assertTrue(cite.is_url("https://github.com/magikcarp/snakecite"))
    
    def test_is_url_with_doi(self):
        self.assertTrue(cite.is_url("https://doi.org/10.1093/bioinformatics/bts480"))

    def test_is_url_with_pypi(self):
        self.assertTrue(cite.is_url("https://pypi.org/"))

    def test_is_url_google_no_http(self):
        self.assertFalse(cite.is_url("www.google.com"))

    def test_is_url_int(self):
        self.assertFalse(cite.is_url(45))

    def test_is_url_float(self):
        self.assertFalse(cite.is_url(4.5))

    def test_is_url_float_as_str(self):
        self.assertFalse(cite.is_url("4.5"))

    # testing cite.is_doi_url
    def test_is_doi_url_success(self):
        self.assertTrue(cite.is_doi_url("https://doi.org/10.1093/bioinformatics/bts480"))

    def test_is_doi_url_success_http(self):
        self.assertTrue(cite.is_doi_url("http://doi.org/10.1093/bioinformatics/bts480"))

    def test_is_doi_url_no_http(self):
        self.assertFalse(cite.is_doi_url("doi.org/10.1093/bioinformatics/bts480"))

    def test_is_doi_url_just_DOI_number(self):
        self.assertFalse(cite.is_doi_url("10.1093/bioinformatics/bts480"))

    def test_is_doi_url_google(self):
        self.assertFalse(cite.is_doi_url("https://www.google.com"))

    def test_is_doi_url_int(self):
        self.assertFalse(cite.is_doi_url(45))

    def test_is_doi_url_float(self):
        self.assertFalse(cite.is_doi_url(4.5))

    def test_is_doi_url_float_as_str(self):
        self.assertFalse(cite.is_doi_url("4.5"))

    # testing cite.is_github_repo
    def test_is_github_repo_success(self):
        self.assertTrue(cite.is_github_repo("https://github.com/magikcarp/snakecite"))

    def test_is_github_repo_success_http(self):
        self.assertTrue(cite.is_github_repo("http://github.com/magikcarp/snakecite"))

    def test_is_github_repo_fail_no_http(self):
        self.assertFalse(cite.is_github_repo("github.com/magikcarp/snakecite"))

    def test_is_github_repo_google(self):
        self.assertFalse(cite.is_github_repo("https://www.google.com"))

    def test_is_github_repo_int(self):
        self.assertFalse(cite.is_github_repo(45))

    def test_is_github_repo_float(self):
        self.assertFalse(cite.is_github_repo(4.5))

    def test_is_github_repo_float_as_str(self):
        self.assertFalse(cite.is_github_repo("4.5"))

    

"""
class TestGithubApi(unittest.TestCase): # TODO implement more tests
    @patch('requests.get')
    def test__query_github_api_not_empty(self, mock_get):
        url = "https://github.com/magikcarp/snakecite"
        mock_get.return_value.status_code = 200
    @patch('requests.get')
    def test__query_github_api_fail_on_404(self, mock_get):
        pass

    @patch('requests.get')
    def test__query_github_api_fail_on_retry_after(self, mock_get):
        pass

    @patch('requests.get')
    def test__query_github_api_fail_on_rate_limiting(self, mock_get):
        pass
"""


class TestDoiApi(unittest.TestCase):
    pass 


class TestParsingFiles(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
