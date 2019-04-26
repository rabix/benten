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


function startLangServer(command: string, args: string[], documentSelector: string[]): Disposable {
	const serverOptions: ServerOptions = {
        command,
        args,
	};
	const clientOptions: LanguageClientOptions = {
		documentSelector: documentSelector,
        synchronize: {
            configurationSection: "cwl"
        }
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

export function activate(context: ExtensionContext) {
	
	// For the language server
	const executable = "benten-ls.sh"
	const args = ["--debug"]
	context.subscriptions.push(startLangServer(executable, args, ["cwl"]));
    // For TCP server needs to be started separately
    // context.subscriptions.push(startLangServerTCP(2087, ["python"]));


	// For the preview
	context.subscriptions.push(
		commands.registerCommand('cwl.show_graph', () => {

			const activeEditor = window.activeTextEditor;

			// Create and show panel
			const panel = window.createWebviewPanel(
				'preview',
				'CWL Preview',
				ViewColumn.One,
				{
					enableScripts: true
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

			/*
			// When we switch tabs we want the view to update
			// But we don't need this because we have onDidChangeTextEditorSelection
			window.onDidChangeActiveTextEditor(
				e => {
					panel.webview.html = getWebviewContent()
				},
				null,
				context.subscriptions
			)
			*/
			
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
	const text = activeEditor.document.getText()

  panel.webview.html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Benten: CWL preview</title>
		
		<script type="text/javascript" src="${on_disk_files["vis.js"]}"></script>
		<link href="${on_disk_files["vis-network.min.css"]}" rel="stylesheet" type="text/css" />

		<style type="text/css">
    #cwl-graph {
      width: 600px;
      height: 400px;
      border: 1px solid lightgray;
    }
  </style>

</head>
<body>

	<div id="cwl-graph"></div>

	<script type="text/javascript">
  // create an array with nodes
  var nodes = new vis.DataSet([
    {id: 1, label: 'Node 1'},
    {id: 2, label: 'Node 2'},
    {id: 3, label: 'Node 3'},
    {id: 4, label: 'Node 4'},
    {id: 5, label: 'Node 5'},
    {id: 6, label: 'Node 6'},
    {id: 7, label: 'Node 7'},
    {id: 8, label: 'Node 8'}
  ]);

  // create an array with edges
  var edges = new vis.DataSet([
    {from: 1, to: 8, arrows:'to', dashes:true},
    {from: 1, to: 3, arrows:'to'},
    {from: 1, to: 2, arrows:'to, from'},
    {from: 2, to: 4, arrows:'to, middle'},
    {from: 2, to: 5, arrows:'to, middle, from'},
    {from: 5, to: 6, arrows:{to:{scaleFactor:2}}},
    {from: 6, to: 7, arrows:{middle:{scaleFactor:0.5},from:true}}
  ]);

  // create a network
  var container = document.getElementById('cwl-graph');
  var data = {
    nodes: nodes,
    edges: edges
  };
  var options = {};
  var network = new vis.Network(container, data, options);
</script>

		<pre>
			${text}
		</pre>
</body>
</html>`;
}
