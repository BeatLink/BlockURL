// Helper Functions ===================================================================================================
export function removeTrailingSlashes(urls){
    urls.forEach(function(url, index, array) {
        array[index] = url.endsWith('/') ? url.slice(0, -1) : url;
    });
    return urls
}

async function sendRequest(method, endpoint, payload=null) {
    let requests = {
        "GET": new Request(`/${endpoint}`),
        "POST": new Request(
            `/${endpoint}`, 
            {
                method: "POST",
                headers: { "Content-Type": "application/json;charset=UTF-8" },
                body: JSON.stringify(payload)
            }
        )    
    }
    return (await fetch(requests[method])).json()
}

// Settings Functions =================================================================================================
export async function getSetting(key){
    return await sendRequest("POST", "settings/get", {"key": key})
}

export async function saveSetting(key, value) {
    return await sendRequest("POST", "settings/set", {"key": key, "value": value})
}

// URL Functions ======================================================================================================
export async function getAllURLs() {
    return await sendRequest("GET", "urls/all")
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
