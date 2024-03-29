#!/usr/bin/python2.5
#
# Copyright 2011 Google Inc.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Parser for iCalendar file data."""

__author__ = "dwightguth@google.com (Dwight Guth)"

import datetime
import logging

import vobject

import model


class Parser(object):
  """Parses VTODO components into App Engine datastore entities."""

  def __init__(self, tasklist):
    """Creates a new Parser object.

    Args:
      tasklist: the tasklist datastore entity to put the parsed tasks into.
    """

    self.tasklist = tasklist

  def ParseAndStore(self, vcal_data):
    """Parses the provided data and stores the resulting entities.

    Args:
      vcal_data: the text of an ics file to be parsed for todo objects.

    Returns:
      The list of entities created by parsing vcal_data.
    """
    vcal = vobject.readOne(vcal_data)
    results = []

    for todo in vcal.components():
      results.append(self.ParseItem(todo))
    return results

  def ParseItem(self, item):
    """Parses a single VTODO object and stores the resulting entity.

    Args:
      item: an icalendar object representing a VTODO object.

    Returns:
      The entity created by parsing item.
    """

    logging.info(item)

    task = model.Task()
    if self.tasklist:
      task.parent_entity = self.tasklist
    if "summary" in item.contents:
      task.title = item.summary.value
    else:
      # we need a title so if it's not there we use the empty string
      task.title = ""
    if "description" in item.contents:
      task.notes = item.description.value
    if "due" in item.contents:
      due = item.due.value
      if isinstance(due, datetime.datetime):
        task.due = due.date()
      elif isinstance(due, datetime.date):
        task.due = due
    if "completed" in item.contents:
      # we don't use the status field because iCalendar doesn't always specify
      # it on completed tasks
      task.status = "completed"
      task.completed = item.completed.value
    else:
      task.status = "needsAction"
    task.put()
    return task
