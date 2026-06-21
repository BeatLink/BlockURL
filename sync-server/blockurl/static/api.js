// Helper Functions ===================================================================================================
export function removeTrailingSlashes(urls) {
    urls.forEach(function (url, index, array) {
        array[index] = url.endsWith('/') ? url.slice(0, -1) : url
    })
    return urls
}

async function sendRequest(method, endpoint, payload = null) {
    // Only build the Request object we actually need, instead of constructing
    // both a GET and a POST request on every call and discarding one.
    let request
    if (method === "GET") {
        request = new Request(`/${endpoint}`)
    } else {
        request = new Request(
            `/${endpoint}`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json;charset=UTF-8" },
                body: JSON.stringify(payload)
            }
        )
    }
    return (await fetch(request)).json()
}

// Settings Functions =================================================================================================
export async function getSetting(key) {
    return await sendRequest("POST", "settings/get", { "key": key })
}

export async function saveSetting(key, value) {
    return await sendRequest("POST", "settings/set", { "key": key, "value": value })
}

// URL Functions =======================================================================================================
export async function getAllURLs() {
    return await sendRequest("GET", "urls/all")
}

export async function queryURLs(urls) {
    urls = removeTrailingSlashes(urls)
    return await sendRequest("POST", "urls/check", { "urls": urls })
}

export async function blockURLs(urls) {
    urls = removeTrailingSlashes(urls)
    return await sendRequest("POST", "urls/block", { "urls": urls })
}

export async function unblockURLs(urls) {
    urls = removeTrailingSlashes(urls)
    return await sendRequest("POST", "urls/unblock", { "urls": urls })
}

export async function getSortedURLs(orderBy = "created_at", descending = true, domain = null) {
    return await sendRequest("POST", "urls/sorted", {
        "order_by": orderBy,
        "descending": descending,
        "domain": domain
    })
}

export async function getDomainsWithCounts() {
    return await sendRequest("GET", "urls/domains")
}