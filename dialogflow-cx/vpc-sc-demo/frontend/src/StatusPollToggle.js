// Copyright 2022 Google LLC
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

import React, {useEffect, useRef} from 'react';
import {QueryClient, QueryClientProvider, useQuery} from 'react-query';
import axios from 'axios';
import Switch from '@mui/material/Switch';
import CircularProgress from '@mui/material/CircularProgress';
import {getPage} from './DataModel.js';
import {handleTokenExpired, getBucket} from './Utilities.js';
import Typography from '@mui/material/Typography';

const TIMER_SCALE = 10;

function ToggleStatus(props) {
  const changeRequested = useRef(false);
  const updatePageNumber = useRef(false);
  const disabled = useRef(false);

  const {isFetching, refetch} = useQuery(
    props.endpoint,
    () =>
      axios
        .post(
          props.endpoint,
          {status: !props.state.status.current},
          {
            params: {
              project_id: props.dataModel.projectData.project_id.current,
              bucket: getBucket(props.dataModel),
              region: props.dataModel.projectData.region.current,
              webhook_name: props.dataModel.projectData.webhook_name.current,
              access_policy_title:
                props.dataModel.projectData.accessPolicyTitle.current,
            },
          }
        )
        .then(res => res.data),
    {
      enabled: false,
    }
  );

  useEffect(() => {
    const interval = setInterval(() => {
      props.state.timeSinceSliderClick.set(val => val + 1);
    }, 1000.0 / TIMER_SCALE);
    return () => clearInterval(interval);
  }, [props.state]);

  useEffect(() => {
    if (updatePageNumber.current) {
      const newPageNumber = getPage(
        props.dataModel.allStates,
        props.pageMapper
      ).page;
      props.pageNumber.set(newPageNumber);
      updatePageNumber.current = false;
    }
  });

  useEffect(() => {
    if (changeRequested.current) {
      props.state.status.set(!props.state.status.current);
      updatePageNumber.current = true;
      changeRequested.current = false;
      props.state.timeSinceSliderClick.set(0);
    }

    if (
      isFetching ||
      (props.blocked_by &&
        props.blocked_by.timeSinceSliderClick.current <
          props.blocked_by_timeout)
    ) {
      props.state.isUpdating.set(true);
    } else {
      if (props.state.timeSinceSliderClick.current > props.timeout - 1) {
        props.state.isUpdating.set(false);
      }
    }
  });

  function onChange() {
    changeRequested.current = true;
    refetch();
  }

  useEffect(() => {
    if (
      props.state.isUpdating.current ||
      props.state.blocked.current ||
      props.dataModel.projectData.project_id.current === null ||
      !props.dataModel.loggedIn.current ||
      props.dataModel.terraformLocked.current
    ) {
      disabled.current = true;
    } else {
      disabled.current = false;
    }
  });

  return (
    <>
      {
        <Switch
          onChange={onChange}
          checked={
            typeof props.state.status.current === 'boolean'
              ? props.state.status.current
              : false
          }
          style={{visibility: disabled.current ? 'hidden' : 'visible'}}
        />
      }
    </>
  );
}

function ExecuteToggleStatus(props) {
  const queryClient = new QueryClient();
  return (
    <div>
      <QueryClientProvider client={queryClient}>
        <ToggleStatus
          state={props.state}
          endpoint={props.endpoint}
          timeout={props.timeout}
          blocked_by={props.blocked_by}
          blocked_by_timeout={props.blocked_by_timeout}
          dataModel={props.dataModel}
          pageMapper={props.pageMapper}
          pageNumber={props.pageNumber}
        />
      </QueryClientProvider>
    </div>
  );
}

