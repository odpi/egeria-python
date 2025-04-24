"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import asyncio
import json
import os
import time
from contextlib import nullcontext as does_not_raise

import pytest

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.core_omag_server_config import CoreServerConfig
from pyegeria.feedback_manager_omvs import FeedbackManager

disable_ssl_warnings = True


TESTING_EGERIA_PLATFORM_URL = os.environ.get(
    "TESTING_EGERIA_PLATFORM_URL", "https://localhost:9443"
)

view_server = "qs-view-server"
user = "erinoverview"
password = "secret"

fm_client = FeedbackManager(view_server, TESTING_EGERIA_PLATFORM_URL, user)


bearer_token = fm_client.create_egeria_bearer_token(user, password)

term_guid = "1dfb68d4-4fc7-49d1-9cac-11b0073e6266"

tag_for_testing = {
    "isPrivateTag": False,
    "name": "testing tag",
    "description": "This is a tag for testing purpose",
}

rating = {
    "class": "RatingProperties",
    "starRating": "TWO_STARS",
    "review": "This is my review",
}

notelog_for_testing = {
    "class": "NoteLogProperties",
    "qualifiedName": "test-note-log",
    "name": "Test Note Log",
    "description": "This is a note log for testing purposes",
    "additionalProperties": {"skyColor": "blue", "bestNoteLogEver": "this one"},
}

updated_notelog_for_testing = {
    "class": "ReferenceableUpdateRequestBody",
    "elementProperties": {
        "class": "NoteLogProperties",
        "qualifiedName": "test-note-log",
        "name": "Test Note Log",
        "description": "This is a note log for testing purposes, with updates",
        "additionalProperties": {
            "waterColor": "blue",
            "bestNoteLogEver": "still this one",
        },
    },
}

note_for_testing = {
    "class": "NoteProperties",
    "qualifiedName": "ready for testing",
    "title": "Ready for Testing",
    "text": "This element has been reviewed and is ready for further testing",
    "additionalProperties": {"status": "Testing Ready", "isCritical?": "No"},
}

updated_note_for_testing = {
    "class": "ReferenceableUpdateRequestBody",
    "elementProperties": {
        "class": "NoteProperties",
        "qualifiedName": "ready for testing",
        "title": "Ready for Testing",
        "text": "This element has been reviewed and is ready for further testing after subsequent updates",
        "additionalProperties": {"hasBeenUpdated?": "not sure", "isCritical?": "Yes"},
    },
}


standard_comment = {
    "class": "ReferenceableUpdateRequestBody",
    "elementProperties": {
        "class": "CommentProperties",
        "qualifiedName": "ExampleStandardComment",
        "commentText": "This is just an example STANDARD comment",
        "comment-type": "STANDARD_COMMENT",
        "additionalProperties": {
            "propertyName1": "property value 1",
            "propertyNameN": "property value N",
        },
    },
}

updated_standard_comment = {
    "class": "ReferenceableUpdateRequestBody",
    "elementProperties": {
        "class": "CommentProperties",
        "qualifiedName": "ExampleStandardComment",
        "commentText": "This is just an example of an updatedSTANDARD comment",
        "comment-type": "STANDARD_COMMENT",
        "additionalProperties": {
            "propertyName2": "property value 2",
            "propertyNameN": "property value N",
        },
    },
}

reply_comment = {
    "class": "ReferenceableUpdateRequestBody",
    "elementProperties": {
        "class": "CommentProperties",
        "qualifiedName": "ExampleReplyComment",
        "commentText": "This is just an example STANDARD comment reply",
        "comment-type": "STANDARD_COMMENT",
        "additionalProperties": {
            "propertyName1": "property value 1",
            "propertyNameN": "property value N",
        },
    },
}


question_comment = {
    "class": "ReferenceableUpdateRequestBody",
    "elementProperties": {
        "class": "CommentProperties",
        "qualifiedName": "ExampleQuestionComment",
        "commentText": "This is just an example Question comment. We would pose some question here.",
        "commentType": "QUESTION",
        "additionalProperties": {
            "propertyName1": "property value 1",
            "propertyNameN": "property value N",
        },
    },
}

