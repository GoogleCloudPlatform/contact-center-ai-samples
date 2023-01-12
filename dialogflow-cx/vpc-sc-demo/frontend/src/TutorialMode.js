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
import Switch from '@mui/material/Switch';

function StatusTutorialMode(props) {
  return <div>{props.state.status.current ? 'True' : 'False'}</div>;
}

function ToggleStatusTutorialMode(props) {
  function onChange() {
    props.state.status.set(!props.state.status.current);
  }

  return (
    <>
      {
        <Switch
          onChange={onChange}
          checked={
            typeof props.state.status.current === 'boolean'
              ? props.state.status.current
              : false
          }
          color="primary"
        />
      }
    </>
  );
}

export {StatusTutorialMode, ToggleStatusTutorialMode};
