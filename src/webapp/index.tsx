import { h, render } from "preact";
import { GraphAPI } from "../core/facebook-client";
import { App } from "./App";

// tslint:disable-next-line:no-console
console.log(new GraphAPI(""));

render(<App />, document.getElementById("react-root") as HTMLElement);
