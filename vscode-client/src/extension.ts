/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */

/* --------------------------------------------------------------------------------------------
 * Additions Copyright (c) 2019 Seven Bridges. All rights reserved.
 * Licensed under the Apache 2.0 License. See License.txt for license information.
 *
 * This file has been modified from the original LSP example published by Microsoft.
 * Code to drive the webview component code has been added.
 * ------------------------------------------------------------------------------------------ */

'use strict';

import * as net from 'net';

import {
  Selection, TextEditorRevealType,
  workspace, Disposable, ExtensionContext,
  commands, window, ViewColumn,
  Uri,
  WebviewPanel,
  DebugConsoleMode,
  OutputChannel
} from 'vscode';

import * as path from 'path';
import {
  LanguageClient, LanguageClientOptions,
  SettingMonitor, ServerOptions,
  ErrorAction, ErrorHandler, CloseAction, TransportKind
} from 'vscode-languageclient';

import { Md5 } from 'ts-md5'
import * as fs from 'fs'
import { openStdin } from 'process';
import { exec, execFileSync } from 'child_process';
import { homedir } from 'os';

import * as https from 'https'; 
import { IncomingMessage } from 'http';

import * as unzip from 'unzip-stream';
import * as tar from 'tar-fs';
import * as gunzip from 'gunzip-maybe';

const thispackage = require('../package.json');

const github_release_url = `https://github.com/denbi/denbi-benten/releases/download/${thispackage.version}/`;


type ActivateCallback = (executable: string, out_chan: OutputChannel, msg: string) => void;


export function activate(context: ExtensionContext) {
  const default_executable = workspace.getConfiguration().get('benten.server.path');
  get_language_server(default_executable, (executable, out_chan, msg) => {
    if (executable === null) {
      window.showErrorMessage("Benten (CWL). Error trying to install/use server. Please look at log.");
      out_chan.show();
    } else {
      activate_server(executable, context);
      activate_preview(context);
      if (msg != null) {
        window.showInformationMessage(msg);
      }
    }
  });
}


export function activate_server(executable: string, context: ExtensionContext) {
  const args = ["--debug"]
  context.subscriptions.push(startLangServer(executable, args, ["cwl"]));
}


function startLangServer(command: string, args: string[], documentSelector: string[]): Disposable {
  const serverOptions: ServerOptions = {
    command,
    args,
  };
  const clientOptions: LanguageClientOptions = {
    outputChannelName: 'Benten (CWL): Log',
    documentSelector: documentSelector,
    synchronize: { configurationSection: "cwl" }
  }
  return new LanguageClient(command, serverOptions, clientOptions).start();
}


function startLangServerTCP(addr: number, documentSelector: string[]): Disposable {
  const serverOptions: ServerOptions = function () {
    return new Promise((resolve, reject) => {
      var client = new net.Socket();
      client.connect(addr, "127.0.0.1", function () {
        resolve({
          reader: client,
          writer: client
        });
      });
    });
  }

  const clientOptions: LanguageClientOptions = {
    documentSelector: documentSelector,
  }
  return new LanguageClient(`tcp lang server (port ${addr})`, serverOptions, clientOptions).start();
}


function get_user_dir() {
  return process.env.APPDATA ||
    process.env.XDG_DATA_HOME ||
    (process.platform == 'darwin' ?
      path.join(homedir(), "Library", "Preferences") :
      path.join(homedir(), ".local", "share"));
}


function get_scratch_dir() {
  const scratch_directory = path.join(get_user_dir(), "sevenbridges", "benten", "scratch")
  console.log(`scratch directory: ${scratch_directory}`)
  return scratch_directory
}


const preview_scratch_directory = get_scratch_dir();


function benten_ls_exists(executable: string) {
  try {
    execFileSync(executable, ["-h"]);
    return true;
  } catch (e) {
    return false;
  }
}


function show_err_msg(msg: string) {
  console.error(msg)
  window.showErrorMessage(msg);
}


