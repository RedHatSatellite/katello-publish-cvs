#!/usr/bin/python

import json
import sys
import time


try:
    import requests
except ImportError:
    print "Please install the python-requests module."
    sys.exit(-1)

# URL to your Satellite 6 server
URL = "https://satellite6.example.com/"
# URL for the API to your deployed Satellite 6 server
SAT_API = URL + "katello/api/v2/"
# Katello-specific API
KATELLO_API = URL + "katello/api/"
POST_HEADERS = {'content-type': 'application/json'}
# Default credentials to login to Satellite 6
USERNAME = "admin"
PASSWORD = "changeme"
# Ignore SSL for now
SSL_VERIFY = False
# Name of the organization to be either created or used
ORG_NAME = "Default Organization"
# Dictionary for Life Cycle Environments ID and name
ENVIRONMENTS = {}
# Search string to list currently running publish tasks
publish_tasks = "foreman_tasks/api/tasks?search=utf8=%E2%9C%93&search=label+%3D+Actions%3A%3AKatello%3A%3AContentView%3A%3APublish+and+state+%3D+running"

def get_json(location):
    """
    Performs a GET using the passed URL location
    """

    r = requests.get(location, auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)

    return r.json()


def post_json(location, json_data):
    """
    Performs a POST and passes the data to the URL location
    """

    result = requests.post(location,
                            data=json_data,
                            auth=(USERNAME, PASSWORD),
                            verify=SSL_VERIFY,
                            headers=POST_HEADERS)

    return result.json()

def put_json(location, json_data):
    """
    Performs a PUT and passes the data to the URL location
    """

    result = requests.put(location,
                            data=json_data,
                            auth=(USERNAME, PASSWORD),
                            verify=SSL_VERIFY,
                            headers=POST_HEADERS)

    return result.json()

def wait_for_publish(seconds):
    """
    Wait for all publishing tasks to terminate. Search string is:
    label = Actions::Katello::ContentView::Publish and state = running
    """
   
    count = 0 
    print "DEBUG: Waiting for publish tasks to finish..."
    while get_json(URL + publish_tasks)["total"] != 0:
        time.sleep(seconds)
        count += 1

    print "DEBUG: Finished waiting after " + str(seconds * count) + " seconds"


def main():

    # Check that organization exists and extract its ID
    print "DEBUG: " + SAT_API + "organizations/" + ORG_NAME
    org_json = get_json(SAT_API + "organizations/" + ORG_NAME)
    
    if org_json.get('error', None):
        print "ERROR: Organization does not exist"
        sys.exit(1)

    org_id =org_json["id"]
    print "DEBUG: Organization ID: " + str(org_id)

    # Fill dictionary of Lifecycle Environments as {name : id}
    envs_json = get_json(KATELLO_API + "organizations/" + str(org_id) + "/environments")
    for env in envs_json["results"]:
        ENVIRONMENTS[env["name"]] = env["id"]

    print "DEBUG: Lifecycle environments: " + str(ENVIRONMENTS)
    
    # Get all non-composite CVs from the API
    print "DEBUG: " + SAT_API + "organizations/" + str(org_id) + "/content_views?noncomposite=true"
    cvs_json = get_json(SAT_API + "organizations/" + str(org_id) + "/content_views?noncomposite=true")
   
    # Publish a new version of all CVs
    published_cv_ids = []
    for cv in cvs_json["results"]:
        if not "Default Organization View" in cv["name"]:
            print "DEBUG: Publishing " + cv["name"]
            post_json(KATELLO_API + "content_views/" + str(cv["id"]) + "/publish", json.dumps({"description": "Automatic publish over API"}))
            published_cv_ids.append(cv["id"])

    wait_for_publish(10)

    # Get all CCVs from the API (TODO: don't use search to get CCVs by name)
    print "DEBUG: " + SAT_API + "organizations/" + str(org_id) + "/content_views"
    ccvs_json = get_json(SAT_API + "organizations/" + str(org_id) + "/content_views?search=CCV*")
    
    # Publish a new version of all CCs that contain any of the published CVs
    ccv_ids_to_promote = []
    for ccv in ccvs_json["results"]:
        new_component_ids = []
        
        for component in ccv["components"]:
            cv_json = get_json(KATELLO_API + "content_views/" + str(component["content_view"]["id"]))
            
            for version in cv_json["versions"]:
                if ENVIRONMENTS["Library"] in version["environment_ids"]:
                    new_component_ids.append(version["id"])
        
        print "DEBUG: Update " + ccv["name"] + " with new compontent IDs: " + str(new_component_ids)
        put_json(KATELLO_API + "content_views/" + str(ccv["id"]), json.dumps({"component_ids": new_component_ids}))
        
        print "DEBUG: Publish new version of " + ccv["name"]
        post_json(KATELLO_API + "content_views/" + str(ccv["id"]) + "/publish", json.dumps({"description": "Automatic publish over API"}))

        # Get the ID of the version in Library 
        version_in_library_id = get_json(KATELLO_API + "content_views/" + str(ccv["id"]) + "/content_view_versions?environment_id=" + str(ENVIRONMENTS["Library"]))["results"][0]["id"]
        ccv_ids_to_promote.append(str(version_in_library_id))

    wait_for_publish(10)
    
    print "DEBUG: Promote all new CCVs to TEST environment"
    for ccv_id in ccv_ids_to_promote:
        post_json(KATELLO_API + "content_view_versions/" + str(ccv_id) + "/promote", json.dumps({"environment_id": ENVIRONMENTS["TEST"]})) 

    print "DEBUG: End of main"

if __name__ == "__main__":
    main()

