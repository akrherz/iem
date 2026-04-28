# Vendor Static Assets Deployment

This document explains how assets under /vendor/ are provided to the webroot.

## Why This Exists

A number of IEM maintained repos use common javascript / CSS libraries.  Since
it is nice to do offline development and for patching, a simple github vendor
repo is maintained and synced to /opt/vendor within the webfarm nodes.

## Source of Truth

- Upstream repo: [akrherz/vendor](https://github.com/akrherz/vendor)
- Version pinning policy: None
- Integrity/verification policy: None

## Provisioning Model

1. The github repo is cloned to /opt/vendor
2. That same repo contains an apache configuration snippet that mounts the
   repo to answer /vendor/ URLs within other repos.

## Validation

It is safe for code review to assume resources are properly references with
/vendor/ mounted URI paths.
