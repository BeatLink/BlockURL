// Helper Functions ===================================================================================================
export function removeTrailingSlashes(urls) {
    urls.forEach(function (url, index, array) {
        array[index] = url.endsWith('/') ? url.slice(0, -1) : url
    })
    return urls
}

async function sendRequest(method, endpoint, payload = null) {
    const settings = await browser.storage.sync.get(["syncServerURL", "apiKey"])
    let syncServerURL = settings["syncServerURL"]

    if (!syncServerURL) {
        console.error("BlockURL: syncServerURL is not set. Configure it in the extension options.")
        throw new Error("syncServerURL is not configured")
    }

    syncServerURL = syncServerURL.endsWith('/') ? syncServerURL.slice(0, -1) : syncServerURL

    const apiKey = settings["apiKey"] || ""
    const authHeaders = apiKey ? { "X-API-Key": apiKey } : {}

    let request
    if (method === "GET") {
        request = new Request(`${syncServerURL}/${endpoint}`, { mode: 'cors', headers: authHeaders })
    } else {
        request = new Request(
            `${syncServerURL}/${endpoint}`,
            {
                method: "POST",
                mode: 'cors',
                headers: { "Content-Type": "application/json;charset=UTF-8", ...authHeaders },
                body: JSON.stringify(payload)
            }
        )
    }

    try {
        const response = await fetch(request)
        if (!response.ok) {
            console.error(`BlockURL: sync server returned ${response.status} for ${endpoint}`)
            throw new Error(`Sync server error: ${response.status}`)
        }
        return await response.json()
    } catch (error) {
        console.error(`BlockURL: failed to reach sync server at ${syncServerURL} (${endpoint})`, error)
        throw error
    }
}

// Settings Functions =================================================================================================
export async function getSetting(key) {
    return await sendRequest("POST", "settings/get", { "key": key })
}

// URL Functions =======================================================================================================
export async function getAllURLs() {
    return await sendRequest("GET", "urls/all", null)
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