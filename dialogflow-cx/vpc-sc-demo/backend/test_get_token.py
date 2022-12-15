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

import pytest
import get_token


@pytest.fixture
def lru_fixture():
    return lambda x: x


def test_LRU_cache_bump_out(lru_fixture):
    max_size, test_size,  = 5, 15
    for curr_val in range(test_size):
        assert lru_fixture(curr_val) == curr_val

    cache = get_token.LRU(lru_fixture, max_size=max_size)
    for curr_val in range(max_size):
        assert cache(curr_val) == curr_val
    assert set(cache.cache.keys()) == {(val,) for val in range(max_size)}
    for curr_val in range(max_size, test_size):
        assert cache(curr_val) == curr_val
    assert set(cache.cache.keys()) == {(val,) for val in range(test_size-max_size, test_size)}


def test_LRU_cache_reuse(lru_fixture):
    mock_val = 10
    cache = get_token.LRU(lru_fixture, max_size=1)
    first_val = cache(mock_val)
    second_val = cache(mock_val)
    assert first_val == second_val == mock_val
    assert len(cache.cache) == 1


def get_token_from_auth_server():
    
