# katello-publish-cvs

This script gets all Content Views from Satellite 6 and publish a new version of them. After that, it iterates through all Composite Content Views and updates them with the new versions of its components. Then it publishes the Composite Content Views as well and promotes them to the first Lifecycle Environment, currently hard coded to TEST.
