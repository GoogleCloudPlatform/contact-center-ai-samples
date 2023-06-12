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
import axios from 'axios';
import {useState, useEffect, useRef} from 'react';
import PropTypes from 'prop-types';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import {QueryClient, QueryClientProvider, useQuery} from 'react-query';

function TabPanel(props) {
  const {children, value, index, ...other} = props;
  const didMountRef = useRef(false);

  function queryFunction() {
    return axios
      .post(
        props.analytics_endpoint,
        {
          current_tab: value,
        },
        {}
      )
      .then(res => res.data);
  }

  const {refetch} = useQuery(props.analytics_endpoint, queryFunction, {
    retry: false,
    enabled: false,
  });

  useEffect(
    () => {
      if (value === index && didMountRef.current) {
        refetch();
      }
      didMountRef.current = true;
    },
    /* eslint-disable react-hooks/exhaustive-deps */
    [value]
    /* eslint-enable react-hooks/exhaustive-deps */
  );

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{p: 3}}>{children}</Box>}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

function setStates(example, dataModel) {
  const PageStateMap = {
    0: [true, false, false, false, false],
    1: [true, false, true, true, false],
    2: [true, true, true, true, false],
    3: [true, true, false, false, true],
    4: [true, true, true, true, true],
  };
  const startingState = PageStateMap[example];
  dataModel.allStates['webhookAccessState'].status.set(startingState[0]);
  dataModel.allStates['webhookIngressState'].status.set(startingState[1]);
  dataModel.allStates['dialogflowRestrictedState'].status.set(startingState[2]);
  dataModel.allStates['cloudfunctionsRestrictedState'].status.set(
    startingState[3]
  );
  dataModel.allStates['serviceDirectoryWebhookState'].status.set(
    startingState[4]
  );
}

function securityLevelToRGB(securityIndex) {
  if (securityIndex === 0) {
    return <div style={{color: '#1D60F6'}}>Low</div>;
  }
  if (securityIndex === 1) {
    return <div style={{color: '#5DC83B'}}>Medium</div>;
  }
  if (securityIndex === 2) {
    return <div style={{color: '#F6C243'}}>High</div>;
  }
  if (securityIndex === 3) {
    return <div style={{color: '#EB3223'}}>Very High</div>;
  }
}

function TutorialTab(props) {
  const queryClient = new QueryClient();
  return (
    <div>
      <QueryClientProvider client={queryClient}>
        <TabPanel
          value={props.value}
          index={props.index}
          analytics_endpoint="/register_set_active_tutorial_tab"
        >
          <Grid container direction="row">
            <Grid item>
              <Typography variant="h5" sx={{my: 3}}>
                {props.title}
              </Typography>
            </Grid>
          </Grid>
          <Grid
            container
            direction="row"
            justifyContent="flex-start"
            spacing={2}
          >
            <Grid item sx={{width: '60%'}}>
              {props.body}
            </Grid>
            <Grid item>
              <Paper sx={{px: 2, py: 2}} elevation={2}>
                <Typography variant="body1">Security Level:</Typography>
                <Typography component={'span'} variant="body1" align="center">
                  {securityLevelToRGB(props.security)}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </QueryClientProvider>
    </div>
  );
}

