import {FunctionCallTree} from "./function_call_tree";

(function () {
    "use strict";

    const qWebChannel = require("qwebchannel");
    qWebChannel.QWebChannel(qt.webChannelTransport, function (channel) {
        const signalHub = channel.objects.signalHub;

        signalHub.funcCallersTreeGet.connect(function (callersTree) {
            new FunctionCallTree(JSON.parse(callersTree));
        });

        signalHub.funcDefTreeFuncSel.connect(function (funcId) {
            console.log(funcId);
            // signalHub.getFuncCallersTree(funcId);
        });

        // Testing
        signalHub.getFuncCallersTree(1);
    });
}());
