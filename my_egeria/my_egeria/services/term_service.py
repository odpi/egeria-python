# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Collections related functions of my_egeria module.


"""

"""Skeleton file to be filled out further later in testing"""

def get_terms_for_glossary(self, glossary_name: str):
    """Glossary Name is the Glossary Qualified Name"""
    self.app.show_term_list(glossary_name)
    return

def show_term_details(self, glossary_name, term_name):
    """Both glossary and term names are Qualified Names"""
    self.app.show_term_details(term_name)
    return
