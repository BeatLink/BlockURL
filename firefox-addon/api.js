// Helper Functions ===================================================================================================
export function removeTrailingSlashes(urls){
    urls.forEach(function(url, index, array) {
        array[index] = url.endsWith('/') ? url.slice(0, -1) : url;
    });
    return urls
}

async function sendRequest(method, endpoint, payload=null) {
    const settings = await browser.storage.sync.get("syncServerURL")
    const syncServerURL = settings["syncServerURL"]
    let requests = {
        "GET": new Request(`${syncServerURL}/${endpoint}`),
        "POST": new Request(
            `${syncServerURL}/${endpoint}`, 
            {
                method: "POST",
                RequestMode:'cors',
                headers: { "Content-Type": "application/json;charset=UTF-8" },
                body: JSON.stringify(payload)
            }
        )    
    }
    return (await fetch(requests[method])).json();
}

// Settings Functions =================================================================================================
export async function getSetting(key){
    return await sendRequest("POST", "settings/get", {"key": key})
}

// URL Functions ======================================================================================================
export async function getAllURLs() {
    return await sendRequest("GET", "urls/all", null)
}

export async function queryURLs(urls){
    urls = removeTrailingSlashes(urls)
    return await sendRequest("POST", "urls/check", {"urls": urls})
}

export async function blockURLs(urls) {
    urls = removeTrailingSlashes(urls)
    return await sendRequest("POST", "urls/block", {"urls": urls})
}

export async function unblockURLs(urls){
    urls = removeTrailingSlashes(urls)
    return await sendRequest("POST", "urls/unblock", {"urls": urls})
}
