# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module to test Terraform module graph."""

import networkx as nx
import pygraphviz as pgv
import pytest

GRAPH = nx.nx_agraph.from_agraph(pgv.AGraph("dependencies.dot"))


class Resource:  # pylint: disable=too-few-public-methods
    """Class to provide a readable interface to check dependencies."""

    def __init__(self, name):
        self.name = name

    def depends_on(self, other):
        """Check if a resource depends on another resource."""
        return other.name in nx.descendants(GRAPH, self.name)


@pytest.fixture
def dialogflow_intent():
    """Resource fixture"""
    return Resource("[root] google_dialogflow_cx_intent.order_new (expand)")


@pytest.fixture
def dialogflow_entity_type():
    """Resource fixture"""
    return Resource("[root] google_dialogflow_cx_entity_type.size (expand)")


def test_reverse_proxy(
    dialogflow_intent, dialogflow_entity_type
):  # pylint: disable=redefined-outer-name
    """Test if Dialogflow intent depends on the entity type."""
    assert dialogflow_intent.depends_on(dialogflow_entity_type)
