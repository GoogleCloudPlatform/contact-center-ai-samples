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
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import {QueryPrincipal} from './QueryPrincipal';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import {InvertMenuSwitchesCheckbox} from './InvertMenuSwitchesCheckbox.js';
import {ShowServicesPanelCheckbox} from './ShowServicesPanelCheckbox.js';
import {QueryToggleAsset} from './AssetPollToggle.js';
import Paper from '@mui/material/Paper';

function SettingsField(props) {
  const projectDataField = props.projectDataField;
  const colorField = props.colorField;

  function onChange(e) {
    props.dataModel.projectData[projectDataField].set(e.target.value);
    props.dataModel[colorField].set('primary');
  }
  const shrink = !(
    props.dataModel.projectData[projectDataField].current === null ||
    props.dataModel.projectData[projectDataField].current === '' ||
    typeof props.dataModel.projectData[projectDataField].current === 'undefined'
  );

  function keyPress(e) {
    if (e.keyCode === 13) {
      props.dataModel.refetchAssetStatus.set(true);
    }
  }

  return (
    <TextField
      sx={props.sx ? props.sx : {mx: 2, width: 350}}
      label={props.label}
      variant="outlined"
      value={
        props.dataModel.projectData[projectDataField].current === null ||
        typeof props.dataModel.projectData[projectDataField].current ===
          'undefined'
          ? ''
          : props.dataModel.projectData[projectDataField].current
      }
      onChange={onChange}
      onKeyDown={keyPress}
      placeholder={''}
      InputProps={{spellCheck: 'false'}}
      disabled={props.dataModel.terraformLocked.current}
      color={props.dataModel[colorField].current}
      InputLabelProps={{
        shrink: shrink,
      }}
      focused={props.dataModel[colorField].current === 'error' ? true : false}
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
  useEffect(
    () => {
      props.dataModel.refetchAssetStatus.set(true);
    },
    /* eslint-disable react-hooks/exhaustive-deps */
    []
    /* eslint-enable react-hooks/exhaustive-deps */
  );
  return (
    <div>
      <Grid container rowSpacing={2} direction="column" sx={{py: 2}}>
        <Grid item justifyContent="flex-start" alignItems="center">
          <QueryPrincipal dataModel={props.dataModel} />
        </Grid>
        <Grid item justifyContent="flex-start" alignItems="center">
          <SettingsField
            label="Project ID"
            dataModel={props.dataModel}
            projectDataField={'project_id'}
            colorField={'projectIdColor'}
          />
        </Grid>
        <Grid item justifyContent="flex-start" alignItems="center">
          <RegionField label="Region" dataModel={props.dataModel} />
        </Grid>
        <Grid item justifyContent="flex-start" alignItems="center">
          <SettingsField
            label="Access Policy Title"
            dataModel={props.dataModel}
            projectDataField={'accessPolicyTitle'}
            colorField={'accessPolicyTitleColor'}
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
