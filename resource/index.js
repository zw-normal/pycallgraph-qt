import {FunctionCallTree} from "./function_call_tree";

(function () {
    "use strict";

    const qWebChannel = require("qwebchannel");
    qWebChannel.QWebChannel(qt.webChannelTransport, function (channel) {
        const signalHub = channel.objects.signalHub;
        const funcCallTree = new FunctionCallTree();

        signalHub.funcCallersTreeGet.connect(function (callersTree) {
            funcCallTree.render(JSON.parse(callersTree));
        });

        signalHub.funcDefTreeFuncSel.connect(function (funcId) {
            signalHub.getFuncCallersTree(funcId);
        });
    });
}());
