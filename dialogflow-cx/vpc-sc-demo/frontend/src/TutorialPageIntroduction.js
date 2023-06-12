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
import Paper from '@mui/material/Paper';

function TutorialPageIntroduction() {
  return (
    <Paper sx={{width: '85%', ml: 2}} variant="string">
      <Typography variant="h3" sx={{my: 3}}>
        Securing Your Dialogflow Agent: A Tutorial
      </Typography>
      <Typography paragraph>
        The front-line security for a Dialogflow CX agent is fairly
        straight-forward to implement, and accomplished through Access Controls
        via Identity and Access Managament (IAM) roles. For self-contained
        agents or exploratory development, these measures provide more than
        enough flexibility and safety. The true power of Dialogflow is unlocked,
        however, when enabling webhook fullfillments to other resources, such as
        databases or other business-logic implemented in on external servers or
        via serverless applications. In these scenarios, additional layers of
        security may not only be a good idea, but required for regulatory
        compliance.
      </Typography>
      <Typography paragraph>
        What other options does Google Cloud Platform (GCP) provide for securing
        sensitive servers or application layers from unexpected or malicious
        intrusion? A &quot;defense-in-depth&quot; approach to security suggests
        building multiple layers of security into the system architure. With
        more layers, however, come more configurations and complications to
        design and manage; below is an interactve tutorial aimed to
        understanding how IAM permissions, firewall configurations, custom
        Certificate Authority (CA) certificates, and VPC Service Controls can be
        layered to secure sensitive data.
      </Typography>
    </Paper>
  );
}

export {TutorialPageIntroduction};
