from contextlib import ExitStack
from dataclasses import dataclass, field
from typing import Mapping

import mock
import pytest
import test_case_delegator as tcd
from google.api_core.operation import Operation
from google.cloud.dialogflowcx import (
    Agent,
    ConversationTurn,
    Flow,
    Intent,
    Page,
    RunTestCaseResponse,
    TestCase,
    TestCaseResult,
    TestResult,
    TestRunDifference,
    Webhook,
)


@dataclass
class RequestMock:
    payload: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def get_json(self) -> Mapping:
        return self.payload


def patch_client(client, method_name, stack, return_value=None):
    stack.enter_context(
        mock.patch.object(
            client,
            method_name,
            return_value=return_value,
        )
    )


hermetic_test_cases = (
    ([TestRunDifference(description="XFAIL")], TestResult.FAILED, True),
    ([TestRunDifference(description="XFAIL")], TestResult.PASSED, True),
    ([], TestResult.FAILED, True),
    ([], TestResult.PASSED, False),
)


def run_hermetic_test(sample, differences, test_result, xfail):
    sample.TEST_CASES = {
        "Test Case 0": {
            "input_text": "MOCK_INPUT_TEXT",
            "expected_response_text": ["MOCK_EXPECTED_RESPONSE_TEXT"],
        },
    }
    with ExitStack() as stack:
        patch_client(
            sample.agent_delegator.client,
            "create_agent",
            stack,
            return_value=Agent(name="MOCK_AGENT_NAME"),
        )
        patch_client(
            sample.webhook_delegator.client,
            "create_webhook",
            stack,
            return_value=Webhook(name="MOCK_WEBHOOK_NAME"),
        )
        patch_client(
            sample.intent_delegator.client,
            "create_intent",
            stack,
            return_value=Intent(name="MOCK_INTENT_NAME"),
        )
        patch_client(
            sample.page_delegator.client,
            "create_page",
            stack,
            return_value=Page(name="MOCK_PAGE_NAME"),
        )
        patch_client(
            sample.start_flow_delegator.client,
            "get_flow",
            stack,
            return_value=Flow(name="MOCK_FLOW_NAME"),
        )
        patch_client(sample.page_delegator.client, "update_page", stack)
        patch_client(sample.start_flow_delegator.client, "update_flow", stack)
        patch_client(sample.page_delegator.client, "delete_page", stack)
        patch_client(sample.intent_delegator.client, "delete_intent", stack)
        patch_client(sample.webhook_delegator.client, "delete_webhook", stack)
        patch_client(sample.agent_delegator.client, "delete_agent", stack)
        for test_case_delegator in sample.test_case_delegators.values():
            patch_client(
                test_case_delegator.client,
                "create_test_case",
                stack,
                return_value=TestCase(
                    name="MOCK_TEST_CASE_NAME",
                    display_name="MOCK_TEST_CASE_DISPLAY_NAME",
                ),
            )
            patch_client(test_case_delegator.client, "batch_delete_test_cases", stack)

            def result():
                return RunTestCaseResponse(
                    result=TestCaseResult(
                        test_result=test_result,
                        conversation_turns=[
                            ConversationTurn(
                                virtual_agent_output=ConversationTurn.VirtualAgentOutput(
                                    differences=differences
                                )
                            )
                        ],
                    )
                )

            lro = mock.create_autospec(Operation, instance=True, spec_set=True)
            lro.result = result
            patch_client(
                test_case_delegator.client, "run_test_case", stack, return_value=lro
            )
        sample.initialize()
        for test_case_delegator in sample.test_case_delegators.values():
            if xfail:
                with pytest.raises(tcd.DialogflowTestCaseFailure):
                    test_case_delegator.run_test_case(wait=0)
            else:
                test_case_delegator.run_test_case(wait=0)
        sample.tear_down()


def yield_sample(sample):
    sample.initialize()
    yield sample
    sample.tear_down()
    del sample