function get_language_server(default_executable, callback: ActivateCallback) {

  const out_chan = window.createOutputChannel("Benten (CWL): Download");

  if(default_executable) {
    if (benten_ls_exists(default_executable)) {
      out_chan.appendLine(`Found user specified server ${default_executable}.`);
      callback(default_executable, out_chan, null);
      return;
    } else {
      const msg = `Can not run user specified server ${default_executable}. Fix the path in Benten settings, or remove to install server automatically.`;
      window.showErrorMessage(msg);
      out_chan.appendLine(msg);
      return;
    }
  }

  const pipx_executable = "benten-ls";
  if (benten_ls_exists(pipx_executable)) {
    out_chan.appendLine("Found pip/pipx installed benten-ls.");
    callback(pipx_executable, out_chan, null);
    return;
  } else {
    out_chan.appendLine("No pipx installed benten-ls found.");
  }

  const userdir = get_user_dir();
  const sbgdir = path.join(userdir, "sevenbridges", "benten");
  const executable = path.join(sbgdir, `benten-${thispackage.version}`, "benten-ls");
  if (benten_ls_exists(executable)) {
    out_chan.appendLine(`Found server: ${executable}`);
    callback(executable, out_chan, null);
    return;
  } else {
    out_chan.appendLine(`No downloaded benten-ls found (${executable}).`);
  }

  const pkgname = `benten-ls-${process.platform}.zip`;
  // https://nodejs.org/api/process.html#process_process_platform
  // 'aix', 'darwin', 'freebsd', 'linux', 'openbsd', 'sunos', 'win32'

  window.showInformationMessage(`Trying to download Benten (CWL) language server ${thispackage.version}`);


  fs.mkdir(sbgdir, { recursive: true }, (err) => {
    if (err) {
      // Fatal: Couldn't make the directory
      out_chan.appendLine(`Failed to create directory: ${sbgdir}. This is where the downloaded Benten server binaries would have been stored.`);
      callback(null, out_chan, null);
    }

    // Download from github releases page
    const package_url = `${github_release_url}/${pkgname}`;
    out_chan.appendLine(`Downloading server code from ${package_url}`);
    get_redirect(package_url, out_chan, (response) => {
      if (response === null) {
        callback(null, out_chan, null);
      }

      const server_response = `Server response: ${response.statusCode} ${response.statusMessage}`;
      if (response.statusCode != 200) {
        out_chan.appendLine(`Failed to download Benten server binary from ${package_url}. ${server_response}`);
        callback(null, out_chan, null);
      } else {
        out_chan.appendLine(server_response);
      }

      // The github zip contains only one file: benten-ls.tar.gz
      response.pipe(unzip.Parse())
        .on('entry', (entry) => {
          entry.pipe(gunzip()).pipe(tar.extract(sbgdir))
            .on('finish', () => {
              out_chan.appendLine("Extracted server binary!");
              callback(executable, out_chan, `Installed Benten ${thispackage.version} from ${package_url}`);
            })
            .on('error', (e) => {
              out_chan.appendLine(`Error extracting Benten server binary: ${e}`);
              out_chan.show();
              callback(null, out_chan, null);
            });
        });
    });
  });
}


type ResponseCallback = (response: IncomingMessage) => void;


function get_redirect(url: string, out_chan: OutputChannel,  callback: ResponseCallback) {
  https.get(url, (response) => {
    if (response.headers.location) {
      var loc = response.headers.location;
      out_chan.appendLine(`Redirect to: ${loc.toString()}`);
      get_redirect(loc, out_chan, callback);
    } else {
      callback(response);
    }
  }).on('error', (e) => {
    out_chan.appendLine(`Failed trying to download Benten server binaries from ${url}. Site responded with ${e}`);
    out_chan.show();
    callback(null);
  });
}


