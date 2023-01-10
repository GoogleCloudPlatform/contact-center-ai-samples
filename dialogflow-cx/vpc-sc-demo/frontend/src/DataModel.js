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

import {useState} from 'react';
import {TIMER_SCALE} from './StatusPollToggle.js';

const region_default = 'us-central1';
const webhook_name_default = 'custom-telco-webhook';

class ReversibleMap {
  constructor(map) {
    this.map = map;
    this.reverseMap = map;
    for (const key in map) {
      const value = map[key];
      this.reverseMap[value] = key;
    }
  }
  get(key) {
    return this.map[key];
  }
  revGet(key) {
    return this.reverseMap[key];
  }
  set(key, value) {
    this.map[key] = value;
    this.reverseMap[value] = key;
  }
  unset(key) {
    delete this.reverseMap[this.map[key]];
    delete this.map[key];
  }
  revUnset(key) {
    delete this.map[this.reverseMap[key]];
    delete this.reverseMap[key];
  }
}

function BuildMapPageNumberToState() {
  const order = new ReversibleMap({});
  order.set('dialogflowRestrictedState', 0);
  order.set('cloudfunctionsRestrictedState', 1);
  order.set('webhookAccessState', 2);
  order.set('webhookIngressState', 3);
  order.set('serviceDirectoryWebhookState', 4);
  let counter = 1;
  const map = new ReversibleMap({});
  for (const x0 of [true, false]) {
    for (const x1 of [true, false]) {
      for (const x2 of [true, false]) {
        for (const x3 of [true, false]) {
          for (const x4 of [true, false]) {
            const curr_array = [x0, x1, x2, x3, x4];
            map.set(counter, curr_array);
            counter += 1;
          }
        }
      }
    }
  }

  const connectionEnabled = {};
  connectionEnabled[[false, false, false, false, false]] = true;
  connectionEnabled[[false, false, false, false, true]] = true;
  connectionEnabled[[false, false, false, true, false]] = false;
  connectionEnabled[[false, false, false, true, true]] = true;
  connectionEnabled[[false, false, true, false, false]] = true;
  connectionEnabled[[false, false, true, false, true]] = true;
  connectionEnabled[[false, false, true, true, false]] = false;
  connectionEnabled[[false, false, true, true, true]] = true;
  connectionEnabled[[false, true, false, false, false]] = true;
  connectionEnabled[[false, true, false, false, true]] = true;
  connectionEnabled[[false, true, false, true, false]] = false;
  connectionEnabled[[false, true, false, true, true]] = true;
  connectionEnabled[[false, true, true, false, false]] = true;
  connectionEnabled[[false, true, true, false, true]] = true;
  connectionEnabled[[false, true, true, true, false]] = false;
  connectionEnabled[[false, true, true, true, true]] = true;
  connectionEnabled[[true, false, false, false, false]] = true;
  connectionEnabled[[true, false, false, false, true]] = true;
  connectionEnabled[[true, false, false, true, false]] = false;
  connectionEnabled[[true, false, false, true, true]] = true;
  connectionEnabled[[true, false, true, false, false]] = true;
  connectionEnabled[[true, false, true, false, true]] = true;
  connectionEnabled[[true, false, true, true, false]] = false;
  connectionEnabled[[true, false, true, true, true]] = true;
  connectionEnabled[[true, true, false, false, false]] = true;
  connectionEnabled[[true, true, false, false, true]] = true;
  connectionEnabled[[true, true, false, true, false]] = false;
  connectionEnabled[[true, true, false, true, true]] = true;
  connectionEnabled[[true, true, true, false, false]] = true;
  connectionEnabled[[true, true, true, false, true]] = true;
  connectionEnabled[[true, true, true, true, false]] = false;
  connectionEnabled[[true, true, true, true, true]] = true;

  const stateCache = [null, null, null, null, null];
  return {
    map: map,
    order: order,
    stateCache: stateCache,
    connectionEnabled: connectionEnabled,
  };
}