answer_comment = {
    "class": "ReferenceableUpdateRequestBody",
    "elementProperties": {
        "class": "CommentProperties",
        "qualifiedName": "ExampleAnswerComment",
        "commentText": "This is just an example Answer comment. We would propose an answer to a question question here.",
        "commentType": "ANSWER",
        "additionalProperties": {
            "propertyName1": "property value 1",
            "propertyNameN": "property value N",
        },
    },
}


def jprint(info, comment=None):
    if comment:
        print(comment)
    print(json.dumps(info, indent=2))


def valid_guid(guid):
    if (guid is None) or (type(guid) is not str):
        return False
    else:
        return True


#
## test_add_comment_reply test
#
def test_add_comment_reply():
    comment_response = fm_client.add_comment_to_element(
        term_guid, body=standard_comment
    )
    reply_response = fm_client.add_comment_reply(
        term_guid, comment_response["guid"], body=reply_comment
    )
    fm_client.remove_comment_from_element(reply_response["guid"])
    fm_client.remove_comment_from_element(comment_response["guid"])
    assert reply_response["relatedHTTPCode"] == 200
    assert reply_response["class"] == "GUIDResponse"
    assert "guid" in reply_response


def test_add_comment_reply_with_private_reply():
    comment_response = fm_client.add_comment_to_element(
        term_guid, body=standard_comment
    )
    reply_response = fm_client.add_comment_reply(
        term_guid, comment_response["guid"], body=reply_comment, is_public=False
    )
    fm_client.remove_comment_from_element(reply_response["guid"])
    fm_client.remove_comment_from_element(comment_response["guid"])
    assert reply_response["relatedHTTPCode"] == 200
    assert reply_response["class"] == "GUIDResponse"
    assert "guid" in reply_response


def test_add_comment_reply_with_access_service_specified():
    comment_response = fm_client.add_comment_to_element(
        term_guid, body=standard_comment
    )
    reply_response = fm_client.add_comment_reply(
        term_guid,
        comment_response["guid"],
        body=reply_comment,
        access_service_url_marker="asset-manager",
    )
    fm_client.remove_comment_from_element(reply_response["guid"])
    fm_client.remove_comment_from_element(comment_response["guid"])
    assert reply_response["relatedHTTPCode"] == 200
    assert reply_response["class"] == "GUIDResponse"
    assert "guid" in reply_response


