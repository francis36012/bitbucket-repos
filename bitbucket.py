import urllib.request
import requests
import json
import argparse


apiendpoint = "https://bitbucket.org/api/2.0/repositories/"
requestheader = {"content-type": "application/json; charset=utf-8"}

# Default scm for a new repository
scm_default = "git"

# Default visibility of a new repository
vis_default = "false"

action_help = "The action to be performed.\n\tcreate create new repository\n\tdelete delete repository\n\tlist list repositories"
clparser = argparse.ArgumentParser()
clparser.add_argument("-a", "--action", help=action_help)
clparser.add_argument("-u", "--username", help="Username")
clparser.add_argument("-p", "--password", help="Password")
clparser.add_argument("-n", "--name", help="Repository name")
clparser.add_argument("-d", "--description", help="Repository description")
clparser.add_argument("-P", "--visibility", help="Visibility of repository. P for public, X for private")
clparser.add_argument("-s", "--repo-slug", help="Repsitory slug, used in URL")
clparser.add_argument("-S", "--scm", help="SCM")
arguments = None

def main():
    if arguments.action == 'create':
        create_repo()
    elif arguments.action == 'delete':
        delete_repo()
    elif arguments.action == 'list':
        list_repos()
    else:
        invalid_action()

def create_repo():
    user = arguments.username
    password = arguments.password
    name = arguments.name
    slug = arguments.repo_slug
    desc = arguments.description
    visi = arguments.visibility
    scma = arguments.scm

    if not user:
        print("Error: The create option requires a username to be provided")
        return
    elif not password:
        print("Error: The create option requires a password to be provided")
        return
    elif not name:
        print("Error: The create option requires a repository name to be provided")
        return

    reponame = '"name":"' + name + '"'
    reposlug = '"repo_slug":"' + name + '"'
    description = '"description":""'
    visibility = '"is_private":"false"'
    scm = '"scm":"' + scm_default + '"'

    if desc:
        description = '"description":"' + desc + '"'
    if visi:
        if visi == "X":
            visibility = '"is_private":"true"'
    if slug:
        reposlug = '"repo_slug":"' + slug + '"'
    if scma:
        scm = '"scm":"' + scma + '"'

    if slug:
        apiurl = apiendpoint + user + '/' + slug
    else:
        apiurl = apiendpoint + user + '/' + name


    reqdata = '{' + reponame + ',' + reposlug + ',' + description + ',' + visibility + ',' + scm + '}'
    auth_token = requests.auth.HTTPBasicAuth(arguments.username, arguments.password)
    response = requests.post(apiurl, data=reqdata, headers=requestheader, auth=auth_token)

    if response.status_code >= 200 and response.status_code < 300:
        print("Repository has been created at: https://www.bitbucket.org/" + user + "/" + slug)
    else:
        if len(response.text) > 0:
            data = json.loads(response.text)
            repos = data["error"]
            print("{0:<15s}{1:<s}".format("Error Message:", str(repos["message"])))
        print("{0:<15s}{1:<d}".format("Error code:", response.status_code))

def delete_repo():
    user = arguments.username
    password = arguments.password
    slug = arguments.repo_slug

    if not user:
        print("Error: The delete option requires a username to be provided")
        return
    elif not password:
        print("Error: The delete option requires a password to be provided")
        return
    elif not slug:
        print("Error: The delete option requires a repository slug to be provided")
        return

    apiurl = apiendpoint + user + '/' + slug
    auth_token = requests.auth.HTTPBasicAuth(arguments.username, arguments.password)
    response = requests.delete(apiurl, headers=requestheader, auth=auth_token)

    if response.status_code >= 200 and response.status_code < 300:
        print("Repository at: https://www.bitbucket.org/" + user + "/" + slug + " was successfully deleted")
    else:
        if len(response.text) > 0:
            data = json.loads(response.text)
            repos = data["error"]
            print("{0:<15s}{1:<s}".format("Error Message:", str(repos["message"])))
        print("{0:<15s}{1:<d}".format("Error code:", response.status_code))

def list_repos():
    user = arguments.username
    password = arguments.password
    if not user:
        print("Error: The list option requires a username to be provided")
        return

    requrl = apiendpoint + user
    response = None
    if password:
        auth_token = requests.auth.HTTPBasicAuth(user, password)
        response = requests.get(requrl, auth=auth_token)
    else:
        response = requests.get(requrl)

    if response.status_code >= 200 and response.status_code < 300:
        data = json.loads(response.text)
        repos = data["values"]
        for repo in repos:
            print("{0:<15s}{1:<s}".format("Repository:", str(repo["name"])))
            print("{0:<15s}{1:<s}".format("Description:", str(repo["description"])))
            print("{0:<15s}{1:<s}".format("Language:", str(repo["language"])))
            print("{0:<15s}{1:<s}".format("Private:", str(repo["is_private"])))
            print("{0:<15s}{1:<s}".format("SCM:", str(repo["scm"])))
            print("{0:<15s}{1:<.0f} KB\n".format("Size:", repo["size"] / 1024))
    else:
        if len(response.text) > 0:
            data = json.loads(response.text)
            repos = data["error"]
            print("{0:<15s}{1:<s}".format("Error Message:", str(repos["message"])))
        print("{0:<15s}{1:<d}".format("Error code:", response.status_code))

def invalid_action():
    if arguments:
        print("Invalid action: " + str(arguments.action))
    else:
        print("Error: No arguments provided")

if __name__ == '__main__':
    arguments = clparser.parse_args()
    main()