export function activate_preview(context: ExtensionContext) {  
  context.subscriptions.push(
    commands.registerCommand('cwl.show_graph', () => {

      // Create and show panel
      const panel = window.createWebviewPanel(
        'preview',
        'CWL Preview',
        ViewColumn.Two,
        {
          enableScripts: true,
          localResourceRoots: [
            Uri.file(path.join(context.extensionPath, 'include')),
            Uri.file(preview_scratch_directory)
          ]
        }
      );

      const on_disk_files: any = {}
      const files = ["vis-network.min.js", "vis-network.min.css"]
      for (let f of files) {
        on_disk_files[f] = panel.webview.asWebviewUri(Uri.file(
          path.join(context.extensionPath, 'include', f)))
      }

      // And set its HTML content
      updateWebviewContent(panel, on_disk_files)

      // Handle interactions on the graph
      panel.webview.onDidReceiveMessage(
        message => {
          for (let te of window.visibleTextEditors) {
            if (te.document.uri.toString() === message.uri) {
              let line = te.document.lineAt(parseInt(message.line))
              te.selection = new Selection(line.range.start, line.range.end)
              te.revealRange(line.range, TextEditorRevealType.InCenter)
              break
            }
          }
        },
        undefined,
        context.subscriptions
      );

      // When we switch tabs we want the view to update
      // But we don't need this because we have onDidChangeTextEditorSelection
      window.onDidChangeActiveTextEditor(
        e => {
          updateWebviewContent(panel, on_disk_files)
        },
        null,
        context.subscriptions
      )

      // We update the diagram each time we change the text
      window.onDidChangeTextEditorSelection(
        e => {
          updateWebviewContent(panel, on_disk_files)
        },
        null,
        context.subscriptions
      )

    })
  );

}


function updateWebviewContent(panel: WebviewPanel, on_disk_files: [string, Uri]) {

  const activeEditor = window.activeTextEditor;
  if (!activeEditor) {
    return;
  }
  const graph_name = Md5.hashStr(activeEditor.document.uri.toString()) + ".json"

  const data_uri = path.join(preview_scratch_directory, graph_name);
  var graph_data = JSON.parse(fs.readFileSync(data_uri, "utf8"));

  panel.webview.html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Benten: ${activeEditor.document.uri.toString()}</title>

		<script type="text/javascript" src="${on_disk_files["vis-network.min.js"]}"></script>
		<link href="${on_disk_files["vis-network.min.css"]}" rel="stylesheet" type="text/css" />

		<style type="text/css">

		html, body {
			width: 100%;
			height: 100%;
			margin: 0;
			padding: 0;
			overflow: hidden;
			font-family: sans-serif;
			background-color: white;
		}

    #cwl-graph {
      width: 100%;
      height: 100%;
      border: 1px solid lightgray;
    }
  </style>

</head>
<body>

	<div id="cwl-graph"></div>

	<script type="text/javascript">

  // create an array with nodes
  var nodes = new vis.DataSet(${JSON.stringify(graph_data["nodes"])})
  var edges = new vis.DataSet(${JSON.stringify(graph_data["edges"])})

	// metadata for scrolling to nodes
	var line_numbers = ${JSON.stringify(graph_data["line-numbers"])}

  // create a network
  var container = document.getElementById('cwl-graph');
  var data = {
    nodes: nodes,
    edges: edges
  };

  var options = {
    "autoResize": true,
    "interaction": {
      "tooltipDelay": 50,
			"navigationButtons": false
    },
		"manipulation": { "enabled": false },
		"nodes": {
      "shape": "dot",
      "borderWidth": 2
    },
    "edges": {
      "arrows": {
        "to": {
          "enabled": true,
          "scaleFactor": 0.5
        }
      },
      "smooth": {
        "type": "cubicBezier",
        "roundness": 0.6
      }
    },
    "groups": {
      "useDefaultGroups": true,
      "inputs": {
        "color": "#00AA28",
        "shadow": {"enabled": false}
      },
      "outputs": {
        "color": "#FFFF00",
        "shadow": {"enabled": false}
      },
      "steps": {
        "color": "#0000FF",
        "shadow": {"enabled": true}
      }
    },
    "layout": {
      "hierarchical": {
        "enabled": true,
        "levelSeparation": 100,
        "direction": "LR",
        "sortMethod": "directed"
      }
    }
  }

  var network = new vis.Network(container, data, options);
	const vscode = acquireVsCodeApi();

	// From https://visjs.github.io/vis-network/examples/network/events/interactionEvents.html
	// From https://code.visualstudio.com/api/extension-guides/webview#passing-messages-from-a-webview-to-an-extension

	network.on("selectNode", function (params) {
		const node_id = params.nodes[0]
		vscode.postMessage({
			"uri": "${activeEditor.document.uri.toString()}",
			"line": line_numbers[node_id]});
	});

</script>

</body>
</html>`;
}
