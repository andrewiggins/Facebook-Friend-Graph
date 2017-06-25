// Include the following lines for isomorphism
// if (!URL) {
//     // tslint:disable-next-line:no-var-requires
//     const { URL, URLSearchParams } = require("url");
// }
// import "isomorphic-fetch";

// Include the following for a Promise polyfill
// import "lie/polyfill";

namespace GraphAPI {
    export interface IQueryParams {
        [key: string]: string;
    }

    export interface IBody {
        [key: string]: string;
    }
}

const FACEBOOK_GRAPH_URL = "https://graph.facebook.com/";

export class GraphAPI {

    private version: string = "v2.9";

    constructor(private accessToken: string) {}

    private request(path: string, queryParams?: URLSearchParams, body?: GraphAPI.IBody, method: string = "GET"): Promise<any> {
        if (!queryParams) {
            queryParams = new URLSearchParams();
        }

        if (body) {
            method = "POST";
        }

        if (this.accessToken) {
            if (body && !("access_token" in body)) {
                body.access_token = this.accessToken;
            }
            else if (!("access_token" in queryParams)) {
                queryParams.set("access_token", this.accessToken);
            }
        }

        let requestUrl = new URL(FACEBOOK_GRAPH_URL + path);
        requestUrl.search = queryParams.toString();

        return fetch(requestUrl.toString(), { method, body }).then(res => res.json());
    }

}
