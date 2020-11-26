import * as d3 from "d3";

const dot = require("graphlib-dot");
const dagreD3 = require("dagre-d3");

import './index.css';

export class FunctionCallDot {

    constructor() {
    }

    render(callDot) {
        d3.select("#call-graph-plot").selectAll("*").remove();
        const svg = d3.select("#call-graph-plot").append("svg");
        const g = svg.append("g");

        const zoom = function zoomed({transform}) {
            g.attr("transform", transform);
        };

        const digraph = dot.read(callDot);
        for (const edge of digraph.edges()) {
            digraph.setEdge(edge.v, edge.w, {curve: d3.curveBasis});
        }
        const render = new dagreD3.render();
        render(g, digraph);

        d3.selectAll("g.node").on("dblclick", function() {
             console.log(d3.select(this).data());
        });

        const {x, y, width, height} = svg.node().getBBox();
        svg.call(
            d3.zoom()
                .extent([[x, y], [width, height]])
                .scaleExtent([0.1, 8])
                .on("zoom", zoom)).on("dblclick.zoom", null);
    }
}
