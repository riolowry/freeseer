#!/usr/bin/python
# -*- coding: utf-8 -*-

# freeseer - vga/presentation capture software
#
#  Copyright (C) 2013  Free and Open Source Software Learning Centre
#  http://fosslc.org
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# For support, questions, suggestions or any other inquiries, visit:
# http://wiki.github.com/Freeseer/freeseer/

"""
Rss FeedParser
--------------

An import plugin which provides a RSS parser used when adding presentations

@author: Rio Lowry
"""

from HTMLParser import HTMLParser

from feedparser import parse

from freeseer.framework.plugin import IImporter


class MLStripper(HTMLParser):
    """Simple stripper to remove markup

    MLStripper from http://stackoverflow.com/a/925630/72321
    """
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    """Helper functions to strip markup from passed object"""
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class FeedParser(IImporter):
    """FeedParser plugin for Freeseer

    Provides functionality to allow a RSS feed to be fetched and parsed
    """

    name = "Rss FeedParser"
    os = ["linux", "linux2"]

    def parse(self, feed_url):
        """Takes feed_url, fetches, parses and saves feed in parsed_feed."""
        parsed_feed = parse(feed_url)
        self.presentations = parsed_feed.entries
        self.presentations_length = len(self.presentations)
        self.presentation_list = []
        for i, entry in enumerate(self.presentations):
            presentation = {}
            presentation["Title"] = entry.title.strip()

            pres_data = entry["summary_detail"]["value"]

            # We want to split the pres_data by 3 spaces because some field
            # data contain spaces and we don't want to erroneously split that
            # data.

            pres_data = filter(None, pres_data.split("   "))

            presentation["Speaker"] = self.get_presentation_field(pres_data, "field-field-speaker")
            presentation["Abstract"] = self.get_presentation_field(pres_data, "field-field-abstract")
            presentation["Level"] = self.get_presentation_field(pres_data, "field-field-level")
            presentation["Status"] = self.get_presentation_field(pres_data, "field-field-status")
            presentation["Time"] = self.get_presentation_field(pres_data, "field-field-time")
            presentation["Event"] = self.get_presentation_field(pres_data, "field-field-event")
            presentation["Room"] = self.get_presentation_field(pres_data, "field-field-room")
            self.presentation_list.append(presentation)

    def get_presentations_list(self):
        """Returns list of dictionaries of all presentations on parsed feed."""
        return self.presentation_list

    def get_presentation_field(self, presentation, field_name):
        """Returns the field_name of the presentation at presentation"""

        # Due to the autogenerated structure of the rss feed the field data is
        # offset by 4 elements from field_name in the passed presentation

        item_presentation_offset = 4
        for i, element in enumerate(presentation):
            if field_name in element:

                # data in element is in unicode, we want an error raised if
                # there are characters that we are not expecting

                field_data = unicode(presentation[i + item_presentation_offset])

                return strip_tags(field_data).strip()
