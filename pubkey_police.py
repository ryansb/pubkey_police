#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import requests
from pprint import pprint
from pygithub3 import Github
import re

REPOS = []
GH = Github(login=raw_input("Username: "), password=raw_input("Password: "))

TITLE = "You seem to have committed a private key to this repo."
BODY_TEMPLATE = ("This is an automatic message from the pubkey police. See"
                 " my code at http://github.com/ryansb/pubkey_police ."
                 " The file {title} at the url http://github.com{fileurl} seems"
                 " to be an rsa"
                 " private key. I'd recommend taking this out of your repo, as"
                 " it is the equivalent of committing a password. You can do"
                 " this by following the instructions Here:"
                 " https://help.github.com/articles/remove-sensitive-data")

class OutOfResultsException(Exception):
    pass

def you_accidentally():
    for repo in REPOS:
        data = {
            'title': TITLE,
            'body': BODY_TEMPLATE.format(title=repo[1], fileurl=repo[2]),
            'assignee': repo[0].split('/')[0]
        }
        print "Would make this issue: ", data['asignee'], repo[0].split('/')[1]
        print "But we're being nice and this is a practice run."
        #GH.issues.create(data, user=data['asignee'], repo=repo[0].split('/')[1])


def find_repos(html):
    # returns a list of tuples of results
    # tuples formatted as (repo_slug, file_title, file_url)
    soup = BeautifulSoup(html)
    results = []
    if not len(soup.findAll('div', {'class': re.compile("^.*code-list-item.*$")})):
        raise OutOfResultsException("Out of results")
    for res in soup.findAll('div', {'class': re.compile("^.*code-list-item.*$")}):
        results.append((res.findAll('a')[1].attrs[0][1][1:],  #repo_slug
                        dict(res.findAll('a')[2].attrs)['title'],  #file_title
                        dict(res.findAll('a')[2].attrs)['href']  #file_url
                        ))
    return filter(lambda r: not bool(re.match('^.*(gpg$|pub$)', r[1])), results)


if __name__ == "__main__":
    p = {'q': "path:.ssh/id_rsa",
            "type":"Code",
            "ref":"advsearch",
            "l":""}
    html_responses = []
    for i in range(1,300):
        if i > 1:
            p['p'] = i
        resp = requests.get("https://github.com/search", params=p)
        try:
            for r in find_repos(resp.content):
                REPOS.append(r)
                print r[0]
        except OutOfResultsException, e:
            print e.message
            break

    print "Messaging users"
    you_accidentally()
