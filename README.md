# katello-publish-cv

The purpose of this script is to automate the process of publishing and promoting content views in Red Hat Satellite 6. This makes it possible to push all new RPMs through your CVs and CCVs automatically. It can for example be run as a cron job at a certain date when you want to publish all new content to a certain lifecyle environment.

# Workflow

This script will first get all Content Views (CVs) from the API. Then for each CV, it will check if any of the underlying repos in that CV has had any updates since last time the CV was published. If so, the CV is published again so that it contain the latest content. 

Then, the script moves on to the Composite Content Views (CCVs). Each CCV is updated with the latest versions of its components, i.e. the version of each CV that is in the Library lifecycle environment.  Then the CCV will be published and also promoted to the TEST environment.

# What versions does it work on

This script has been tested and works on:

* Satellite 6.2 Beta

# Prerequisites

* A login user to Satellite
* Python
* python-requests

# Usage

~~
./katello-publish-cvs.py
~~

# Example Output

In this example, there has been new RPMs synced to the repository "Red Hat Enterprise Linux 7 Server RPMs x86_64 7Server" which is part of CV-RHEL7. Then the output looks like the following:
~~
Organization "Default Organization has ID: 1
Lifecycle environments: {u'TEST': 4, u'PROD': 5, u'Library': 1}
A sync task for repo "Red Hat Enterprise Linux 7 Server RPMs x86_64 7Server" downloaded new content and ended after CV-RHEL7 was published last time
Publish CV-RHEL7 because some of its content has changed
CV-PUPPET doesn't need to be published
CV-CAPSULE doesn't need to be published
Waiting for publish tasks to finish...
Finished waiting after 160 seconds
Update CCV-RHEL7-CAPSULE with new compontent IDs: [10, 84, 83]
Publish new version of CCV-RHEL7-CAPSULE
Update CCV-RHEL7 with new compontent IDs: [84, 83]
Publish new version of CCV-RHEL7
Waiting for publish tasks to finish...
Finished waiting after 150 seconds
Promote all effected CCVs to TEST environment
~~

# Known issues

* All CCVs are published everytime the script is run, even if they are not changed. This can be improved by only publishing and promoting CCVs where any of the components have actually changed (future feature).

