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
import {Document, Page} from 'react-pdf';
import diagram_sd from './VPC_SC_diagram_latest.pdf';
import Paper from '@mui/material/Paper';
import {getPage} from './DataModel.js';
import {pdfjs} from 'react-pdf';
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function ArchitectureImage(props) {
  const isLoading = props.renderedPageNumber.current !== props.currPage;
  return (
    <Paper variant="string" sx={{width: props.width, height: props.pageHeight}}>
      <Document file={diagram_sd} loading="loading_slides">
        {isLoading && props.renderedPageNumber.current ? (
          <Page
            key={props.renderedPageNumber.current}
            className="prevPage"
            pageNumber={props.renderedPageNumber.current}
            height={props.pageHeight}
            loading=""
          />
        ) : null}
        <Page
          key={props.currPage}
          pageNumber={props.currPage}
          height={props.pageHeight}
          onRenderSuccess={() => {
            props.renderedPageNumber.set(props.currPage);
          }}
          loading=""
        />
      </Document>
    </Paper>
  );
}

function StateImage(props) {
  const renderedPageNumber = props.dataModel.renderedPageNumber;
  const allStates = props.dataModel.allStates;
  const pageMapper = props.dataModel.pageMapper;
  const currPage = getPage(allStates, pageMapper).page
    ? getPage(allStates, pageMapper).page
    : 33;

  return ArchitectureImage({
    renderedPageNumber: renderedPageNumber,
    currPage: currPage,
    pageHeight: 300,
    width: 750,
  });
}

export {StateImage, ArchitectureImage};
