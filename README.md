# twitter-capsule
Code to run a Mastodon bot that posts from a Twitter archive.

## Prerequisites

This script can be run in two ways; either running it natively on a Linux machine
with Python installed or from a Docker container. It can also be run using WSL on
Windows. It may also work natively on Windows and MacOS, but may require
additional setup.

Ensure either that:

* Python 3.8+ is installed, or
* Docker and docker-compose are installed

Which one you choose will determine which config file you use. You will also
need to request and download your Twitter archive from Twitter. This may take
several days to complete.

You will also need to have created an account on botsin.space and set up a
developer app. You will need the key for the app in order for this to function.

## Setup

### Running natively

When running natively, it's recommended your Python working directory be in the
root of this project. Create a `files` directory here so that there will be two
directories: app, and files.

Extract your Twitter archive to its own folder and copy that entire folder
inside the files directory.

Then, edit the `variables.sh` file and fill in the variables according to the
comments. Use quotation marks for any setting that contains a space.

### Running in Docker

When running in Docker, you will need to establish some folder for `files`, but
it does not need to be in the same location as this project. Instead, it will
be set in the `docker-compose.yml` file. Once you know the path, you'll need to
insert it into this file, along with the other variables.

When using docker-compose, you can safely ignore the `variables.sh` file, since
you'll instead be adding all your variables to the `docker-compose.yml` file.
This is done in the "environment" section. Don't use quotation marks for the
settings which require a space. They're not needed and things will misbehave.

### Have Questions?

I don't blame you! I need to add a lot more to this guide before I consider it
done. This is a first draft, and if it works for you, that's amazing! If not,
maybe wait and see if I add more detail? Or reach out to me. If you have to.