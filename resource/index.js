import {FunctionCallDot} from "./function_call_dot";

(function () {
    "use strict";

    const qWebChannel = require("qwebchannel");
    qWebChannel.QWebChannel(qt.webChannelTransport, function (channel) {
        const signalHub = channel.objects.signalHub;
        const funcCallDot = new FunctionCallDot(signalHub);

        signalHub.funcCallDotProgress.connect(function (message) {
            funcCallDot.showProgress(message);
        });

        signalHub.funcCallDotGet.connect(function (callDot) {
            funcCallDot.render(callDot);
        });

        signalHub.funcCallDotSave.connect(function () {
            funcCallDot.saveAsPng();
        });
    });
}());
