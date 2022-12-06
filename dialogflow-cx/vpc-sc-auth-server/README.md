<!-- 
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. 
-->

# Developer Instructions

- Run all linters: `inv lint`
- Run one specific linter:
  - `inv lint --linter=terraform`
  - `inv lint --linter=javascript`
  - `inv lint --linter=black`
  - `inv lint --linter=isort`
  - `inv lint --linter=jscpd`
  - `inv lint --linter=flake8`
  - `inv lint --linter=pylint`
  - `inv lint --linter=mypy`
  - `inv lint --linter=bash`
  - `inv lint --linter=hadolint`
- Run automatic fix of lint improvements: `black . && isort .`