function getState() {
  return {
    status: {current: null, set: null},
    isUpdating: {current: null, set: null},
    blocked: {current: null, set: null},
    timeSinceSliderClick: {current: null, set: null},
  };
}
function InitializeState(state) {
  [state.isUpdating.current, state.isUpdating.set] = useState(true);
  [state.status.current, state.status.set] = useState(false);
  [state.blocked.current, state.blocked.set] = useState(false);
  [state.timeSinceSliderClick.current, state.timeSinceSliderClick.set] =
    useState(1000 * TIMER_SCALE);
}

function ProjectData() {
  const principal = {current: null, set: null};
  const webhook_name = {current: null, set: null};
  const region = {current: null, set: null};

  [webhook_name.current, webhook_name.set] = useState(webhook_name_default);
  [region.current, region.set] = useState(region_default);
  [principal.current, principal.set] = useState(null);
  return {
    project_id: {current: null, set: null},
    webhook_name: webhook_name,
    region: region,
    principal: principal,
    accessPolicyTitle: {current: null, set: null},
  };
}

function AssetStatus() {
  const dialogflowService = {current: null, set: null};
  const cloudfunctionService = {current: null, set: null};
  const computeService = {current: null, set: null};
  const iamService = {current: null, set: null};
  const servicedirectoryService = {current: null, set: null};
  const runService = {current: null, set: null};
  const cloudbuildService = {current: null, set: null};
  const artifactregistryService = {current: null, set: null};
  const accesscontextmanagerService = {current: null, set: null};
  const vpcaccessService = {current: null, set: null};
  const appengineService = {current: null, set: null};
  const cloudbillingService = {current: null, set: null};
  const network = {current: null, set: null};
  const subNetwork = {current: null, set: null};
  const natRouter = {current: null, set: null};
  const natManual = {current: null, set: null};
  const firewallDialogflow = {current: null, set: null};
  const firewallAllow = {current: null, set: null};
  const proxyNamespace = {current: null, set: null};
  const proxyService = {current: null, set: null};
  const proxyEndpoint = {current: null, set: null};
  const proxyAddress = {current: null, set: null};
  const networkModule = {current: null, set: null};
  const servicesModule = {current: null, set: null};
  const serviceDirectoryModule = {current: null, set: null};
  const webhookAgentModule = {current: null, set: null};
  const storageBucket = {current: null, set: null};
  const webhookArchive = {current: null, set: null};
  const webhookFunction = {current: null, set: null};
  const webhookAgent = {current: null, set: null};
  const allAssets = {current: null, set: null};
  const servicePerimeterModule = {current: null, set: null};
  const servicePerimeter = {current: null, set: null};
  const webhookRegistry = {current: null, set: null};
  const buildTrigger = {current: null, set: null};
  const proxyServer = {current: null, set: null};
  const serviceAgent = {current: null, set: null};
  const serviceAgentMemberA = {current: null, set: null};
  const serviceAgentMemberB = {current: null, set: null};
  const buildPubSub = {current: null, set: null};
  const serverArchive = {current: null, set: null};

  [cloudfunctionService.current, cloudfunctionService.set] = useState(null);
  [dialogflowService.current, dialogflowService.set] = useState(null);
  [computeService.current, computeService.set] = useState(null);
  [iamService.current, iamService.set] = useState(null);
  [servicedirectoryService.current, servicedirectoryService.set] =
    useState(null);
  [runService.current, runService.set] = useState(null);
  [cloudbuildService.current, cloudbuildService.set] = useState(null);
  [artifactregistryService.current, artifactregistryService.set] =
    useState(null);
  [accesscontextmanagerService.current, accesscontextmanagerService.set] =
    useState(null);
  [vpcaccessService.current, vpcaccessService.set] = useState(null);
  [appengineService.current, appengineService.set] = useState(null);
  [cloudbillingService.current, cloudbillingService.set] = useState(null);
  [network.current, network.set] = useState(null);
  [subNetwork.current, subNetwork.set] = useState(null);
  [natRouter.current, natRouter.set] = useState(null);
  [natManual.current, natManual.set] = useState(null);
  [firewallDialogflow.current, firewallDialogflow.set] = useState(null);
  [firewallAllow.current, firewallAllow.set] = useState(null);
  [proxyNamespace.current, proxyNamespace.set] = useState(null);
  [proxyService.current, proxyService.set] = useState(null);
  [proxyEndpoint.current, proxyEndpoint.set] = useState(null);
  [proxyAddress.current, proxyAddress.set] = useState(null);
  [networkModule.current, networkModule.set] = useState(null);
  [servicesModule.current, servicesModule.set] = useState(null);
  [serviceDirectoryModule.current, serviceDirectoryModule.set] = useState(null);
  [webhookAgentModule.current, webhookAgentModule.set] = useState(null);
  [storageBucket.current, storageBucket.set] = useState(null);
  [webhookArchive.current, webhookArchive.set] = useState(null);
  [webhookFunction.current, webhookFunction.set] = useState(null);
  [webhookAgent.current, webhookAgent.set] = useState(null);
  [allAssets.current, allAssets.set] = useState(null);
  [servicePerimeterModule.current, servicePerimeterModule.set] = useState(null);
  [servicePerimeter.current, servicePerimeter.set] = useState(null);
  [webhookRegistry.current, webhookRegistry.set] = useState(null);
  [buildTrigger.current, buildTrigger.set] = useState(null);
  [proxyServer.current, proxyServer.set] = useState(null);
  [serviceAgent.current, serviceAgent.set] = useState(null);
  [serviceAgentMemberA.current, serviceAgentMemberA.set] = useState(null);
  [serviceAgentMemberB.current, serviceAgentMemberB.set] = useState(null);
  [buildPubSub.current, buildPubSub.set] = useState(null);
  [serverArchive.current, serverArchive.set] = useState(null);

  return {
    'module.services': servicesModule,
    'module.services.google_project_service.appengine': appengineService,
    'google_project_service.artifactregistry': artifactregistryService,
    'module.services.google_project_service.run': runService,
    'module.services.google_project_service.vpcaccess': vpcaccessService,
    'google_project_service.accesscontextmanager': accesscontextmanagerService,
    'google_project_service.cloudbilling': cloudbillingService,
    'google_project_service.cloudbuild': cloudbuildService,
    'google_project_service.cloudfunctions': cloudfunctionService,
    'google_project_service.compute': computeService,
    'google_project_service.dialogflow': dialogflowService,
    'google_project_service.iam': iamService,
    'google_project_service.servicedirectory': servicedirectoryService,
    'module.vpc_network': networkModule,
    'module.vpc_network.google_artifact_registry_repository.webhook_registry':
      webhookRegistry,
    'module.vpc_network.google_cloudbuild_trigger.reverse_proxy_server':
      buildTrigger,
    'module.vpc_network.google_compute_address.reverse_proxy_address':
      proxyAddress,
    'module.vpc_network.google_compute_firewall.allow': firewallAllow,
    'module.vpc_network.google_compute_firewall.allow_dialogflow':
      firewallDialogflow,
    'module.vpc_network.google_compute_instance.reverse_proxy_server':
      proxyServer,
    'module.vpc_network.google_compute_network.vpc_network': network,
    'module.vpc_network.google_compute_router.nat_router': natRouter,
    'module.vpc_network.google_compute_router_nat.nat_manual': natManual,
    'module.vpc_network.google_compute_subnetwork.reverse_proxy_subnetwork':
      subNetwork,
    'module.vpc_network.google_project_service_identity.dfsa': serviceAgent,
    'module.vpc_network.google_project_iam_member.dfsa_sd_pscAuthorizedService':
      serviceAgentMemberA,
    'module.vpc_network.google_project_iam_member.dfsa_sd_viewer':
      serviceAgentMemberB,
    'module.vpc_network.google_pubsub_topic.reverse_proxy_server_build':
      buildPubSub,
    'module.vpc_network.google_storage_bucket_object.proxy_server_source':
      serverArchive,
    'module.service_directory': serviceDirectoryModule,
    'module.service_directory.google_service_directory_namespace.reverse_proxy':
      proxyNamespace,
    'module.service_directory.google_service_directory_service.reverse_proxy':
      proxyService,
    'module.service_directory.google_service_directory_endpoint.reverse_proxy':
      proxyEndpoint,
    'module.service_perimeter.google_access_context_manager_service_perimeter.service_perimeter[0]':
      servicePerimeter,
    'module.webhook_agent': webhookAgentModule,
    'google_storage_bucket.bucket': storageBucket,
    'module.webhook_agent.google_dialogflow_cx_agent.full_agent': webhookAgent,
    'module.webhook_agent.google_storage_bucket_object.webhook': webhookArchive,
    'module.webhook_agent.google_cloudfunctions_function.webhook':
      webhookFunction,
    all: allAssets,
  };
}

