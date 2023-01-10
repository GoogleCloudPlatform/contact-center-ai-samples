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
import Switch from '@mui/material/Switch';
import Typography from '@mui/material/Typography';
import {QueryClient, QueryClientProvider, useQuery} from 'react-query';
import axios from 'axios';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import Link from '@mui/material/Link';
import Divider from '@mui/material/Divider';
import {getBucket, handleTokenExpired} from './Utilities.js';

const PANEL_WIDTH = 150;

function ResourceCollectionDeployment(target, dataModel) {
  let valueList;
  if (target === 'module.webhook_agent') {
    valueList = [
      dataModel.assetStatus['google_storage_bucket.bucket'].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.webhook_agent.google_storage_bucket_object.webhook'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.webhook_agent.google_cloudfunctions_function.webhook'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.webhook_agent.google_dialogflow_cx_agent.full_agent'
      ].current === true
        ? 1
        : 0,
    ];
  } else if (target === 'module.service_directory') {
    valueList = [
      dataModel.assetStatus[
        'module.service_directory.google_service_directory_namespace.reverse_proxy'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.service_directory.google_service_directory_service.reverse_proxy'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.service_directory.google_service_directory_endpoint.reverse_proxy'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.service_perimeter.google_access_context_manager_service_perimeter.service_perimeter[0]'
      ].current === true
        ? 1
        : 0,
    ];
  } else if (target === 'module.vpc_network') {
    valueList = [
      dataModel.assetStatus[
        'module.vpc_network.google_artifact_registry_repository.webhook_registry'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_cloudbuild_trigger.reverse_proxy_server'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_compute_address.reverse_proxy_address'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus['module.vpc_network.google_compute_firewall.allow']
        .current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_compute_firewall.allow_dialogflow'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_compute_instance.reverse_proxy_server'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_compute_network.vpc_network'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_compute_router.nat_router'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_compute_router_nat.nat_manual'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_compute_subnetwork.reverse_proxy_subnetwork'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_project_iam_member.dfsa_sd_pscAuthorizedService'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_project_iam_member.dfsa_sd_viewer'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_project_service_identity.dfsa'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_pubsub_topic.reverse_proxy_server_build'
      ].current === true
        ? 1
        : 0,
      dataModel.assetStatus[
        'module.vpc_network.google_storage_bucket_object.proxy_server_source'
      ].current === true
        ? 1
        : 0,
    ];
  } else if (target === 'module.services') {
    valueList = [
      dataModel.assetStatus['google_project_service.dialogflow'].current ===
      true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.cloudfunctions'].current ===
      true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.compute'].current === true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.iam'].current === true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.servicedirectory']
        .current === true
        ? 1
        : 0,
      dataModel.assetStatus['module.services.google_project_service.run']
        .current === true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.cloudbuild'].current ===
      true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.artifactregistry']
        .current === true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.accesscontextmanager']
        .current === true
        ? 1
        : 0,
      dataModel.assetStatus['google_project_service.cloudbilling'].current ===
      true
        ? 1
        : 0,
      dataModel.assetStatus['module.services.google_project_service.vpcaccess']
        .current === true
        ? 1
        : 0,
      dataModel.assetStatus['module.services.google_project_service.appengine']
        .current === true
        ? 1
        : 0,
    ];
  }
  return {
    deployed: valueList.reduce((a, b) => a + b, 0),
    count: valueList.length,
  };
}

function ResourceCollectionIsAllSame(target, dataModel) {
  const modules = [
    'module.webhook_agent',
    'module.service_directory',
    'module.vpc_network',
    'module.services',
  ];
  if (modules.includes(target)) {
    const deployment = ResourceCollectionDeployment(target, dataModel);
    return (
      deployment['deployed'] === 0 ||
      deployment['count'] === deployment['deployed']
    );
  } else if (target === 'all') {
    let count = 0;
    let deployed = 0;
    for (const module of modules) {
      const deployment = ResourceCollectionDeployment(module, dataModel);
      count += deployment['count'];
      deployed += deployment['deployed'];
    }
    return deployed === 0 || deployed === count;
  }
}