function PollStatus(props) {
  const completed = useRef(false);

  function onSuccess() {
    completed.current = true;
  }
  function queryFunction() {
    return axios
      .get(props.endpoint, {
        params: {
          project_id: props.dataModel.projectData.project_id.current,
          bucket: getBucket(props.dataModel),
          region: props.dataModel.projectData.region.current,
          webhook_name: props.dataModel.projectData.webhook_name.current,
          access_policy_title:
            props.dataModel.projectData.accessPolicyTitle.current,
        },
      })
      .then(res => res.data);
  }

  const enabled =
    props.state.isUpdating.current ||
    props.dataModel.projectData.project_id.current === '' ||
    props.dataModel.projectData.project_id.current === null ||
    typeof props.dataModel.validProjectId.current !== 'boolean' ||
    props.dataModel.validProjectId.current === false ||
    props.dataModel.loggedIn.current === false ||
    props.dataModel.terraformLocked.current
      ? false
      : true;
  const {data} = useQuery(props.endpoint, queryFunction, {
    refetchInterval: 10000,
    onSuccess: onSuccess,
    retry: false,
    enabled: enabled,
  });

  useEffect(() => {
    if (data && completed.current) {
      completed.current = false;
      props.state.status.set(data.status);
      if (data.status === 'BLOCKED') {
        props.state.blocked.set(true);
        if (
          data.reason === 'POLICY_NOT_FOUND' ||
          data.reason === 'NO_ACCESS_POLICY'
        ) {
          props.state.status.set(false);
        } else if (
          (data.reason === 'TOKEN_EXPIRED') &
          props.dataModel.loggedIn.current &
          !props.dataModel.sessionExpiredModalOpen.current
        ) {
          handleTokenExpired(props.dataModel);
        }
      } else {
        props.state.blocked.set(false);
      }
    }
  });

  if (props.dataModel.terraformLocked.current) {
    return (
      <Typography variant="body2" align="right" style={{color: 'red'}}>
        {'Blocked: TERRAFORM_UPDATING'}
      </Typography>
    );
  } else if (props.state.isUpdating.current) {
    let remainingTimeBlocker = 0;
    if (props.blocked_by) {
      remainingTimeBlocker = Math.max(
        0,
        props.blocked_by_timeout -
          1 -
          props.blocked_by.timeSinceSliderClick.current
      );
    }
    const remainingTime = Math.max(
      Math.max(0, props.timeout - 1 - props.state.timeSinceSliderClick.current),
      remainingTimeBlocker
    );
    if (remainingTime > 0) {
      // console.log(props.blocked_by_timeout, props.timeout)
      let startTime;
      if (remainingTimeBlocker > 0) {
        startTime = Math.max(props.blocked_by_timeout - 1, props.timeout - 1);
      } else {
        startTime = props.timeout - 1;
      }
      // console.log('remainingTime', remainingTime, startTime, remainingTime/startTime, 100.0*(remainingTime/startTime))
      return (
        <CircularProgress
          size={20}
          variant={'determinate'}
          value={100.0 * (remainingTime / startTime)}
        />
      );
    }
    return <CircularProgress size={20} />;
  } else if (props.state.blocked.current && data.status === 'BLOCKED') {
    return (
      <Typography variant="body2" align="right" style={{color: 'red'}}>
        {`Blocked: ${data.reason}`}
      </Typography>
    );
  } else if (!props.dataModel.loggedIn.current) {
    return <div style={{color: 'red'}}>{'Blocked: LOGIN_REQUIRED'}</div>;
  } else {
    // console.log(props.state.blocked.current)
    return <div>{props.state.status.current ? 'True' : 'False'}</div>;
  }
}

function QueryPollStatus(props) {
  const queryClient = new QueryClient();
  return (
    <div>
      <QueryClientProvider client={queryClient}>
        <PollStatus
          state={props.state}
          endpoint={props.endpoint}
          timeout={props.timeout}
          blocked_by={props.blocked_by}
          blocked_by_timeout={props.blocked_by_timeout}
          dataModel={props.dataModel}
        />
      </QueryClientProvider>
    </div>
  );
}

export {ExecuteToggleStatus, QueryPollStatus, TIMER_SCALE};
