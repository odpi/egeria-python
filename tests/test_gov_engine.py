"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This file contains a set of test routines to test the platform_services of the Egeria python client.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests. To run these tests you need to use the
Egeria lab environment and run the automate-curation lab to just before the initiateGovernanceAction

"""

import pytest
import requests
from datetime import datetime
import json

from contextlib import nullcontext as does_not_raise
disable_ssl_warnings = True

from pyegeria.exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,

)
from pyegeria.gov_engine import GovEng

def test_get_engine_actions():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
            "erinoverview")

        gov_actions = g_client.get_engine_actions()
        if gov_actions:
            print("\n\n")
            for g in gov_actions:
                print(json.dumps(g, indent=4))

        assert gov_actions is not None, "Failed to find governance actions"

    except (
            InvalidParameterException,
            PropertyServerException,
    ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_get_engine_action():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
            "erinoverview")
        guid = "EngineAction-417ceb34-0856-4b59-a3f0-b401406d0c21"
        gov_action = g_client.get_engine_action(guid)
        if gov_action:
            print("\n\n")
            # g_client.print_governance_action_summary(gov_action)
            print(json.dumps(gov_action, indent=4))

        assert gov_action is not None, "Failed to find governance actions"

    except (
            InvalidParameterException,
            PropertyServerException,
    ) as e:
        print_exception_response(e)
        assert False, "Invalid request"


@pytest.mark.skip(reason="bug")
def test_get_active_engine_actions():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
            "erinoverview")

        gov_actions = g_client.get_active_engine_actions()
        if gov_actions:
            print("\n\n")
            for g in gov_actions:
                print(json.dumps(g, indent=4))

        assert gov_actions is not None, "Failed to find governance actions"

    except (
            InvalidParameterException,
            PropertyServerException,
    ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_get_engine_actions_by_name():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
            "erinoverview")

        gov_actions = g_client.get_engine_actions_by_name('Listener: data/landing-area/hospitals')
        if gov_actions:
            print("\n\n")
            for g in gov_actions:
                print(json.dumps(g, indent=4))

        assert gov_actions is not None, "Failed to find governance actions"

    except (
            InvalidParameterException,
            PropertyServerException,
    ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_find_engine_actions():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
            "erinoverview")

        gov_actions = g_client.find_engine_actions('Populate.*')
        if gov_actions:
            print("\n\n")
            for g in gov_actions:
                print(json.dumps(g, indent=4))

        assert gov_actions is not None, "Failed to find governance actions"

    except (
            InvalidParameterException,
            PropertyServerException,
        ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_get_governance_action_process_by_guid():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
             "erinoverview" )

        guid = "GovernanceActionProcess-47925639-6a07-489f-b185-85be1722ec2e"
        gov_process = g_client.get_governance_action_process_by_guid(guid)
        print("\n\n" )
        if gov_process:
            print(json.dumps(gov_process, indent=4))
        assert gov_process is not None, "Failed to find governance process"

    except (
            InvalidParameterException,
            PropertyServerException,
        ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_get_governance_action_process_by_name():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
             "erinoverview" )

        name = "governance-action-process:clinical-trials:drop-foot:weekly-measurements:onboarding"
        gov_process = g_client.get_governance_action_processes_by_name(name)
        print("\n\n" )
        if gov_process:
            print(json.dumps(gov_process, indent=4))
        assert gov_process is not None, "Failed to find governance process"

    except (
            InvalidParameterException,
            PropertyServerException,
        ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_find_governance_action_processes():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
             "erinoverview" )

        gov_processes = g_client.find_governance_action_processes(".*")
        if gov_processes:
            print("\n\n")
            for g in gov_processes:
                print(json.dumps(g, indent=4))

        assert gov_processes is not None, "Failed to find governance action processes"

    except (
            InvalidParameterException,
            PropertyServerException,
        ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_initiate_governance_action_process():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
             "erinoverview" )


        n = datetime.now()
        governance_process_GUID = g_client.initiate_governance_action_process(
                    "governance-action-process:clinical-trials:drop-foot:weekly-measurements:onboarding",
                    None,None, n,
                    None,None,None)

        print("\n\n" + governance_process_GUID)
        assert governance_process_GUID is not None, "Failed to initiate governance action"

    except (
            InvalidParameterException,
            PropertyServerException,
    ) as e:
        print_exception_response(e)
        assert False, "Invalid request"
def test_initiate_engine_action():
    try:
        g_client = GovEng(
            "cocoMDS2", "https://127.0.0.1:9443",
             "erinoverview" )

        request_parameters = {
            "sourceFile": "/moo",
            "destinationFolder": "/goo"
        }
        n = datetime.now()
        governanceActionGUID = g_client.initiate_engine_action(
                        "FTP Oak Dene Week 1", 0,"meow", "a description",
                        None,None,None,n, "AssetGovernance", "simulate-ftp",
                        request_parameters, "Populate landing area",None,None,None)

        print("\n\n" + governanceActionGUID)
        assert governanceActionGUID is not None, "Failed to initiate governance action"

    except (
            InvalidParameterException,
            PropertyServerException,
    ) as e:
        print_exception_response(e)
        assert False, "Invalid request"

def test_print_engine_actions():
    g_client = GovEng(
        "cocoMDS1", "https://127.0.0.1:9444",
        "erinoverview")
    g_client.print_engine_actions()

    assert True






















def test_print_governance_actions():
    g_client = GovEng(
        "cocoMDS2", "https://127.0.0.1:9443",
        "erinoverview")

    g_client.print_governance_actions()