function StateLockErrorDialog(props) {
  return (
    <Dialog open={props.open} onClose={() => {}}>
      <DialogTitle>
        {`Error Encountered when deploying ${props.target}`}
      </DialogTitle>
      <DialogContent>
        <DialogContentText style={{whiteSpace: 'pre'}}>
          {props.error.response.data.errors[0]['@message']}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={props.onClickCancel} variant="contained">
          OK
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function ResourceImportDialog(props) {
  return (
    <Dialog open={props.open} onClose={() => {}}>
      <DialogTitle>
        {`Error Encountered when deploying ${props.target}`}
      </DialogTitle>
      <DialogContent>
        <DialogContentText style={{whiteSpace: 'pre'}}>
          {props.error.response.data.errors[0]['@message']}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={props.onClickCancel} variant="contained">
          Cancel
        </Button>
        <Button onClick={props.onClickImport} variant="contained" autoFocus>
          Import
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function AgentLocationSettingsDialog(props) {
  return (
    <Dialog open={props.open} onClose={() => {}}>
      <DialogTitle>
        {`Error Encountered when deploying ${props.target}`}
      </DialogTitle>
      <DialogContent>
        <DialogContentText style={{whiteSpace: 'pre'}}>
          {`FailedPreconditionException: Location settings have to be initialized before creating the agent in location: ${props.region}`}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={props.onClickCancel} variant="contained">
          Cancel
        </Button>
        <Button
          target="_blank"
          href={`https://dialogflow.cloud.google.com/cx/projects/${props.project_id}/locations`}
          variant="contained"
          autoFocus
        >
          OK
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function GenericErrorDialog(props) {
  return (
    <Dialog open={props.open} onClose={() => {}}>
      <DialogTitle>{'Error Encountered:'}</DialogTitle>
      <DialogContent>
        <DialogContentText style={{whiteSpace: 'pre'}}>
          {props.error.response.data.errors[0]['diagnostic']['summary']}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={props.onClickCancel} variant="contained">
          OK
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function AccessPolicyErrorDialog(props) {
  return (
    <Dialog open={props.open} onClose={() => {}}>
      <DialogTitle>{'Policy Not Found:'}</DialogTitle>
      <DialogContent>
        <DialogContentText style={{whiteSpace: 'pre'}}>
          Error using Access Policy &quot;{props.badAccessPolicyTitle}&quot;:{' '}
          {props.error.response.data.reason}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={props.onClickCancel} variant="contained">
          OK
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function ProjectIdErrorDialog(props) {
  return (
    <Dialog open={props.open} onClose={() => {}}>
      <DialogTitle>{'Unknown Project Id:'}</DialogTitle>
      <DialogContent>
        <DialogContentText style={{whiteSpace: 'pre'}}>
          Unknown Project ID: {props.unknownProjectId}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={props.onClickCancel} variant="contained">
          OK
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function ErrorDialog(props) {
  let resourceName;
  let responseType = null;

  if (
    props.error !== null &&
    Object.hasOwn(props.error.response.data, 'status') &&
    props.error.response.data.status === 'BLOCKED' &&
    props.error.response.data.reason === 'POLICY_NOT_FOUND'
  ) {
    responseType = 'ACCESS_POLICY_ERROR';
  } else if (
    props.error !== null &&
    Object.hasOwn(props.error.response.data, 'status') &&
    props.error.response.data.status === 'BLOCKED' &&
    props.error.response.data.reason === 'UNKNOWN_PROJECT_ID'
  ) {
    responseType = 'UNKNOWN_PROJECT_ID_ERROR';
  } else if (
    props.error !== null &&
    props.error.response.data.errors[0]['diagnostic']['summary'] ===
      'googleapi: Error 409: Your previous request to create the named bucket succeeded and you already own it., conflict'
  ) {
    resourceName = `'${getBucket(props.dataModel)}'`;
    responseType = 'RESOURCE_IMPORT';
  } else if (
    props.error !== null &&
    props.error.response.data.errors[0] ===
      'Error: Error acquiring the state lock'
  ) {
    responseType = 'STATE_LOCK';
  } else if (
    props.error !== null &&
    props.error.response.data.errors[0]['diagnostic']['summary'].includes(
      'Location settings have to be initialized before creating the agent'
    )
  ) {
    responseType = 'AGENT_LOCATION_SETTINGS';
  } else if (
    props.error !== null &&
    props.error.response.data.errors[0]['diagnostic']['summary'].includes(
      'generic::already_exists'
    )
  ) {
    if (
      props.target === 'module.vpc_network.google_compute_router_nat.nat_manual'
    ) {
      resourceName = `'projects/${props.dataModel.projectData.project_id.current}/regions/${props.dataModel.projectData.region.current}/routers/nat-router/nat-config'`;
    } else if (
      props.target ===
      'module.service_directory.google_service_directory_service.reverse_proxy'
    ) {
      resourceName = `'projects/${props.dataModel.projectData.project_id.current}/locations/${props.dataModel.projectData.region.current}/namespaces/df-namespace/services/df-service'`;
    } else if (
      props.target ===
      'module.service_directory.google_service_directory_endpoint.reverse_proxy'
    ) {
      resourceName = `'projects/${props.dataModel.projectData.project_id.current}/locations/${props.dataModel.projectData.region.current}/namespaces/df-namespace/services/df-service/endpoints/df-endpoint'`;
    } else if (
      props.target ===
      'module.webhook_agent.google_cloudfunctions_function.webhook'
    ) {
      resourceName = `'projects/${props.dataModel.projectData.project_id.current}/locations/${props.dataModel.projectData.region.current}/functions/${props.dataModel.projectData.webhook_name.current}'`;
    } else {
      resourceName =
        props.error.response.data.errors[0]['diagnostic']['summary'];
    }
    responseType = 'RESOURCE_IMPORT';
  } else if (
    props.error !== null &&
    props.error.response.data.errors[0]['diagnostic']['summary'].includes(
      'Must specify a title for access policy object'
    )
  ) {
    responseType = 'GENERIC';
  } else if (props.error !== null) {
    responseType = 'GENERIC';
  }

  useEffect(() => {
    if (resourceName) {
      props.setResourceName(resourceName);
    }
  }, [props, resourceName]);

  useEffect(
    () => {
      if (responseType === 'ACCESS_POLICY_ERROR') {
        props.dataModel.validAccessPolicy.set(false);
        props.dataModel.accessPolicyTitleColor.set('error');
      }
      if (responseType === 'UNKNOWN_PROJECT_ID_ERROR') {
        props.dataModel.validProjectId.set(null);
        props.dataModel.projectIdColor.set('error');
      }
    },
    /* eslint-disable react-hooks/exhaustive-deps */
    [responseType]
    /* eslint-enable react-hooks/exhaustive-deps */
  );

  if (responseType === 'STATE_LOCK') {
    return (
      <StateLockErrorDialog
        open={props.open}
        target={props.target}
        error={props.error}
        onClickCancel={props.onClickCancel}
      />
    );
  } else if (responseType === 'RESOURCE_IMPORT') {
    return (
      <ResourceImportDialog
        open={props.open}
        target={props.target}
        error={props.error}
        onClickCancel={props.onClickCancel}
        onClickImport={props.onClickImport}
      />
    );
  } else if (responseType === 'AGENT_LOCATION_SETTINGS') {
    return (
      <AgentLocationSettingsDialog
        open={props.open}
        target={props.target}
        error={props.error}
        onClickCancel={props.onClickCancel}
        region={props.dataModel.projectData.region.current}
        project_id={props.dataModel.projectData.project_id.current}
      />
    );
  } else if (responseType === 'GENERIC') {
    return (
      <GenericErrorDialog
        open={props.open}
        target={props.target}
        error={props.error}
        onClickCancel={props.onClickCancel}
      />
    );
  } else if (responseType === 'ACCESS_POLICY_ERROR') {
    return (
      <AccessPolicyErrorDialog
        open={props.open}
        onClickCancel={props.onClickCancel}
        error={props.error}
        badAccessPolicyTitle={
          props.dataModel.projectData.accessPolicyTitle.current
        }
      />
    );
  } else if (responseType === 'UNKNOWN_PROJECT_ID_ERROR') {
    return (
      <ProjectIdErrorDialog
        open={props.open}
        onClickCancel={props.onClickCancel}
        unknownProjectId={props.dataModel.projectData.project_id.current}
      />
    );
  } else if (responseType === null) {
    return <></>;
  }
}

function ToggleAsset(props) {
  const asset = props.dataModel.assetStatus[props.target];
  const [errorBoxOpen, setErrorBoxOpen] = React.useState(false);
  const [resourceName, setResourceName] = React.useState(null);

  const handleErrorBoxCancel = () => {
    setErrorBoxOpen(false);
  };

  function onSettled() {
    props.dataModel.terraformLocked.set(false);
    props.dataModel.invertAssetCollectionSwitches.set(false);
  }

  function queryFunction() {
    let destroy = asset.current === true ? true : false;
    props.dataModel.validAccessPolicy.set(true);
    if (
      props.isModuleSwitch &&
      props.dataModel.invertAssetCollectionSwitches.current &&
      !ResourceCollectionIsAllSame(props.target, props.dataModel)
    ) {
      destroy = !destroy;
    }

    let target;
    if (props.target === 'module.services' && destroy) {
      target = [
        props.target,
        'google_project_service.dialogflow',
        'google_project_service.cloudfunctions',
        'google_project_service.compute',
        'google_project_service.servicedirectory',
        'google_project_service.cloudbuild',
        'google_project_service.accesscontextmanager',
        'google_project_service.cloudbilling',
        'google_project_service.iam',
      ];
    } else if (props.target === 'module.service_directory') {
      target = [
        props.target,
        'module.service_perimeter.google_access_context_manager_service_perimeter.service_perimeter[0]',
      ];
    } else if (props.target === 'module.webhook_agent' && destroy) {
      target = [props.target, 'google_storage_bucket.bucket'];
    } else {
      target = [props.target];
    }

    props.dataModel.terraformLocked.set(true);
    return axios
      .post(
        '/update_target',
        {
          targets: target,
          destroy: destroy,
        },
        {
          params: {
            project_id: props.dataModel.projectData.project_id.current,
            bucket: getBucket(props.dataModel),
            region: props.dataModel.projectData.region.current,
            access_policy_title:
              props.dataModel.projectData.accessPolicyTitle.current,
            debug: false,
          },
        }
      )
      .then(res => res.data);
  }

  function onError() {
    setErrorBoxOpen(true);
  }

  function importFunction() {
    props.dataModel.terraformLocked.set(true);
    return axios
      .post(
        '/import',
        {
          resourceName: resourceName,
        },
        {
          params: {
            project_id: props.dataModel.projectData.project_id.current,
            bucket: getBucket(props.dataModel),
            access_policy_title:
              props.dataModel.projectData.accessPolicyTitle.current,
            region: props.dataModel.projectData.region.current,
            target: props.target,
          },
        }
      )
      .then(res => res.data);
  }

  function onSuccess(data) {
    props.dataModel.validAccessPolicy.set(true);
    props.dataModel.validProjectId.set(true);
    props.dataModel.projectIdColor.set('primary');
    if (data.status === 'BLOCKED') {
      if (
        (data.reason === 'TOKEN_EXPIRED') &
        props.dataModel.loggedIn.current &
        !props.dataModel.sessionExpiredModalOpen.current
      ) {
        handleTokenExpired(props.dataModel);
      }
    } else {
      for (const key in props.dataModel.assetStatus) {
        props.dataModel.assetStatus[key].set(data.resources.includes(key));
      }
    }
  }

  const update = useQuery('/update_target', queryFunction, {
    enabled: false,
    onSettled: onSettled,
    retry: 0,
    onError: onError,
    onSuccess: onSuccess,
  });

  function onImportSuccess() {
    update.refetch();
  }

  const tfImport = useQuery(['/import'], importFunction, {
    enabled: false,
    onSettled: onSettled,
    retry: 0,
    onSuccess: onImportSuccess,
  });

  const handleErrorBoxImport = () => {
    setErrorBoxOpen(false);
    tfImport.refetch();
  };

  function onChange() {
    update.refetch();
  }

  let visibility;
  if (
    !props.dataModel.validProjectId.current ||
    !props.dataModel.validAccessPolicy.current ||
    update.isFetching ||
    tfImport.isFetching ||
    typeof asset.current !== 'boolean' ||
    props.dataModel.terraformLocked.current ||
    asset.current === 'BLOCKED'
  ) {
    visibility = 'hidden';
  } else {
    visibility = 'visible';
  }

  if (
    (props.target ===
      'module.service_perimeter.google_access_context_manager_service_perimeter.service_perimeter[0]') &
    (props.dataModel.projectData.accessPolicyTitle.current === null ||
      typeof props.dataModel.projectData.accessPolicyTitle.current ===
        'undefined' ||
      props.dataModel.projectData.accessPolicyTitle.current === '')
  ) {
    visibility = 'hidden';
  }

  let checked = typeof asset.current === 'boolean' ? asset.current : false;
  if (
    props.isModuleSwitch &&
    props.dataModel.invertAssetCollectionSwitches.current &&
    !ResourceCollectionIsAllSame(props.target, props.dataModel)
  ) {
    checked = !checked;
  }
  const indicator = (
    <Switch
      onChange={onChange}
      checked={checked}
      color="primary"
      style={{visibility: visibility}}
      size={props.target === 'all' ? 'medium' : 'small'}
    />
  );

  let name;
  if (
    props.dataModel &&
    props.dataModel.projectData.project_id.current !== null &&
    props.dataModel.assetStatus[props.target].current === true
  ) {
    name = (
      <Link target="_blank" href={props.href} variant="body1">
        {props.name}
      </Link>
    );
  } else {
    name = <Typography variant="body2">{props.name}</Typography>;
  }

  const nameBox = (
    <Box
      sx={{pl: 1, mx: 0, my: 0.5, py: 1, width: PANEL_WIDTH, height: 30}}
      display="flex"
      alignItems="center"
      justifyContent="right"
    >
      {name}
    </Box>
  );

  return (
    <>
      <ErrorDialog
        open={errorBoxOpen}
        onClickCancel={handleErrorBoxCancel}
        onClickImport={handleErrorBoxImport}
        target={props.target}
        setResourceName={setResourceName}
        error={update.error}
        dataModel={props.dataModel}
      />
      <Grid
        container
        item
        direction="row"
        columnSpacing={3}
        justifyContent="flex-start"
        alignItems="center"
      >
        {props.includeNameBox ? <></> : nameBox}
        <Box
          sx={{width: 60, height: 30}}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {indicator}
        </Box>
      </Grid>
    </>
  );
}

function PollAssetStatus(props) {
  const [errorBoxOpen, setErrorBoxOpen] = React.useState(false);

  function onSettled() {
    props.dataModel.terraformLocked.set(false);
  }

  function queryFunction() {
    props.dataModel.terraformLocked.set(true);
    props.dataModel.validAccessPolicy.set(true);
    return axios
      .get('/asset_status', {
        params: {
          project_id: props.dataModel.projectData.project_id.current,
          bucket: getBucket(props.dataModel),
          region: props.dataModel.projectData.region.current,
          access_policy_title:
            props.dataModel.projectData.accessPolicyTitle.current,
          debug: false,
        },
      })
      .then(res => res.data);
  }

  function onError() {
    setErrorBoxOpen(true);
  }

  function onSuccess(data) {
    props.dataModel.validAccessPolicy.set(true);
    props.dataModel.validProjectId.set(true);
    props.dataModel.projectIdColor.set('primary');
    if (data.status !== 'BLOCKED') {
      for (const key in props.dataModel.assetStatus) {
        props.dataModel.assetStatus[key].set(data.resources.includes(key));
      }
    }
  }

  const assetStatus = useQuery(
    ['/asset_status', props.dataModel.projectData.project_id.current],
    queryFunction,
    {
      refetchInterval: props.dataModel.terraformLocked.current ? false : 600000,
      onSettled: onSettled,
      retry: false,
      enabled: false,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
      onError: onError,
      onSuccess: onSuccess,
    }
  );

  useEffect(() => {
    if (props.dataModel.refetchAssetStatus.current === true) {
      assetStatus.refetch();
      props.dataModel.refetchAssetStatus.set(false);
    }
  });

  const handleErrorBoxCancel = () => {
    setErrorBoxOpen(false);
  };

  return (
    <ErrorDialog
      open={errorBoxOpen}
      onClickCancel={handleErrorBoxCancel}
      error={assetStatus.error}
      dataModel={props.dataModel}
    />
  );
}

function QueryToggleAsset(props) {
  const queryClient = new QueryClient();
  const {isModuleSwitch = false} = props;
  return (
    <div>
      <QueryClientProvider client={queryClient}>
        <ToggleAsset
          name={props.name}
          target={props.target}
          dataModel={props.dataModel}
          enableAlert={props.enableAlert}
          includeNameBox={props.includeNameBox}
          isModuleSwitch={isModuleSwitch}
          href={props.href}
        />
      </QueryClientProvider>
    </div>
  );
}

function QueryPollAssetStatus(props) {
  const queryClient = new QueryClient();
  return (
    <div>
      <QueryClientProvider client={queryClient}>
        <PollAssetStatus dataModel={props.dataModel} />
      </QueryClientProvider>
    </div>
  );
}

function servicesLink(service, project_id) {
  return `https://console.cloud.google.com/apis/api/${service}.googleapis.com/metrics?project=${project_id}`;
}

function servicePerimeterLink(project_id) {
  return `https://console.cloud.google.com/security/service-perimeter?orgonly=true&project=${project_id}&supportedpurview=organizationId`;
}

function bucketLink(bucket) {
  return `https://console.cloud.google.com/storage/browser/${bucket}`;
}

function archiveLink(bucket, filename) {
  return `https://console.cloud.google.com/storage/browser/_details/${bucket}/${filename}`;
}

function webhookLink(project_id, region) {
  return `https://console.cloud.google.com/functions/details/${region}/custom-telco-webhook?project=${project_id}`;
}

function agentLink(project_id, region) {
  return `https://dialogflow.cloud.google.com/cx/projects/${project_id}/locations/${region}/agents`;
}

function namespaceLink(project_id, region) {
  return `https://console.cloud.google.com/net-services/service-directory/namespaces/${region}/df-namespace/view?orgonly=true&project=${project_id}&supportedpurview=organizationId`;
}

function serviceLink(project_id, region) {
  return `https://console.cloud.google.com/net-services/service-directory/namespaces/${region}/df-namespace/services/df-service/view?orgonly=true&project=${project_id}&supportedpurview=organizationId`;
}

function endpointLink(project_id, region) {
  return `https://console.cloud.google.com/net-services/service-directory/namespaces/${region}/df-namespace/services/df-service/endpoints/df-endpoint/view?orgonly=true&project=${project_id}&supportedpurview=organizationId`;
}

function networkLink(project_id) {
  return `https://console.cloud.google.com/networking/networks/details/webhook-net?project=${project_id}&orgonly=true&supportedpurview=organizationId`;
}

function subnetworkLink(project_id, region) {
  return `https://console.cloud.google.com/networking/subnetworks/details/${region}/webhook-subnet?project=${project_id}&orgonly=true&supportedpurview=organizationId`;
}

function routerLink(project_id, region) {
  return `https://console.cloud.google.com/hybrid/routers/details/${region}/nat-router?project=${project_id}&region=${region}`;
}

function routerNATLink(project_id, region) {
  return `https://console.cloud.google.com/net-services/nat/details/${region}/nat-router/nat-config?project=${project_id}&tab=details`;
}

function firewallLink(name, project_id) {
  return `https://console.cloud.google.com/networking/firewalls/details/${name}?project=${project_id}`;
}

function addressesLink(project_id) {
  return `https://console.cloud.google.com/networking/addresses/list?orgonly=true&project=${project_id}&supportedpurview=organizationId`;
}

function registryLink(project_id, region) {
  return `https://console.cloud.google.com/artifacts/docker/${project_id}/${region}/webhook-registry`;
}

function buildHistoryLink(project_id) {
  return `https://console.cloud.google.com/cloud-build/builds?project=${project_id}`;
}

function buildTriggerLink(project_id) {
  return `https://console.cloud.google.com/cloudpubsub/topic/detail/build?project=${project_id}`;
}

function proxyServerLink(project_id, region) {
  return `https://console.cloud.google.com/compute/instancesDetail/zones/${region}-a/instances/webhook-server?project=${project_id}`;
}

function serviceIdentityLink(project_id) {
  return `https://console.cloud.google.com/iam-admin/iam?project=${project_id}`;
}

function ServicesPanel(props) {
  const project_id = props.dataModel.projectData.project_id.current;
  return (
    <>
      <Grid container direction="row" justifyContent="space-between">
        <Typography variant="h6">APIs & Services:</Typography>
        <QueryToggleAsset
          target="module.services"
          dataModel={props.dataModel}
          enableAlert={true}
          includeNameBox={true}
          isModuleSwitch={true}
        />
      </Grid>
      <Divider sx={{my: 1}} orientation="horizontal" flexItem />
      <Grid container justifyContent="flex-end">
        <QueryToggleAsset
          name="dialogflow"
          target="google_project_service.dialogflow"
          dataModel={props.dataModel}
          href={servicesLink('dialogflow', project_id)}
        />
        <QueryToggleAsset
          name="cloudfunctions"
          target="google_project_service.cloudfunctions"
          dataModel={props.dataModel}
          href={servicesLink('cloudfunctions', project_id)}
        />
        <QueryToggleAsset
          name="compute"
          target="google_project_service.compute"
          dataModel={props.dataModel}
          href={servicesLink('compute', project_id)}
        />
        <QueryToggleAsset
          name="iam"
          target="google_project_service.iam"
          dataModel={props.dataModel}
          href={servicesLink('iam', project_id)}
        />
        <QueryToggleAsset
          name="servicedirectory"
          target="google_project_service.servicedirectory"
          dataModel={props.dataModel}
          href={servicesLink('servicedirectory', project_id)}
        />
        <QueryToggleAsset
          name="run"
          target="module.services.google_project_service.run"
          dataModel={props.dataModel}
          href={servicesLink('run', project_id)}
        />
        <QueryToggleAsset
          name="cloudbuild"
          target="google_project_service.cloudbuild"
          dataModel={props.dataModel}
          href={servicesLink('cloudbuild', project_id)}
        />
        <QueryToggleAsset
          name="artifactregistry"
          target="google_project_service.artifactregistry"
          dataModel={props.dataModel}
          href={servicesLink('artifactregistry', project_id)}
        />
        <QueryToggleAsset
          name="accesscontextmanager"
          target="google_project_service.accesscontextmanager"
          dataModel={props.dataModel}
          href={servicesLink('accesscontextmanager', project_id)}
        />
        <QueryToggleAsset
          name="cloudbilling"
          target="google_project_service.cloudbilling"
          dataModel={props.dataModel}
          href={servicesLink('cloudbilling', project_id)}
        />
        <QueryToggleAsset
          name="vpcaccess"
          target="module.services.google_project_service.vpcaccess"
          dataModel={props.dataModel}
          href={servicesLink('vpcaccess', project_id)}
        />
        <QueryToggleAsset
          name="appengine"
          target="module.services.google_project_service.appengine"
          dataModel={props.dataModel}
          href={servicesLink('appengine', project_id)}
        />
      </Grid>
    </>
  );
}

function NetworkPanel(props) {
  const project_id = props.dataModel.projectData.project_id.current;
  const region = props.dataModel.projectData.region.current;
  const bucket = getBucket(props.dataModel);
  return (
    <>
      <Grid container direction="row" justifyContent="space-between">
        <Typography variant="h6">VPC Resources:</Typography>
        <QueryToggleAsset
          target="module.vpc_network"
          dataModel={props.dataModel}
          enableAlert={false}
          includeNameBox={true}
          isModuleSwitch={true}
        />
      </Grid>
      <Divider sx={{my: 1}} orientation="horizontal" flexItem />
      <Grid container justifyContent="flex-end">
        <QueryToggleAsset
          name="VPC network"
          target="module.vpc_network.google_compute_network.vpc_network"
          dataModel={props.dataModel}
          href={networkLink(project_id)}
        />
        <QueryToggleAsset
          name="VPC subnetwork"
          target="module.vpc_network.google_compute_subnetwork.reverse_proxy_subnetwork"
          dataModel={props.dataModel}
          href={subnetworkLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Router"
          target="module.vpc_network.google_compute_router.nat_router"
          dataModel={props.dataModel}
          href={routerLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Router NAT"
          target="module.vpc_network.google_compute_router_nat.nat_manual"
          dataModel={props.dataModel}
          href={routerNATLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Firewall: General"
          target="module.vpc_network.google_compute_firewall.allow"
          dataModel={props.dataModel}
          href={firewallLink('allow', project_id)}
        />
        <QueryToggleAsset
          name="Firewall: Dialogflow"
          target="module.vpc_network.google_compute_firewall.allow_dialogflow"
          dataModel={props.dataModel}
          href={firewallLink('allow-dialogflow', project_id)}
        />
        <QueryToggleAsset
          name="Address"
          target="module.vpc_network.google_compute_address.reverse_proxy_address"
          dataModel={props.dataModel}
          href={addressesLink(project_id)}
        />
        <QueryToggleAsset
          name="Artifact Registry"
          target="module.vpc_network.google_artifact_registry_repository.webhook_registry"
          dataModel={props.dataModel}
          href={registryLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Server Source"
          target="module.vpc_network.google_storage_bucket_object.proxy_server_source"
          dataModel={props.dataModel}
          href={archiveLink(bucket, 'server.zip')}
        />
        <QueryToggleAsset
          name="Build History"
          target="module.vpc_network.google_cloudbuild_trigger.reverse_proxy_server"
          dataModel={props.dataModel}
          href={buildHistoryLink(project_id)}
        />
        <QueryToggleAsset
          name="Build Trigger"
          target="module.vpc_network.google_pubsub_topic.reverse_proxy_server_build"
          dataModel={props.dataModel}
          href={buildTriggerLink(project_id)}
        />
        <QueryToggleAsset
          name="Proxy Server"
          target="module.vpc_network.google_compute_instance.reverse_proxy_server"
          dataModel={props.dataModel}
          href={proxyServerLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Service Identity"
          target="module.vpc_network.google_project_service_identity.dfsa"
          dataModel={props.dataModel}
          href={serviceIdentityLink(project_id)}
        />
      </Grid>
    </>
  );
}

function ServiceDirectoryPanel(props) {
  const project_id = props.dataModel.projectData.project_id.current;
  const region = props.dataModel.projectData.region.current;
  return (
    <>
      <Grid container direction="row" justifyContent="space-between">
        <Typography variant="h6">Service Directory:</Typography>
        <QueryToggleAsset
          target="module.service_directory"
          dataModel={props.dataModel}
          enableAlert={false}
          includeNameBox={true}
          isModuleSwitch={true}
        />
      </Grid>
      <Divider sx={{my: 1}} orientation="horizontal" flexItem />
      <Grid container justifyContent="flex-end">
        <QueryToggleAsset
          name="Namespace"
          target="module.service_directory.google_service_directory_namespace.reverse_proxy"
          dataModel={props.dataModel}
          href={namespaceLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Service"
          target="module.service_directory.google_service_directory_service.reverse_proxy"
          dataModel={props.dataModel}
          href={serviceLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Endpoint"
          target="module.service_directory.google_service_directory_endpoint.reverse_proxy"
          dataModel={props.dataModel}
          href={endpointLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Service Perimeter"
          target="module.service_perimeter.google_access_context_manager_service_perimeter.service_perimeter[0]"
          dataModel={props.dataModel}
          href={servicePerimeterLink(project_id, region)}
        />
      </Grid>
    </>
  );
}

function AgentPanel(props) {
  const project_id = props.dataModel.projectData.project_id.current;
  const region = props.dataModel.projectData.region.current;
  const bucket = getBucket(props.dataModel);
  return (
    <>
      <Grid container direction="row" justifyContent="space-between">
        <Typography variant="h6">Webhook Agent:</Typography>
        <QueryToggleAsset
          target="module.webhook_agent"
          dataModel={props.dataModel}
          enableAlert={false}
          includeNameBox={true}
          isModuleSwitch={true}
        />
      </Grid>
      <Divider sx={{my: 1}} orientation="horizontal" flexItem />
      <Grid container justifyContent="flex-end">
        <QueryToggleAsset
          name="Storage Bucket"
          target="google_storage_bucket.bucket"
          dataModel={props.dataModel}
          href={bucketLink(bucket)}
        />
        <QueryToggleAsset
          name="Webhook Source"
          target="module.webhook_agent.google_storage_bucket_object.webhook"
          dataModel={props.dataModel}
          href={archiveLink(bucket, 'webhook.zip')}
        />
        <QueryToggleAsset
          name="Webhook Function"
          target="module.webhook_agent.google_cloudfunctions_function.webhook"
          dataModel={props.dataModel}
          href={webhookLink(project_id, region)}
        />
        <QueryToggleAsset
          name="Dialogflow Agent"
          target="module.webhook_agent.google_dialogflow_cx_agent.full_agent"
          dataModel={props.dataModel}
          href={agentLink(project_id, region)}
        />
      </Grid>
    </>
  );
}

export {
  ServicesPanel,
  NetworkPanel,
  AgentPanel,
  QueryPollAssetStatus,
  QueryToggleAsset,
  ServiceDirectoryPanel,
  PANEL_WIDTH,
};
