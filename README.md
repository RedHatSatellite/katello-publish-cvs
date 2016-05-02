# katello-publish-cvs

The purpose of this script is to automate the process of publishing new content in Red Hat Satellite 6.

It performs the following steps:

1. Publish a new version of all Content Views
1. Update all comonents of all Composite Content Views to the latest published version
1. Publish a new version of all effected Composite Content Views
1. Promote all Composite Content Views to the first Lifecycle Environment (in this case hard-coded to TEST)
