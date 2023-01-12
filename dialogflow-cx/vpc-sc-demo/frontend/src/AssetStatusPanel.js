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
import {
  ServicesPanel,
  NetworkPanel,
  AgentPanel,
  ServiceDirectoryPanel,
  PANEL_WIDTH,
} from './AssetPollToggle.js';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';

function AssetStatusPanel(props) {
  const sx_1 = {
    height: 600,
    width: PANEL_WIDTH + 100,
    px: 1,
    py: 1,
    my: 1,
  };

  const sx_2 = {
    height: 292,
    width: PANEL_WIDTH + 100,
    px: 1,
    py: 1,
    my: 1,
  };

  let ServicesPanelObj;
  if (props.dataModel.showServicesPanel.current) {
    ServicesPanelObj = (
      <Grid item>
        <Paper variant="outlined" sx={sx_1}>
          <ServicesPanel dataModel={props.dataModel} />
        </Paper>
      </Grid>
    );
  } else {
    ServicesPanelObj = <></>;
  }

  return (
    <>
      <Grid container direction="row" columnSpacing={3} alignItems="flex-start">
        <Grid item>
          <Paper variant="outlined" sx={sx_1}>
            <NetworkPanel dataModel={props.dataModel} />
          </Paper>
        </Grid>

        <Grid item>
          <Grid container direction="column">
            <Grid item>
              <Paper variant="outlined" sx={sx_2}>
                <ServiceDirectoryPanel dataModel={props.dataModel} />
              </Paper>
            </Grid>
            <Grid item>
              <Paper variant="outlined" sx={sx_2}>
                <AgentPanel dataModel={props.dataModel} />
              </Paper>
            </Grid>
          </Grid>
        </Grid>

        {ServicesPanelObj}
      </Grid>
    </>
  );
}

export {AssetStatusPanel};
