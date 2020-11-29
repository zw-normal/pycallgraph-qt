import * as d3 from "d3";

const dot = require("graphlib-dot");
const dagreD3 = require("dagre-d3");
const exportPng = require("save-svg-as-png");

import './index.css';

export class FunctionCallDot {

    constructor(signalHub) {
        this.signalHub = signalHub;
        this.render.bind(this);
    }

    clear() {
        d3.select("#call-graph-plot").selectAll("*").remove();
    }

    showProgress(message) {
        this.clear();
        d3.select("#call-graph-plot")
            .append("span")
            .text(message);
    }

    saveAsPng() {
        if (document.querySelector("#call-graph-plot svg")) {
            exportPng.saveSvgAsPng(
                document.querySelector("#call-graph-plot svg"),
                'function-call-graph.png',
                { backgroundColor: 'white' }
            );
        }
    }

    render(callDot) {
        const self = this;

        self.clear();
        const svg = d3.select("#call-graph-plot").append("svg");
        const g = svg.append("g");

        const zoom = function zoomed({transform}) {
            g.attr("transform", transform);
        };

        const digraph = dot.read(callDot);
        const render = new dagreD3.render();
        render(g, digraph);

        d3.selectAll("g.node").on("dblclick", function() {
            self.signalHub.funcCallDotNodeSel(d3.select(this).data()[0]);
        });

        const {x, y, width, height} = svg.node().getBBox();
        svg.call(
            d3.zoom()
                .extent([[x, y], [width, height]])
                .scaleExtent([0.1, 8])
                .on("zoom", zoom)).on("dblclick.zoom", null);
    }
}
