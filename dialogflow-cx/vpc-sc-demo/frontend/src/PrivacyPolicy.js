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

import React from 'react';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';

function PrivacyPolicyPage(props) {
  const openSourceAndPubliclyViewable = (
    <Link
      target="_blank"
      href="https://github.com/GoogleCloudPlatform/contact-center-ai-samples/tree/main/dialogflow-cx/vpc-sc-demo"
      variant="body1"
    >
      Open Source and publicly viewable
    </Link>
  );
  const AccessToken = (
    <Link
      target="_blank"
      href="https://developers.google.com/identity/protocols/oauth2"
      variant="body1"
    >
      Access Token
    </Link>
  );
  const AccessTokenScope = (
    <Link
      target="_blank"
      href="https://www.googleapis.com/auth/cloud-platform"
      variant="body1"
    >
      cloud-platform
    </Link>
  );
  const launchPadLink = (
    <Link
      style={{cursor: 'pointer'}}
      onClick={() => {
        props.dataModel.activePage.set('liveDemo');
      }}
    >
      Live Demo &quot;Launch Pad&quot;
    </Link>
  );

  return (
    <>
      <Typography variant="h4" sx={{my: 3}} id="privacyPolicy">
        Privacy Policy
      </Typography>
      <Typography paragraph>
        This demo app is built and maintained by the Developer Enablement
        Engineering Team at Google Cloud, but is not an official Google Project.
        When you use this service, you are entrusting us with your data, and we
        take that responsibility very seriously. This site collects some data as
        you explore the demo via cookies. But no identifying information is
        collected or stored. There is an option to &quot;Log In&quot; with your
        Google identity using OAuth to access the advanced features of the demo,
        but this additional data is only stored for a short period of time
        (maximum 60 minutes). All the source code for this website is{' '}
        {openSourceAndPubliclyViewable}, but to summarize:
      </Typography>
      <Typography variant="h5" sx={{mx: 2, my: 1}} id="privacyPolicyCookies">
        Cookies:
      </Typography>
      <Typography paragraph sx={{mx: 2, mb: 1}}>
        This website uses cookies in two ways:
      </Typography>
      <Typography paragraph sx={{mx: 4, mb: 1}}>
        1) To keep track of the total number of unique visitors. This
        information is anonymous when it is collected, and only used in the
        aggregate to help us better understand what parts of the site are the
        most interesting and helpful to the users.
      </Typography>
      <Typography paragraph sx={{mx: 4}}>
        2) When a user &quot;Logs In&quot; via OAuth, a session cookie is stored
        in your browser. This cookie is a unique identifier that enables the
        website to issue commands to Google Cloud APIs. This data expires after
        60 minutes, and is not used for tracking or analytics.
      </Typography>
      <Typography variant="h5" sx={{mx: 2, my: 1}} id="privacyPolicyTokens">
        Access Tokens:
      </Typography>
      <Typography paragraph sx={{mx: 2}}>
        If you authenticate your identity using OAuth with your Google identity
        (i.e. &quot;Log in&quot;), you will authorize an {AccessToken} with{' '}
        {AccessTokenScope} scope to be temporarily stored. This non-renewable
        token is deleted after 60 minutes, and is used to deploy and remove
        several pre-defined cloud resources.
      </Typography>
      <Typography paragraph sx={{mx: 2}}>
        If the token expires while you are still exploring (or you log out), it
        will be immediately deleted and you will be prompted to reauthorize the
        service. Although your access token is temporarily stored, it is stored
        in an RSA-encrypted format, so that only you can use your token on the{' '}
        {launchPadLink}.
      </Typography>
      <Typography variant="h5" sx={{mx: 2, my: 1}} id="privacyPolicyStorage">
        Data Storage:
      </Typography>
      <Typography paragraph sx={{mx: 2}}>
        Access Tokens are stored in a secure, private Google Cloud Storage
        bucket, in an encrypted form, and is deleted after 60 minutes, and
        session ids are never stored. Anonymous visit ids are permanently stored
        in a Google BigQuery, but cannot be correlated to user visits or user
        data.
      </Typography>
      <Typography variant="h5" sx={{mx: 2, my: 1}} id="privacyPolicyContact">
        Contact Us:
      </Typography>
      <Typography paragraph sx={{mx: 2}}>
        If you have any questions regarding our Privacy Policy, please contact
        us at: webmaster@dialogflow-demo.app.
      </Typography>
    </>
  );
}

export {PrivacyPolicyPage};