function TutorialPageTabs(props) {
  const [value, setValue] = useState(0);

  /* eslint-disable react-hooks/exhaustive-deps */
  useEffect(() => {
    setStates(value, props.dataModel);
  }, []);
  /* eslint-enable react-hooks/exhaustive-deps */

  const handleChange = (event, newValue) => {
    setValue(newValue);
    setStates(newValue, props.dataModel);
  };

  const iamPermissions = (
    <Link
      target="_blank"
      href="https://cloud.google.com/functions/docs/concepts/iam"
      variant="body1"
    >
      identy and access management (IAM) permissions
    </Link>
  );

  const VPCServiceControls = (
    <Link
      target="_blank"
      href="https://cloud.google.com/vpc-service-controls/docs/overview"
      variant="body1"
    >
      VPC Service Controls
    </Link>
  );

  const ingressProtections = (
    <Link
      target="_blank"
      href="https://cloud.google.com/functions/docs/networking/network-settings#ingress_settings"
      variant="body1"
    >
      Cloud Functions ingress protections
    </Link>
  );

  const webhookServiceDirectory = (
    <Link
      target="_blank"
      href="https://cloud.google.com/dialogflow/cx/docs/concept/webhook#sd"
      variant="body1"
    >
      Service Directory for private network access
    </Link>
  );

  const exporingWebhooksBody = (
    <Typography paragraph sx={{ml: 2}}>
      If you are just starting out with Dialogflow Webhooks and Cloud Functions,
      it might make sense to at a minimum utilize {iamPermissions} to allow only
      authorized users to access your webhook and agent. Unauthenticated access
      to Dialogflow CX agents is not allowed, but is possible with Cloud
      Functions; removing allUsers principal in the Permissions menu will enable
      this first layer of security.
    </Typography>
  );

  const vpcscProtectionBody = (
    <div>
      <Typography paragraph sx={{ml: 2}}>
        When developing towards a production environment, {VPCServiceControls}{' '}
        offer an extra layer of security by providing security perimeters around
        the Dialogflow and Cloud Function APIs. These perimeters constrain data
        ingress and egress to prevent sensitive data from crossing through the
        open internet.
      </Typography>
      <Typography paragraph sx={{ml: 2}}>
        The Cloud Functions service perimeter does not fully disable access to
        the webhook. Authenticated users outside the VPC can still invoke the
        webhook, which might be benificial for development and testing, but
        leaves a security gap that needs to be closed through additional
        configuration before production. It does, however, provide additional
        security-through-obscurity by preventing all API access from outside the
        VPC, for example listing which cloud functions are available or
        modifying their configuration.
      </Typography>
    </div>
  );

  const webhookIngressProtection = (
    <div>
      <Typography paragraph sx={{ml: 2}}>
        {ingressProtections} can limit the invocation of a webhook fulfillment
        to traffic originating from within the VPC network. In a production
        environment, configuring ingression to &quot;allow internal traffic
        only&quot; is required for securing access to a webhook fulfillment with
        (or without!) a VPC service perimiter.
      </Typography>
      <Typography paragraph sx={{ml: 2}}>
        However, without additional network resources this policy configuation
        is too restrictive; Dialogflow (which is outside of the VPC) can no
        longer communicate to the webhook! To reestablish this communication
        channel, we can deploy a Google Compute Engine resource to serve as a
        middle-out revery proxy server and carry communication back and forth
        between the two restricted services.
      </Typography>
    </div>
  );

  const webhookProxyNoVPC = (
    <div>
      <Typography paragraph sx={{ml: 2}}>
        What security advantages can fulfillment traffic through a middle out
        proxy server provide on its own, independent of the security perimeters?
        The first additional layer results from the proxy server serving as a
        common point of ingress/egress to Cloud Functions, so that additional
        VPC firewall settings can be configured to fine-grain network traffic.
        Furthermore, fullfilling Dialogflow requests in a VPC context requires
        using {webhookServiceDirectory} to route traffic to the proxy server,
        which can be configured to use mutual TLS authentication. This further
        guarantees that potentially sensitive data is only transmitted through
        authorized network resources.
      </Typography>
    </div>
  );

  const webhookProxyFull = (
    <div>
      <Typography paragraph sx={{ml: 2, mb: 0}}>
        Combining all of these strategies together results in a very secure
        communication architecture with multiple overlapping solutions layering
        to provide security:
      </Typography>
      <List sx={{ml: 6}}>
        <ListItem
          style={{display: 'list-item', padding: 0, listStyleType: 'disc'}}
        >
          <ListItemText primary="IAM permissions secure webhook invocation to only intended users" />
        </ListItem>
        <ListItem
          style={{display: 'list-item', padding: 0, listStyleType: 'disc'}}
        >
          <ListItemText primary="Webhook ingress settings block invocation from outside the VPC" />
        </ListItem>
        <ListItem
          style={{display: 'list-item', padding: 0, listStyleType: 'disc'}}
        >
          <ListItemText primary="VPC Service Control perimeters block API access to sensitive resources" />
        </ListItem>
        <ListItem
          style={{display: 'list-item', padding: 0, listStyleType: 'disc'}}
        >
          <ListItemText primary="A VPC proxy server enforces mTLS authentication with Dialogflow and provides fine-grained firewall protection within the VPC" />
        </ListItem>
      </List>
    </div>
  );

  return (
    <Box sx={{width: '80%'}}>
      <Box sx={{borderBottom: 1, borderColor: 'divider'}}>
        <Tabs value={value} onChange={handleChange}>
          <Tab label="Exploring Webhooks" />
          <Tab label="Adding VPC-SC" />
          <Tab label="Ingress Protection" />
          <Tab label="Webhook Proxy without VPC-SC" />
          <Tab label="Webhook Proxy with VPC-SC" />
        </Tabs>
      </Box>
      <TutorialTab
        value={value}
        index={0}
        title="Example: Exploring Webhooks"
        body={exporingWebhooksBody}
        security={0}
      />
      <TutorialTab
        value={value}
        index={1}
        title="Example: Adding VPC Security Control Protection"
        body={vpcscProtectionBody}
        security={1}
      />
      <TutorialTab
        value={value}
        index={2}
        title="Example: Adding Webhook Ingress Protection"
        body={webhookIngressProtection}
        security={2}
      />
      <TutorialTab
        value={value}
        index={3}
        title="Example: VPC Proxying without VPC-SC"
        body={webhookProxyNoVPC}
        security={2}
      />
      <TutorialTab
        value={value}
        index={4}
        title="Example: VPC Proxying with VPC-SC"
        body={webhookProxyFull}
        security={3}
      />
    </Box>
  );
}

export {TutorialPageTabs};
