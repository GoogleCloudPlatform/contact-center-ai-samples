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

import React, {useEffect} from 'react';
import {QueryClient, QueryClientProvider, useQuery} from 'react-query';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import {QueryPrincipal} from './QueryPrincipal';
import axios from 'axios';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import {InvertMenuSwitchesCheckbox} from './InvertMenuSwitchesCheckbox.js';
import {ShowServicesPanelCheckbox} from './ShowServicesPanelCheckbox.js';
import {QueryToggleAsset} from './AssetPollToggle.js';
import Paper from '@mui/material/Paper';
import {handleTokenExpired} from './Utilities.js';

function ProjectIdInputField(props) {
  function queryFunction() {
    return axios
      .get('/validate_project_id', {
        params: {
          project_id: props.dataModel.projectData.project_id.current,
        },
      })
      .then(res => res.data);
  }

  const {data} = useQuery(
    ['/validate_project_id', props.dataModel.projectData.project_id.current],
    queryFunction,
    {
      enabled: props.dataModel.loggedIn.current === true,
      retry: false,
    }
  );

  function onChange(e) {
    props.dataModel.projectData.project_id.set(e.target.value);
  }

  useEffect(() => {
    if (data) {
      if (
        (data.status === 'BLOCKED') &
        (data.reason === 'TOKEN_EXPIRED') &
        props.dataModel.loggedIn.current &
        !props.dataModel.sessionExpiredModalOpen.current
      ) {
        handleTokenExpired(props.dataModel);
      } else {
        props.dataModel.validProjectId.set(data.status);
      }
    }
  });

  const textFieldColor = props.dataModel.validProjectId.current
    ? 'primary'
    : 'error';
  return (
    <TextField
      sx={props.sx ? props.sx : {mx: 2, width: 350}}
      label={props.label}
      variant="outlined"
      value={props.dataModel.projectData.project_id.current}
      onChange={onChange}
      placeholder={props.label}
      InputProps={{spellCheck: 'false'}}
      color={textFieldColor}
    />
  );
}

function AccessPolicyField(props) {
  function onChange(e) {
    props.dataModel.projectData.accessPolicyTitle.set(e.target.value);
  }
  return (
    <TextField
      sx={props.sx ? props.sx : {mx: 2, width: 350}}
      label={props.label}
      variant="outlined"
      value={
        props.dataModel.projectData.accessPolicyTitle.current === null
          ? ''
          : props.dataModel.projectData.accessPolicyTitle.current
      }
      onChange={onChange}
      placeholder={''}
      InputProps={{spellCheck: 'false'}}
      disabled={props.dataModel.terraformLocked.current}
      color="primary"
      InputLabelProps={{
        shrink: props.dataModel.projectData.accessPolicyTitle.current,
      }}
    />
  );
}

function RegionField(props) {
  return (
    <TextField
      sx={props.sx ? props.sx : {mx: 2, width: 350}}
      label={props.label}
      variant="outlined"
      value={props.dataModel.projectData.region.current}
      placeholder={props.label}
      InputProps={{spellCheck: 'false'}}
      disabled={true}
      color="primary"
    />
  );
}

function SettingsPanel(props) {
  const queryClient = new QueryClient();
  return (
    <div>
      <Grid container rowSpacing={2} direction="column" sx={{py: 2}}>
        <Grid item justifyContent="flex-start" alignItems="center">
          <QueryPrincipal dataModel={props.dataModel} />
        </Grid>
        <Grid item justifyContent="flex-start" alignItems="center">
          <QueryClientProvider client={queryClient}>
            <ProjectIdInputField
              label="Project ID"
              dataModel={props.dataModel}
            />
          </QueryClientProvider>
        </Grid>
        <Grid item justifyContent="flex-start" alignItems="center">
          <RegionField label="Region" dataModel={props.dataModel} />
        </Grid>
        <Grid item justifyContent="flex-start" alignItems="center">
          <AccessPolicyField
            label="Access Policy Title"
            dataModel={props.dataModel}
          />
        </Grid>
      </Grid>
    </div>
  );
}

function RefreshStateSpinner(props) {
  if (props.dataModel.terraformLocked.current) {
    return (
      <Grid container direction="column" alignItems="center">
        <Grid item>
          <Typography variant="h6">Refreshing State...</Typography>
        </Grid>
        <Grid item>
          <CircularProgress size={100} thickness={10} />
        </Grid>
      </Grid>
    );
  } else {
    return <></>;
  }
}

function SettingsPanelWithSpinner(props) {
  return (
    <>
      <Grid
        container
        direction="column"
        justifyContent="space-between"
        alignItems="center"
        sx={{height: 622}}
      >
        <Grid item>
          <Grid container direction="row" sx={{pl: 2, width: 360}}>
            <Paper sx={{width: 350}} variant="string">
              <Grid
                container
                direction="row"
                justifyContent="space-between"
                sx={{pt: 2}}
              >
                <Grid item>
                  <Typography variant="h5">All Project Resources:</Typography>
                </Grid>
                <Grid item>
                  <QueryToggleAsset
                    target="all"
                    dataModel={props.dataModel}
                    enableAlert={true}
                    includeNameBox={true}
                    isModuleSwitch={true}
                  />
                </Grid>
              </Grid>
              <Grid
                container
                direction="row"
                justifyContent="space-between"
                alignItems="center"
              >
                <Typography variant="body1">Invert menu switches:</Typography>
                <InvertMenuSwitchesCheckbox
                  dataModel={props.dataModel}
                  sx={{pr: 2}}
                />
              </Grid>
              <Grid
                container
                direction="row"
                justifyContent="space-between"
                alignItems="center"
              >
                <Typography variant="body1">
                  Show &quot;APIs & Services&quot; panel:
                </Typography>
                <ShowServicesPanelCheckbox
                  dataModel={props.dataModel}
                  sx={{pr: 2}}
                />
              </Grid>
            </Paper>
            <Grid item sx={{pt: 3}}>
              <RefreshStateSpinner dataModel={props.dataModel} />
            </Grid>
          </Grid>
        </Grid>
        <Grid item>
          <SettingsPanel dataModel={props.dataModel} />
        </Grid>
      </Grid>
    </>
  );
}

export {SettingsPanelWithSpinner};
