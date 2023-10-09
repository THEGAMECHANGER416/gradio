import { getWorkerProxyContext } from "./context";

type MediaSrc = string | undefined | null;

export async function resolve_wasm_src(src: MediaSrc): Promise<MediaSrc> {
	if (src == null) {
		return src;
	}

	const url = new URL(src);
	if (url.host !== window.location.host) {
		return src;
	}
	if (url.protocol !== "http" && url.protocol !== "https") {
		// `src` can be a data URL.
		return src;
	}

	const maybeWorkerProxy = getWorkerProxyContext();
	if (maybeWorkerProxy == null) {
		// We are not in the Wasm env. Just use the src as is.
		return src;
	}

	const path = url.pathname;
	return maybeWorkerProxy
		.httpRequest({
			method: "GET",
			path,
			headers: {},
			query_string: ""
		})
		.then((response) => {
			if (response.status !== 200) {
				throw new Error(`Failed to get file ${path} from the Wasm worker.`);
			}
			const blob = new Blob([response.body], {
				type: response.headers["Content-Type"]
			});
			const blobUrl = URL.createObjectURL(blob);
			return blobUrl;
		});
}
