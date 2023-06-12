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
import Typography from '@mui/material/Typography';
import {StateChangeButtonGrid} from './StateButtonGrid.js';
import {StateImage} from './StateSlides.js';
import {AssetStatusPanel} from './AssetStatusPanel.js';
import {SettingsPanelWithSpinner} from './SettingsPanel.js';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import {QueryPollAssetStatus} from './AssetPollToggle.js';
import Divider from '@mui/material/Divider';
import {LiveDemoPrerequisites} from './LiveDemoPrerequisites.js';
import {TutorialPageIntroduction} from './TutorialPageIntroduction.js';
import {TutorialPageTabs} from './TutorialPageTabs.js';
import {HomePage} from './HomePage.js';
import {PrivacyPolicyPage} from './PrivacyPolicy.js';

function StateButtonGridAndImage(props) {
  return (
    <Grid
      container
      direction="row"
      columnSpacing={3}
      alignItems="center"
      justifyContent="center"
    >
      <Grid item>
        <StateChangeButtonGrid
          dataModel={props.dataModel}
          liveMode={props.liveMode}
        />
      </Grid>
      <Grid item>
        <StateImage dataModel={props.dataModel} />
      </Grid>
    </Grid>
  );
}

function TutorialPage(props) {
  return (
    <>
      <TutorialPageIntroduction />
      <TutorialPageTabs dataModel={props.dataModel} />
      <StateButtonGridAndImage dataModel={props.dataModel} liveMode={false} />
    </>
  );
}

function LiveDemoPage(props) {
  return (
    <>
      <LiveDemoPrerequisites dataModel={props.dataModel} />
      <Divider sx={{my: 2}} orientation="horizontal" flexItem />
      <QueryPollAssetStatus dataModel={props.dataModel} />
      <Typography variant="h4" sx={{mx: 3, my: 3}} id="statusDashboard">
        Status Dashboard
      </Typography>
      <StateButtonGridAndImage dataModel={props.dataModel} liveMode={true} />
      <Divider sx={{my: 2}} orientation="horizontal" flexItem />
      <Typography variant="h4" sx={{mx: 3, my: 3}} id="deploymentDashboard">
        Deployment Dashboard
      </Typography>
      <Grid container direction="row">
        <Grid item>
          <SettingsPanelWithSpinner dataModel={props.dataModel} />
        </Grid>
        <Grid item>
          <AssetStatusPanel dataModel={props.dataModel} />
        </Grid>
      </Grid>
    </>
  );
}

function LoginRedirectPage() {
  return (
    <>
      <Typography variant="h5" sx={{my: 3}}>
        Redirecting to Login Page
      </Typography>
      <CircularProgress size={100} thickness={10} />
    </>
  );
}

function PageContent(props) {
  const targetPage = props.activePage;
  if (props.dataModel.loginRedirect.current) {
    return <LoginRedirectPage />;
  }
  if (targetPage === 'home') {
    return <HomePage dataModel={props.dataModel} />;
  } else if (targetPage === 'tutorial') {
    return <TutorialPage dataModel={props.dataModel} />;
  } else if (targetPage === 'liveDemo') {
    return <LiveDemoPage dataModel={props.dataModel} />;
  } else if (targetPage === 'privacyPolicy') {
    return <PrivacyPolicyPage dataModel={props.dataModel} />;
  } else if (typeof targetPage === 'undefined') {
    return <HomePage dataModel={props.dataModel} />;
  }
}

export {PageContent};
