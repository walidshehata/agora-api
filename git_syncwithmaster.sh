#!/bin/bash

# This line will fetch the upstream repo (from Husain), chckit out to your local drive, and merge it with your own master code

git fetch upstream && git checkout master && git merge upstream/master