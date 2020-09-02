# conda-bots

This repository contains a small python web app intended for deployment to heroku
for handling simple, automated tasks using GitHub webhooks for any number of
repositories, independent of the GitHub organization in which they reside.

## Requirements for Adding to a Repository

* Webhook added to repository settiongs using this URL: https://conda-bots.herokuapp.com/ . The secret
for this webhook stored in `GH_SECRET` of the deployed heroku app should be added to the GitHub webhook
configuration. The webhook can be configured to either send all events to this heroku application or
an allowlist of only the following events:

        * pull request open
        * issue comment created

* `@anaconda-issue-bot` added as a collaborator to the repository for commenting, labeling, and PR status configuration.
* For the CLA Bot to block PR merges without CLA signing verification, the master branch for the repository must be configured
to require the status `verifcation/cla-signed` to be passing before merging.

## Librarian

This web app includes functionality to summon the configured bot, `@anaconda-issue-bot` to reply with configured
FAQ responses stored in [responses.yml](./responses.yml). `@anaconda-issue-bot help` will ask the bot to respond
with the list of available topics with configured responses.

## CLA-Bot

The ClaBot class of this application is configured to respond automatically to pull request opening and upon
being summoned on an existing pull request in an issue comment. If it finds the user in the conda/cla-config
contributors list, the ClaBot will do the following:

        * add the `cla-signed` label to the PR
        * mark the `verification/cla-signed` status for the PR as successful.

If the bot does not find the user in the accepted contributors list, the ClaBot will:

        * mark the `verification/cla-signed` status for the PR as failed.
        * include a welcome message in an issue comment with instructions on signing the CLA for newly opened pull requests.