function DataModel() {
  const pageMapper = BuildMapPageNumberToState();
  const loggedIn = {current: null, set: null};
  const pageNumber = {current: null, set: null};
  const renderedPageNumber = {current: null, set: null};
  const terraformLocked = {current: null, set: null};
  const validProjectId = {current: null, set: null};
  const validAccessPolicy = {current: null, set: null};
  const invertAssetCollectionSwitches = {current: null, set: null};
  const showServicesPanel = {current: null, set: null};
  const sessionExpiredModalOpen = {current: null, set: null};
  const loginRedirect = {current: null, set: null};
  const refetchAssetStatus = {current: null, set: null};
  const projectIdColor = {current: null, set: null};
  const accessPolicyTitleColor = {current: null, set: null};

  const allStates = {};
  allStates['dialogflowRestrictedState'] = getState();
  allStates['cloudfunctionsRestrictedState'] = getState();
  allStates['webhookAccessState'] = getState();
  allStates['webhookIngressState'] = getState();
  allStates['serviceDirectoryWebhookState'] = getState();
  InitializeState(allStates['dialogflowRestrictedState']);
  InitializeState(allStates['cloudfunctionsRestrictedState']);
  InitializeState(allStates['webhookAccessState']);
  InitializeState(allStates['webhookIngressState']);
  InitializeState(allStates['serviceDirectoryWebhookState']);

  [loggedIn.current, loggedIn.set] = useState(false);
  [pageNumber.current, pageNumber.set] = useState(33);
  [renderedPageNumber.current, renderedPageNumber.set] = useState(null);
  [terraformLocked.current, terraformLocked.set] = useState(false);
  [validProjectId.current, validProjectId.set] = useState(false);
  [validAccessPolicy.current, validAccessPolicy.set] = useState(true);
  [invertAssetCollectionSwitches.current, invertAssetCollectionSwitches.set] =
    useState(false);
  [showServicesPanel.current, showServicesPanel.set] = useState(true);
  [sessionExpiredModalOpen.current, sessionExpiredModalOpen.set] =
    useState(false);
  [loginRedirect.current, loginRedirect.set] = useState(false);
  [refetchAssetStatus.current, refetchAssetStatus.set] = useState(false);
  [projectIdColor.current, projectIdColor.set] = useState('primary');
  [accessPolicyTitleColor.current, accessPolicyTitleColor.set] =
    useState('primary');

  const dataModel = {
    pageMapper: pageMapper,
    loggedIn: loggedIn,
    pageNumber: pageNumber,
    allStates: allStates,
    renderedPageNumber: renderedPageNumber,
    projectData: ProjectData(),
    assetStatus: AssetStatus(),
    terraformLocked: terraformLocked,
    validProjectId: validProjectId,
    validAccessPolicy: validAccessPolicy,
    invertAssetCollectionSwitches: invertAssetCollectionSwitches,
    showServicesPanel: showServicesPanel,
    sessionExpiredModalOpen: sessionExpiredModalOpen,
    loginRedirect: loginRedirect,
    refetchAssetStatus: refetchAssetStatus,
    projectIdColor: projectIdColor,
    accessPolicyTitleColor: accessPolicyTitleColor,
    activePage: {current: null, set: null},
    queryParams: {},
  };
  return dataModel;
}

function getPage(allStates, pageMapper) {
  const curr_array = [null, null, null, null, null];
  for (const [key, value] of Object.entries(allStates)) {
    const idx = pageMapper.order.get(key);
    curr_array[idx] = value.status.current;
  }
  for (let ii = 0; ii < curr_array.length; ii++) {
    if (curr_array[ii] !== 'BLOCKED') {
      pageMapper.stateCache[ii] = curr_array[ii];
    }
  }
  return {
    page: pageMapper.map.get(pageMapper.stateCache),
    connectionEnabled: pageMapper.connectionEnabled[pageMapper.stateCache],
  };
}

export {DataModel, getPage, webhook_name_default};
