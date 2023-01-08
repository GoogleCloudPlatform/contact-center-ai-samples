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

import React from 'react';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import {styled} from '@mui/material/styles';
import {
  ExecuteToggleStatus,
  QueryPollStatus,
  TIMER_SCALE,
} from './StatusPollToggle.js';
import {StatusTutorialMode, ToggleStatusTutorialMode} from './TutorialMode.js';
import Typography from '@mui/material/Typography';
import {getPage} from './DataModel.js';

const Item = styled(Paper)(({theme}) => ({
  ...theme.typography.body2,
  padding: 0,
  textAlign: 'right',
  color: theme.palette.text.secondary,
}));

function getControlElem(
  title,
  state,
  timeout,
  blocked_by_timeout,
  queryEndpoint,
  toggleEndpoint,
  blocked_by,
  liveMode,
  dataModel,
  pageMapper,
  pageNumber
) {
  let statusElem;
  let toggleStatusElem;
  if (liveMode) {
    statusElem = (
      <QueryPollStatus
        state={state}
        endpoint={queryEndpoint}
        timeout={timeout * TIMER_SCALE}
        blocked_by={blocked_by}
        blocked_by_timeout={blocked_by_timeout * TIMER_SCALE}
        dataModel={dataModel}
      />
    );
    toggleStatusElem = (
      <ExecuteToggleStatus
        state={state}
        endpoint={toggleEndpoint}
        timeout={timeout * TIMER_SCALE}
        blocked_by={blocked_by}
        blocked_by_timeout={blocked_by_timeout * TIMER_SCALE}
        dataModel={dataModel}
        pageMapper={pageMapper}
        pageNumber={pageNumber}
      />
    );
  } else {
    statusElem = <StatusTutorialMode state={state} />;
    toggleStatusElem = <ToggleStatusTutorialMode state={state} />;
  }

  return (
    <Grid container direction="row" columnSpacing={3} alignItems="center">
      <Grid item>
        <Item sx={{my: 0}} variant="string">
          {toggleStatusElem}
        </Item>
      </Grid>
      <Grid item sx={{width: 335}}>
        <Typography variant="body1" align="right">
          {title}
        </Typography>
      </Grid>
      <Grid item>{statusElem}</Grid>
    </Grid>
  );
}

function StateChangeButtonGrid(props) {
  const webhookAccessState = props.dataModel.allStates.webhookAccessState;
  const webhookIngressState = props.dataModel.allStates.webhookIngressState;
  const cloudfunctionsRestrictedState =
    props.dataModel.allStates.cloudfunctionsRestrictedState;
  const dialogflowRestrictedState =
    props.dataModel.allStates.dialogflowRestrictedState;
  const serviceDirectoryWebhookState =
    props.dataModel.allStates.serviceDirectoryWebhookState;
  const pageMapper = props.dataModel.pageMapper;
  const pageNumber = props.dataModel.pageNumber;
  const liveMode = props.liveMode;
  const dataModel = props.dataModel;

  let connectionEnabled;
  let extraGridItem;
  if (!liveMode) {
    if (
      getPage(dataModel.allStates, dataModel.pageMapper).connectionEnabled ===
      true
    ) {
      connectionEnabled = (
        <Grid item>
          <div style={{color: '#73DC54'}}>Yes</div>
        </Grid>
      );
    } else if (
      getPage(dataModel.allStates, dataModel.pageMapper).connectionEnabled ===
      false
    ) {
      connectionEnabled = (
        <Grid item>
          <div style={{color: 'red'}}>{'No'}</div>
        </Grid>
      );
    } else {
      connectionEnabled = 'TODO';
    }
    extraGridItem = (
      <Grid item>
        <Grid container direction="row" columnSpacing={3} alignItems="center">
          <Grid item>
            <Box sx={{my: 0, width: 58}} variant="string" />
          </Grid>
          <Grid item sx={{width: 335}}>
            <Typography variant="body1" align="right">
              Can Dialogflow contact Cloud Functions?
            </Typography>
          </Grid>
          {connectionEnabled}
        </Grid>
      </Grid>
    );
  } else {
    extraGridItem = <></>;
  }

  return (
    <>
      <Grid container direction="column" rowSpacing={1}>
        <Grid item>
          {getControlElem(
            'Webhook Access Authenticated Only?',
            webhookAccessState,
            3,
            110,
            '/webhook_access_allow_unauthenticated_status',
            '/update_webhook_access',
            cloudfunctionsRestrictedState,
            liveMode,
            dataModel,
            pageMapper,
            pageNumber
          )}
        </Grid>

        <Grid item>
          {getControlElem(
            'Restrict Cloudfunctions Access (VPC-SC)?',
            cloudfunctionsRestrictedState,
            15,
            null,
            '/restricted_services_status_cloudfunctions',
            '/update_security_perimeter_cloudfunctions',
            null,
            liveMode,
            dataModel,
            pageMapper,
            pageNumber
          )}
        </Grid>

        <Grid item>
          {getControlElem(
            'Restrict Dialogflow Access (VPC-SC)?',
            dialogflowRestrictedState,
            15,
            null,
            '/restricted_services_status_dialogflow',
            '/update_security_perimeter_dialogflow',
            null,
            liveMode,
            dataModel,
            pageMapper,
            pageNumber
          )}
        </Grid>

        <Grid item>
          {getControlElem(
            'Webhook Allow Internal Ingress Only?',
            webhookIngressState,
            85,
            110,
            '/webhook_ingress_internal_only_status',
            '/update_webhook_ingress',
            cloudfunctionsRestrictedState,
            liveMode,
            dataModel,
            pageMapper,
            pageNumber
          )}
        </Grid>

        <Grid item>
          {getControlElem(
            'Route Dialogflow Through VPC Proxy?',
            serviceDirectoryWebhookState,
            8,
            110,
            '/service_directory_webhook_fulfillment_status',
            '/update_service_directory_webhook_fulfillment',
            dialogflowRestrictedState,
            liveMode,
            dataModel,
            pageMapper,
            pageNumber
          )}
        </Grid>

        {extraGridItem}
      </Grid>
    </>
  );
}

export {StateChangeButtonGrid};
