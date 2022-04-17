class DialogflowSample:
    """Base class for samples"""

    def set_auth_delegator(self, auth_delegator):
        self._auth_delegator = auth_delegator

    def set_agent_delegator(self, agent_delegator):
        self._agent_delegator = agent_delegator

    @property
    def auth_delegator(self):
        return self._auth_delegator

    @property
    def agent_delegator(self):
        return self._agent_delegator

    @property
    def project_id(self):
        return self.auth_delegator.project_id

    @property
    def location(self):
        return self.auth_delegator.location

    @property
    def start_flow(self):
        return self.agent_delegator.start_flow

    def run(self):
        for test_case_delegator in self.test_case_delegators.values():
            if not test_case_delegator.expected_exception:
                test_case_delegator.run_test_case()
