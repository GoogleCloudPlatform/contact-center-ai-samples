// Copyright 2023 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, {useEffect} from 'react';
import axios from 'axios';
import {QueryClient, QueryClientProvider, useQuery} from 'react-query';

function RegisterSetActivePage(props) {
  function queryFunction() {
    return axios
      .post(
        props.endpoint,
        {
          current_page: props.dataModel.activePage.current,
        },
        {}
      )
      .then(res => res.data);
  }

  const {refetch} = useQuery(props.endpoint, queryFunction, {
    retry: false,
    enabled: false,
  });

  useEffect(
    () => {
      refetch();
    },
    /* eslint-disable react-hooks/exhaustive-deps */
    [props.dataModel.activePage.current]
    /* eslint-enable react-hooks/exhaustive-deps */
  );
}

function QueryRegisterSetActivePage(props) {
  const queryClient = new QueryClient();
  return (
    <div>
      <QueryClientProvider client={queryClient}>
        <RegisterSetActivePage
          endpoint="/register_set_active_page"
          dataModel={props.dataModel}
        />
      </QueryClientProvider>
    </div>
  );
}

export {QueryRegisterSetActivePage};
