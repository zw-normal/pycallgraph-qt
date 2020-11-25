import {FunctionCallDot} from "./function_call_dot";

(function () {
    "use strict";

    const qWebChannel = require("qwebchannel");
    qWebChannel.QWebChannel(qt.webChannelTransport, function (channel) {
        const signalHub = channel.objects.signalHub;
        const funcCallDot = new FunctionCallDot();

        signalHub.funcCallersDotGet.connect(function (callersDot) {
            funcCallDot.render(callersDot);
        });

        signalHub.funcDefTreeFuncSel.connect(function (funcId) {
            signalHub.getFuncCallersDot(funcId);
        });
    });
}());
