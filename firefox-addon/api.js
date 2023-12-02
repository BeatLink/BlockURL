// Helper Functions ===================================================================================================
export function removeTrailingSlashes(urls){
    urls.forEach(function(url, index, array) {
        array[index] = url.endsWith('/') ? url.slice(0, -1) : url;
    });
    return urls
}

function sendPOST(endpoint, payload, callback, callbackArgs){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const syncServerURL = settings["syncServerURL"]
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { callback(xhttp, callbackArgs) }
        xhttp.open("POST", `${syncServerURL}/${endpoint}`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify(payload));
    })
}

function sendGET(endpoint, callback, callbackArgs){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const syncServerURL = settings["syncServerURL"]
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { callback(xhttp, callbackArgs) }
        xhttp.open("GET", `${syncServerURL}/${endpoint}`, true);
        xhttp.send();
    })
}

// Settings Functions =================================================================================================
export function getSetting(key, callback, callbackArgs){
    sendPOST("settings/get", {"key": key}, callback, callbackArgs)
}

export function saveSetting(key, value, callback, callbackArgs) {
    sendPOST("settings/set", {"key": key, "value": value}, callback, callbackArgs)
}

// URL Functions ======================================================================================================
export function getAllURLs(callback, callbackArgs) {
    sendGET("urls/all", callback, callbackArgs)
}

export function queryURLs(urls, callback, callbackArgs){
    urls = removeTrailingSlashes(urls)
    sendPOST("urls/check", {"urls": urls}, callback, callbackArgs)
}

export function blockURLs(urls, callback, callbackArgs) {
    urls = removeTrailingSlashes(urls)
    sendPOST("urls/block", {"urls": urls}, callback, callbackArgs)
}

export function unblockURLs(urls, callback, callbackArgs){
    urls = removeTrailingSlashes(urls)
    sendPOST("urls/unblock", {"urls": urls}, callback, callbackArgs)
}
