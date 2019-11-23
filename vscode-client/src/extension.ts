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
	workspace, Disposable, ExtensionContext, 
	commands, window, ViewColumn,
	Uri, 
	WebviewPanel
} from 'vscode';
import * as path from 'path';
import { 
	LanguageClient, LanguageClientOptions, 
	SettingMonitor, ServerOptions, 
	ErrorAction, ErrorHandler, CloseAction, TransportKind 
} from 'vscode-languageclient';

import {Md5} from 'ts-md5'
import * as fs from 'fs'


function startLangServer(command: string, args: string[], documentSelector: string[]): Disposable {
	const serverOptions: ServerOptions = {
        command,
        args,
	};
	const clientOptions: LanguageClientOptions = {
		documentSelector: documentSelector,
    synchronize: { configurationSection: "cwl" }
	}
	return new LanguageClient(command, serverOptions, clientOptions).start();
}


function startLangServerTCP(addr: number, documentSelector: string[]): Disposable {
	const serverOptions: ServerOptions = function() {
		return new Promise((resolve, reject) => {
			var client = new net.Socket();
			client.connect(addr, "127.0.0.1", function() {
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

const preview_scratch_directory = get_scratch_dir()

function get_scratch_dir() {
	const homedir = require('os').homedir()
	const scratch_directory = 
		process.env.XDG_DATA_HOME ? 
				process.env.XDG_DATA_HOME 
			: path.join(homedir, ".local", "share", "sevenbridges", "benten", "scratch") 
	console.log(`scratch directory: ${scratch_directory}`)
	return scratch_directory
}


export function activate(context: ExtensionContext) {
	
	// For the language server
	const executable = "benten-ls"
	const args = ["--debug"]
	context.subscriptions.push(startLangServer(executable, args, ["cwl"]));
    // For TCP server needs to be started separately
    // context.subscriptions.push(startLangServerTCP(2087, ["python"]));


	// For the preview
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
			const files = ["vis.js", "vis-network.min.css"]
			for(let f of files) {
				on_disk_files[f] = Uri.file(
					path.join(context.extensionPath, 'include', f))
					.with({ scheme: 'vscode-resource' })
			}

			// And set its HTML content
			updateWebviewContent(panel, on_disk_files)

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
		
		<script type="text/javascript" src="${on_disk_files["vis.js"]}"></script>
		<link href="${on_disk_files["vis-network.min.css"]}" rel="stylesheet" type="text/css" />

		<style type="text/css">

		html, body {
			width: 100%;
			height: 100%;
			margin: 0;
			padding: 0;
			overflow: hidden;
			font-family: sans-serif;
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
      "navigationButtons": true
    },
    "nodes": {
      "shape": "dot",
      "borderWidth": 2
    },
    "manipulation": {
      "enabled": false
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
</script>

</body>
</html>`;
}
