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

"""Dialogflow CX webhook sample unit tests."""


import pytest
from basic_webhook_sample import BasicWebhookSample
from utilities import hermetic_test_cases, run_hermetic_test


@pytest.fixture(scope="session")
def webhook_sample(session_uuid, project_id, webhook_uri):
    sample = BasicWebhookSample(
        agent_display_name=f"BasicWebhookSample (test session {session_uuid})",
        project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.initialize()
    yield sample
    sample.tear_down()
    del sample


@pytest.mark.integration
@pytest.mark.flaky(max_runs=3, reruns_delay=15)
@pytest.mark.parametrize("test_case_display_name", BasicWebhookSample.TEST_CASES)
def test_basic_webhook_integration(test_case_display_name, webhook_sample):
    test_case_delegator = webhook_sample.test_case_delegators[test_case_display_name]
    if test_case_delegator.expected_exception:
        with pytest.raises(test_case_delegator.expected_exception):
            test_case_delegator.run_test_case()
    else:
        test_case_delegator.run_test_case(wait=10)


@pytest.mark.hermetic
@pytest.mark.parametrize("differences,test_result,xfail", hermetic_test_cases)
def test_basic_webhook_hermetic(differences, test_result, xfail):
    sample = BasicWebhookSample(
        agent_display_name="MOCK_AGENT_DISPLAY_NAME",
        project_id=-1,
        webhook_uri="MOCK_WEBHOOK_URI",
    )
    run_hermetic_test(sample, differences, test_result, xfail)