#
## test_add_comment_to_element test
#
def test_add_comment_to_element():
    response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    fm_client.remove_comment_from_element(response["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "GUIDResponse"
    assert "guid" in response


#
## test_add_like_to_element test
#
def test_add_like_to_element():
    response = fm_client.add_like_to_element(term_guid)
    fm_client.remove_like_from_element(term_guid)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_add_rating_to_element test
#
def test_add_rating_to_element():
    response = fm_client.add_rating_to_element(term_guid, body=rating)
    fm_client.remove_rating_from_element(term_guid)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_add_tag_to_element test
#
def test_add_tag_to_element():
    informal_tag = fm_client.create_informal_tag(tag_for_testing)
    response = fm_client.add_tag_to_element(term_guid, informal_tag["guid"])
    fm_client.delete_tag(informal_tag["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_clear_accepted_answer test
#


def test_clear_accepted_answer():
    question_comment_response = fm_client.add_comment_to_element(
        term_guid, body=question_comment
    )
    answer_comment_response = fm_client.add_comment_reply(
        term_guid, question_comment_response["guid"], body=answer_comment
    )
    setup_response = fm_client.setup_accepted_answer(
        question_comment_response["guid"], answer_comment_response["guid"]
    )
    response = fm_client.clear_accepted_answer(
        question_comment_response["guid"], answer_comment_response["guid"]
    )
    fm_client.remove_comment_from_element(answer_comment_response["guid"])
    fm_client.remove_comment_from_element(question_comment_response["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_create_informal_tag test
#
def test_create_informal_tag():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "test-tag-from-python",
        "description": "this tag was created using the python API for testing purposes",
    }
    response = fm_client.create_informal_tag(my_test_tag_body)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "GUIDResponse"
    assert valid_guid(response["guid"])
    fm_client.delete_tag(response["guid"])


#
## test_create_note test
#
def test_create_note():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.create_note(note_log_response["guid"], body=note_for_testing)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "GUIDResponse"
    assert valid_guid(response["guid"])
    fm_client.remove_note_log(note_log_response["guid"])


#
## test_create_note_log test
#
def test_create_note_log():
    response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "GUIDResponse"
    assert valid_guid(response["guid"])
    fm_client.remove_note_log(response["guid"])


#
## test_delete_tag test
#
def test_delete_tag():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "test-tag-from-python",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_response = fm_client.create_informal_tag(my_test_tag_body)
    assert create_response["relatedHTTPCode"] == 200
    assert create_response["class"] == "GUIDResponse"
    assert valid_guid(create_response["guid"])
    delete_response = fm_client.delete_tag(create_response["guid"])
    assert delete_response["relatedHTTPCode"] == 200
    assert delete_response["class"] == "VoidResponse"


#
## test_find_my_tags test
#
def test_find_my_tags():
    my_test_tag_body = {
        "isPrivateTag": True,
        "name": "one of my tags",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_response = fm_client.create_informal_tag(my_test_tag_body)
    response = fm_client.find_my_tags({"filter": "one"}, starts_with=True)
    assert response[0]["isPrivateTag"] == my_test_tag_body["isPrivateTag"]
    assert response[0]["name"] == my_test_tag_body["name"]
    assert response[0]["description"] == my_test_tag_body["description"]
    delete_response = fm_client.delete_tag(create_response["guid"])


def test_find_my_tags_with_no_tags():
    response = fm_client.find_my_tags({"filter": "one"}, starts_with=True)
    assert response["class"] == "InformalTagsResponse"
    assert response["relatedHTTPCode"] == 200


def test_find_my_tags_with_no_tags_and_details():
    response = fm_client.find_my_tags(
        {"filter": "one"}, starts_with=True, detailed_response=True
    )
    assert response["class"] == "InformalTagsResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_find_note_logs test
#
def test_find_note_logs():
    create_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.find_note_logs({"filter": ""})
    assert "class" in response[0]
    assert "qualifiedName" in response[0]
    assert "description" in response[0]
    assert "guid" in response[0]
    fm_client.remove_note_log(create_response["guid"])


def test_find_note_logs_detailed():
    create_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.find_note_logs({"filter": ""}, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "NoteLogsResponse"
    assert "elementList" in response
    fm_client.remove_note_log(create_response["guid"])


def test_find_note_logs_with_no_note_logs():
    response = fm_client.find_note_logs({"filter": ""}, starts_with=True)
    assert response["class"] == "NoteLogsResponse"
    assert response["relatedHTTPCode"] == 200


def test_find_note_logs_with_no_no_note_and_details():
    response = fm_client.find_note_logs(
        {"filter": ""}, starts_with=True, detailed_response=True
    )
    assert response["class"] == "NoteLogsResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_find_notes test
#
def test_find_notes():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.create_note(note_log_response["guid"], body=note_for_testing)
    response = fm_client.find_notes({"filter": ""})
    assert "class" in response[0]
    assert "qualifiedName" in response[0]
    assert "guid" in response[0]
    fm_client.remove_note_log(note_log_response["guid"])


def test_find_notes_detailed():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    note_response = fm_client.create_note(
        note_log_response["guid"], body=note_for_testing
    )
    response = fm_client.find_notes({"filter": ""}, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "NotesResponse"
    assert "elementList" in response
    fm_client.remove_note_log(note_log_response["guid"])


def test_find_notes_with_no_notes():
    response = fm_client.find_notes({"filter": ""}, starts_with=True)
    assert response["class"] == "NotesResponse"
    assert response["relatedHTTPCode"] == 200


def test_find_notes_with_no_notes_and_details():
    response = fm_client.find_notes(
        {"filter": ""}, starts_with=True, detailed_response=True
    )
    assert response["class"] == "NotesResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_find_tags test
#
def test_find_tags():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "This tag is public",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_response = fm_client.create_informal_tag(my_test_tag_body)
    response = fm_client.find_tags({"filter": "public"}, ends_with=True)
    assert response[0]["isPrivateTag"] == my_test_tag_body["isPrivateTag"]
    assert response[0]["name"] == my_test_tag_body["name"]
    assert response[0]["description"] == my_test_tag_body["description"]
    delete_response = fm_client.delete_tag(create_response["guid"])


def test_find_tags_with_no_tags():
    response = fm_client.find_tags({"filter": "one"}, starts_with=True)
    assert response["class"] == "InformalTagsResponse"
    assert response["relatedHTTPCode"] == 200


def test_find_tags_with_no_tags_and_details():
    response = fm_client.find_tags(
        {"filter": "one"}, starts_with=True, detailed_response=True
    )
    assert response["class"] == "InformalTagsResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_find_comments test
#
def test_can_handle_no_comments():
    response = fm_client.find_comments({"filter": ""})
    assert response["class"] == "CommentElementsResponse"
    assert response["relatedHTTPCode"] == 200


def test_can_handle_no_comments_with_details_requested():
    response = fm_client.find_comments({"filter": ""}, detailed_response=True)
    assert response["class"] == "CommentElementsResponse"
    assert response["relatedHTTPCode"] == 200


def test_find_comments():
    create_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.find_comments({"filter": ""})
    assert "class" in response[0]
    assert response[0]["class"] == "CommentProperties"
    assert "qualifiedName" in response[0]
    assert "guid" in response[0]
    fm_client.remove_comment_from_element(create_response["guid"])


def test_find_comments_detailed():
    create_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.find_comments({"filter": ""}, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "CommentElementsResponse"
    assert "elementList" in response
    fm_client.remove_comment_from_element(create_response["guid"])


#
## test_get_attached_comments test
#
def test_get_attached_comments():
    create_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.get_attached_comments(term_guid)
    assert "class" in response[0]
    assert response[0]["class"] == "CommentProperties"
    assert "qualifiedName" in response[0]
    assert "guid" in response[0]
    fm_client.remove_comment_from_element(create_response["guid"])


def test_get_attached_comments_detailed():
    create_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.get_attached_comments(term_guid, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "CommentElementsResponse"
    assert "elementList" in response
    fm_client.remove_comment_from_element(create_response["guid"])


def test_get_attached_comments_with_no_comments():
    response = fm_client.get_attached_comments(term_guid)
    assert response["class"] == "CommentElementsResponse"
    assert response["relatedHTTPCode"] == 200


def test_get_attached_comments_with_no_comments_and_details():
    response = fm_client.get_attached_comments(term_guid, detailed_response=True)
    assert response["class"] == "CommentElementsResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_get_attached_likes test
#
def test_get_attached_likes():
    create_response = fm_client.add_like_to_element(term_guid)
    response = fm_client.get_attached_likes(term_guid)
    assert "user" in response[0]
    assert "guid" in response[0]
    fm_client.remove_like_from_element(term_guid)


def test_get_attached_likes_detailed():
    create_response = fm_client.add_like_to_element(term_guid)
    response = fm_client.get_attached_likes(term_guid, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "LikeElementsResponse"
    assert "elementList" in response
    fm_client.remove_like_from_element(term_guid)


def test_get_attached_likes_with_no_likes():
    response = fm_client.get_attached_likes(term_guid)
    assert response["class"] == "LikeElementsResponse"
    assert response["relatedHTTPCode"] == 200


def test_get_attached_likes_with_no_likes_and_details():
    response = fm_client.get_attached_likes(term_guid, detailed_response=True)
    assert response["class"] == "LikeElementsResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_get_attached_ratings test
#


def test_get_attached_ratings():
    create_response = fm_client.add_rating_to_element(term_guid, body=rating)
    response = fm_client.get_attached_ratings(term_guid)
    assert "starRating" in response[0]
    assert "guid" in response[0]
    fm_client.remove_rating_from_element(term_guid)


def test_get_attached_ratings_detailed():
    create_response = fm_client.add_rating_to_element(term_guid, body=rating)
    response = fm_client.get_attached_ratings(term_guid, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "RatingElementsResponse"
    assert "elementList" in response
    fm_client.remove_rating_from_element(term_guid)


def test_get_attached_ratings_with_no_ratings():
    response = fm_client.get_attached_ratings(term_guid)
    assert response["class"] == "RatingElementsResponse"
    assert response["relatedHTTPCode"] == 200


def test_get_attached_ratings_with_no_ratings_and_details():
    response = fm_client.get_attached_ratings(term_guid, detailed_response=True)
    assert response["class"] == "RatingElementsResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_get_attached_tags test
#
def test_get_attached_tags():
    create_response = fm_client.create_informal_tag(tag_for_testing)
    fm_client.add_tag_to_element(term_guid, create_response["guid"])
    response = fm_client.get_attached_tags(term_guid)
    assert "name" in response[0]
    assert "isPrivateTag" in response[0]
    assert "guid" in response[0]
    fm_client.delete_tag(create_response["guid"])


def test_get_attached_tags_detailed():
    create_response = fm_client.create_informal_tag(tag_for_testing)
    fm_client.add_tag_to_element(term_guid, create_response["guid"])
    response = fm_client.get_attached_tags(term_guid, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "InformalTagsResponse"
    assert "tags" in response
    fm_client.delete_tag(create_response["guid"])


def test_get_attached_tags_with_no_tags():
    response = fm_client.get_attached_tags(term_guid)
    assert response["class"] == "InformalTagsResponse"
    assert response["relatedHTTPCode"] == 200


def test_get_attached_tags_with_no_tags_and_details():
    response = fm_client.get_attached_tags(term_guid, detailed_response=True)
    assert response["class"] == "InformalTagsResponse"
    assert response["relatedHTTPCode"] == 200


#
## test_get_comment test
#


def test_get_comment():
    create_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.get_comment(create_response["guid"])
    assert "class" in response
    assert response["class"] == "CommentProperties"
    assert "qualifiedName" in response
    assert "guid" in response
    fm_client.remove_comment_from_element(create_response["guid"])


def test_get_comment_detailed():
    create_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.get_comment(create_response["guid"], detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "CommentResponse"
    fm_client.remove_comment_from_element(create_response["guid"])


def test_get_comment_with_bad_guid():
    with pytest.raises(InvalidParameterException):
        response = fm_client.get_comment("1234")


#
## test_get_elements_by_tag test
#
def test_get_elements_by_tag():
    create_response = fm_client.create_informal_tag(tag_for_testing)
    fm_client.add_tag_to_element(term_guid, create_response["guid"])
    response = fm_client.get_elements_by_tag(create_response["guid"])
    assert "name" in response[0]
    assert "typeName" in response[0]
    assert "properties" in response[0]
    assert "guid" in response[0]
    fm_client.delete_tag(create_response["guid"])


def test_get_elements_by_tag_detailed():
    create_response = fm_client.create_informal_tag(tag_for_testing)
    fm_client.add_tag_to_element(term_guid, create_response["guid"])
    response = fm_client.get_elements_by_tag(
        create_response["guid"], detailed_response=True
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "RelatedElementsResponse"
    assert "elementList" in response
    fm_client.delete_tag(create_response["guid"])


#
## test_get_note_by_guid test
#


def test_get_note_by_guid():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    note_response = fm_client.create_note(
        note_log_response["guid"], body=note_for_testing
    )
    response = fm_client.get_note_by_guid(note_response["guid"])
    assert "class" in response
    assert "qualifiedName" in response
    assert "guid" in response
    fm_client.remove_note_log(note_log_response["guid"])


def test_get_note_by_guid_detailed():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    note_response = fm_client.create_note(
        note_log_response["guid"], body=note_for_testing
    )
    response = fm_client.get_note_by_guid(note_response["guid"], detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "NoteResponse"
    assert "element" in response
    fm_client.remove_note_log(note_log_response["guid"])


#
## test_get_note_log_by_guid test
#


def test_get_note_log_by_guid():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.get_note_log_by_guid(note_log_response["guid"])
    assert "class" in response
    assert response["class"] == "NoteLogProperties"
    assert "qualifiedName" in response
    assert "guid" in response
    fm_client.remove_note_log(note_log_response["guid"])


def test_get_note_log_by_guid_detailed():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.get_note_log_by_guid(
        note_log_response["guid"], detailed_response=True
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "NoteLogResponse"
    assert "element" in response
    fm_client.remove_note_log(note_log_response["guid"])


#
## test_get_note_logs_by_name test
#


def test_get_note_logs_by_name():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.get_note_logs_by_name(
        {"filter": notelog_for_testing["qualifiedName"]}
    )
    assert "class" in response[0]
    assert response[0]["class"] == "NoteLogProperties"
    assert "qualifiedName" in response[0]
    assert "guid" in response[0]
    fm_client.remove_note_log(note_log_response["guid"])


def test_get_note_logs_by_name_detailed():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.get_note_logs_by_name(
        {"filter": notelog_for_testing["qualifiedName"]}, detailed_response=True
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "NoteLogsResponse"
    assert "elementList" in response
    fm_client.remove_note_log(note_log_response["guid"])


#
## test_get_note_logs_for_element test
#


def test_get_note_logs_for_element():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.get_note_logs_for_element(term_guid)
    assert "class" in response[0]
    assert response[0]["class"] == "NoteLogProperties"
    assert "qualifiedName" in response[0]
    assert "guid" in response[0]
    fm_client.remove_note_log(note_log_response["guid"])


def test_get_note_logs_for_element_detailed():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.get_note_logs_for_element(term_guid, detailed_response=True)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "NoteLogsResponse"
    assert "elementList" in response
    fm_client.remove_note_log(note_log_response["guid"])


#
## test_get_notes_for_note_log test
#
def test_get_notes_for_note_log():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.create_note(note_log_response["guid"], body=note_for_testing)
    response = fm_client.get_notes_for_note_log(note_log_response["guid"])
    assert "class" in response[0]
    assert "qualifiedName" in response[0]
    assert "guid" in response[0]
    fm_client.remove_note_log(note_log_response["guid"])


def test_get_notes_for_note_log_detailed():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    note_response = fm_client.create_note(
        note_log_response["guid"], body=note_for_testing
    )
    response = fm_client.get_notes_for_note_log(
        note_log_response["guid"], detailed_response=True
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "NotesResponse"
    assert "elementList" in response
    fm_client.remove_note_log(note_log_response["guid"])


#
## test_get_tag test
#
def test_get_tag():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "test-tag-from-python",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_response = fm_client.create_informal_tag(my_test_tag_body)
    response = fm_client.get_tag(create_response["guid"])
    assert response["isPrivateTag"] == my_test_tag_body["isPrivateTag"]
    assert response["name"] == my_test_tag_body["name"]
    assert response["description"] == my_test_tag_body["description"]
    delete_response = fm_client.delete_tag(create_response["guid"])


#
## test_get_tags_by_name test 1
#
def test_get_tags_by_name_test1():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "test-tag-from-python",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_response = fm_client.create_informal_tag(my_test_tag_body)
    response = fm_client.get_tags_by_name({"filter": my_test_tag_body["name"]})
    assert response[0]["isPrivateTag"] == my_test_tag_body["isPrivateTag"]
    assert response[0]["name"] == my_test_tag_body["name"]
    assert response[0]["description"] == my_test_tag_body["description"]
    delete_response = fm_client.delete_tag(create_response["guid"])


#
## test_get_tags_by_name test 2
#
def test_get_tags_by_name_test2():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "test-tag-from-python",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_1_response = fm_client.create_informal_tag(my_test_tag_body)
    create_2_response = fm_client.create_informal_tag(my_test_tag_body)
    response = fm_client.get_tags_by_name({"filter": my_test_tag_body["name"]})
    assert len(response) >= 2
    assert response[0]["isPrivateTag"] == my_test_tag_body["isPrivateTag"]
    assert response[0]["name"] == my_test_tag_body["name"]
    assert response[0]["description"] == my_test_tag_body["description"]
    assert response[1]["isPrivateTag"] == my_test_tag_body["isPrivateTag"]
    assert response[1]["name"] == my_test_tag_body["name"]
    assert response[1]["description"] == my_test_tag_body["description"]
    fm_client.delete_tag(create_1_response["guid"])
    fm_client.delete_tag(create_2_response["guid"])


#
## test_get_tags_by_name test 3
#
def test_get_tags_by_name_test3():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "test-tag-from-python",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_response = fm_client.create_informal_tag(my_test_tag_body)
    #    response = fm_client.get_tags_by_name(my_test_tag_body['name'], "view-server", 0, 10, True)
    response = fm_client.get_tags_by_name(
        {"filter": my_test_tag_body["name"]}, detailed_response=True
    )
    assert response["class"] == "InformalTagsResponse"
    assert response["relatedHTTPCode"] == 200
    assert "elementHeader" in response["tags"][0]
    assert "properties" in response["tags"][0]
    delete_response = fm_client.delete_tag(create_response["guid"])


#
## test_remove_comment_from_element test
#
def test_remove_comment_from_element():
    create_comment = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.remove_comment_from_element(create_comment["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_remove_like_from_element test
#
def test_remove_like_from_element():
    fm_client.add_like_to_element(term_guid)
    response = fm_client.remove_like_from_element(term_guid)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_remove_note test
#
def test_remove_note():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    note_response = fm_client.create_note(
        note_log_response["guid"], body=note_for_testing
    )
    response = fm_client.remove_note_log(note_log_response["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"
    #


## test_remove_note_log test
#
def test_remove_note_log():
    create_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.remove_note_log(create_response["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_remove_rating_from_element test
#
def test_remove_rating_from_element():
    fm_client.add_rating_to_element(term_guid, body=rating)
    response = fm_client.remove_rating_from_element(term_guid)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_remove_tag_from_element test
#
def test_remove_tag_from_element():
    informal_tag = fm_client.create_informal_tag(tag_for_testing)
    fm_client.add_tag_to_element(term_guid, informal_tag["guid"])
    response = fm_client.remove_tag_from_element(term_guid, informal_tag["guid"])
    fm_client.delete_tag(informal_tag["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_setup_accepted_answer test
#
def test_setup_accepted_answer():
    question_comment_response = fm_client.add_comment_to_element(
        term_guid, body=question_comment
    )
    answer_comment_response = fm_client.add_comment_reply(
        term_guid, question_comment_response["guid"], body=answer_comment
    )
    response = fm_client.setup_accepted_answer(
        question_comment_response["guid"], answer_comment_response["guid"]
    )
    fm_client.remove_comment_from_element(answer_comment_response["guid"])
    fm_client.remove_comment_from_element(question_comment_response["guid"])
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"


#
## test_update_comment test
#
def test_update_comment():
    add_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.update_comment(add_response["guid"], updated_standard_comment)
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"
    fm_client.remove_comment_from_element(add_response["guid"])


#
## test_update_comment_visibility test
#
def test_update_comment_visibility():
    add_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.update_comment_visibility(
        term_guid, add_response["guid"], is_public=True
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"
    fm_client.remove_comment_from_element(add_response["guid"])


def test_update_comment_visibility2():
    add_response = fm_client.add_comment_to_element(term_guid, body=standard_comment)
    response = fm_client.update_comment_visibility(
        term_guid, add_response["guid"], is_public=False
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"
    fm_client.remove_comment_from_element(add_response["guid"])


#
## test_update_note test
#
def test_update_note():
    note_log_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    jprint(note_log_response)
    note_response = fm_client.create_note(
        note_log_response["guid"], body=note_for_testing
    )
    jprint(note_response, "Note Response:")
    jprint(updated_note_for_testing, "Updated Note for testing:")
    response = fm_client.update_note(
        note_response["guid"], updated_note_for_testing, is_merge_update=True
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"
    fm_client.remove_note_log(note_log_response["guid"])


#
## test_update_note_log test
#
def test_update_note_log():
    create_response = fm_client.create_note_log(term_guid, body=notelog_for_testing)
    response = fm_client.update_note_log(
        create_response["guid"], updated_notelog_for_testing, is_merge_update=True
    )
    assert response["relatedHTTPCode"] == 200
    assert response["class"] == "VoidResponse"
    fm_client.remove_note_log(create_response["guid"])


#
## test_update_tag_description test
#
def test_update_tag_description():
    my_test_tag_body = {
        "isPrivateTag": False,
        "name": "test-tag-from-python",
        "description": "this tag was created using the python API for testing purposes",
    }
    create_response = fm_client.create_informal_tag(my_test_tag_body)
    updated_description = "This is my updated description"
    update_response = fm_client.update_tag_description(
        create_response["guid"], {"description": updated_description}
    )
    assert update_response["relatedHTTPCode"] == 200
    assert update_response["class"] == "VoidResponse"
    get_response = fm_client.get_tag(create_response["guid"])
    assert get_response["description"] == updated_description
    fm_client.delete_tag(create_response["guid"])
