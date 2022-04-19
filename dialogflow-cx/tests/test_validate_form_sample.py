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

"""Dialogflow CX form validation webhook sample unit tests."""


import pytest
from utilities import create_conversational_turn, run_hermetic_test
from validate_form_sample import ValidateFormSample
import dialogflow_sample as ds


@pytest.fixture(name='sample', scope="session")
def fixture_sample(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all ValidateFormSample tests."""
    sample = ValidateFormSample(
        agent_display_name=f"ValidateFormSample (test session {session_uuid})",
        project_id=project_id,
        quota_project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.setup()
    yield sample
    # sample.tear_down()
    del sample


@pytest.mark.integration
@pytest.mark.parametrize("display_name,user_input,exception", [
    ('validate_form_sample', '22', None),
    # ('validate_form_sample_xfail', 'XFAIL', ds.UnexpectedResponseFailure),
])
def test_validate_form_sample(display_name, user_input, exception, sample):
    """Test the ValidateFormSample test cases."""
    is_webhook_enabled = True
    test_case_conversation_turns = [
        create_conversational_turn(
            'trigger intent',
            ['Entering Main Page', 'What is your age?'],
            sample.intent_delegator.intent,
            sample.page_delegator.page,
            is_webhook_enabled,
        ),
        create_conversational_turn(
            user_input,
            ['Form Filled', 'Valid age'],
            None,
            sample.start_page_delegator.page,
            is_webhook_enabled,
        ),
    ]
    test_case = sample.create_test_case(display_name, test_case_conversation_turns)
    if exception:
        with pytest.raises(exception):
            sample.run_test_case(test_case)    
    else:
        sample.run_test_case(test_case)


@pytest.mark.hermetic
def test_basic_webhook_sample_hermetic():
    """Test the ValidateFormSample test cases with mocked API interactions."""
    sample = ValidateFormSample(
        agent_display_name="MOCK_AGENT_DISPLAY_NAME",
        project_id=-1,
        webhook_uri="MOCK_WEBHOOK_URI",
    )
    run_hermetic_test(sample)
