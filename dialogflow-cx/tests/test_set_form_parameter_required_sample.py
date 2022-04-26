# Copyright 2022 Google LLC
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

"""Dialogflow CX sample: Setting a session parameter with a webhook."""


import pytest
from utilities import create_conversational_turn


@pytest.mark.integration
@pytest.mark.flaky(max_runs=3, reruns_delay=5)
def test_set_session_param_sample_not_required(set_form_parameter_required_sample):
    """Test the SetSessionParamSample test cases."""
    is_webhook_enabled = True
    test_case_conversation_turns = [
        create_conversational_turn(
            "trigger intent",
            ["Entering Main Page"],
            set_form_parameter_required_sample.intent_delegator_main_page.intent,
            set_form_parameter_required_sample.page_delegator.page,
            is_webhook_enabled,
        ),
    ]
    expected_session_parameters = [{"name": "UNKNOWN", "age": 25.0}]
    test_case = set_form_parameter_required_sample.create_test_case(
        "Test Case 0",
        test_case_conversation_turns,
    )
    set_form_parameter_required_sample.run_test_case(
        test_case, expected_session_parameters
    )


@pytest.mark.integration
@pytest.mark.flaky(max_runs=2, reruns_delay=5)
def test_set_session_param_sample_required(set_form_parameter_required_sample):
    """Test the SetSessionParamSample test cases."""

    responses = set_form_parameter_required_sample.run(
        ["set form parameter age as required.", "trigger intent"], quiet=True
    )
    assert responses == [
        {
            "replies": ["TRIGGERED", "Form parameter age set as required"],
            "parameters": {},
        },
        {
            "replies": ["Entering Main Page", "What is your age?"],
            "parameters": {"name": "UNKNOWN"},
        },
    ]
