import commonjs from "rollup-plugin-commonjs";
import nodeResolve from "rollup-plugin-node-resolve";
import sourcemaps from 'rollup-plugin-sourcemaps';

export default {
    entry: "./lib/webapp/index.js",

    targets: [{
        dest: "./dist/webapp.js",
        format: "iife",
        sourceMap: true,
    }],

    plugins: [
        // Resolves npm packages from node_modules
        nodeResolve({
            browser: true,
            jsnext: true,
        }),

        commonjs(),

        // Parses existing sourcemaps (e.g. sourcemaps produced by TypeScript)
        sourcemaps(),
    ]
};
