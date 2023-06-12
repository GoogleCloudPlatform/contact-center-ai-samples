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

import React, {useState} from 'react';
import {IconButton, Snackbar} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import SyntaxHighlighter from 'react-syntax-highlighter';

const CopyToClipboardButton = props => {
  const [open, setOpen] = useState(false);

  const handleClick = () => {
    setOpen(true);
    navigator.clipboard.writeText(props.text);
  };

  return (
    <>
      <IconButton onClick={handleClick} color="primary">
        <ContentCopyIcon />
      </IconButton>
      <Snackbar
        message="Copied to clibboard"
        anchorOrigin={{vertical: 'top', horizontal: 'center'}}
        autoHideDuration={2000}
        onClose={() => setOpen(false)}
        open={open}
      />
    </>
  );
};

function SnippetWithCopyButton(props) {
  return (
    <Card
      sx={{
        maxWidth: '700px',
        minWidth: '75%',
        my: 2,
        py: 0,
        ml: 4,
        justifyContent: 'flex-start',
      }}
    >
      <CardContent>
        <Grid container alignItems="center" direction="row">
          <Grid item>
            <CopyToClipboardButton text={props.code} />
          </Grid>
          <Grid item>
            <Typography color="text.secondary">{props.title}</Typography>
          </Grid>
        </Grid>
        <SyntaxHighlighter language={props.language}>
          {props.code}
        </SyntaxHighlighter>
      </CardContent>
    </Card>
  );
}

export {SnippetWithCopyButton};
