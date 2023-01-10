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

const LOGIN_COOKIE_NAME = 'user_logged_in';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function deleteCookie(name) {
  if (getCookie(name)) {
    document.cookie = `${name}=;domain=${window.location.hostname};expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  }
}

function handleTokenExpired(dataModel) {
  dataModel.projectData.principal.set(null);
  dataModel.sessionExpiredModalOpen.set(true);
  deleteCookie(LOGIN_COOKIE_NAME);
}

function getBucket(dataModel) {
  return `${dataModel.projectData.project_id.current}-vpcsc-demo`;
}

export {handleTokenExpired, getCookie, LOGIN_COOKIE_NAME, getBucket};
