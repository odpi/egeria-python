#!/bin/zsh

#
#   PDX-License-Identifier: Apache-2.0
#   Copyright Contributors to the ODPi Egeria project.
#
#
#


#export PYTHONPATH=/Users/dwolfson/localGit/egeria-v5-3/egeria_tui/src:$PYTHONPATH

export PYTHONPATH=/User/petercoldicott/PycharmProjects/egeria/my_egeria:$PYTHONPATH
export EGERIA_DEBUG_METHODS=true
export EGERIA_PLATFORM_URL=https://localhost:9443
export EGERIA_VIEW_SERVER=qs-view-server
export EGERIA_USER=erinoverview
export EGERIA_USER_PASSWORD=secret
export EGERIA_SSL_VERIFY=false
export EGERIA_DEBUG_METHODS=true
export EGERIA_DEBUG_RESULTS=true
textual run --dev my_egeria.py

