/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
'use strict';

import * as net from 'net';

import { workspace, Disposable, ExtensionContext } from 'vscode';
import { LanguageClient, LanguageClientOptions, SettingMonitor, ServerOptions, ErrorAction, ErrorHandler, CloseAction, TransportKind } from 'vscode-languageclient';


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
    // const executable = workspace.getConfiguration("pyls").get<string>("executable");
	// const executable = ". ~/.venvs/benten/bin/activate && python -m benten"
	const executable = "sh"
	const args = ["/Users/kghose/Work/code/benten/vscode-client/start.sh"]
	context.subscriptions.push(startLangServer(executable, args, ["cwl"]));
    // For TCP server needs to be started seperately
    // context.subscriptions.push(startLangServerTCP(2087, ["python"]));
}