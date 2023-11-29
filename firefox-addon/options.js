// Initialization =====================================================================================================
function initialize() {
    loadSyncSettings()
    loadSettings()
    loadUrls()
}


// Sync Settings ======================================================================================================

// Load Sync Settings ----------------------------------------------------------------------------------
async function loadSyncSettings() {
    console.log(await browser.storage.sync.get("syncServerURL"))
    document.getElementById("sync-server-url").value = (await browser.storage.sync.get("syncServerURL"))["syncServerURL"];
}

// Save Sync Settings ----------------------------------------------------------------------------------
async function saveSyncSettings() {
    await browser.storage.sync.set({"syncServerURL": document.getElementById("sync-server-url").value});
}


// Settings ===========================================================================================================
function getSetting(key, onDone){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/settings/get`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"key": key}));
    })
}

function saveSetting(key, value, onDone) {
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/settings/set`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"key": key, "value": value}));
    })
}


// Load Settings ----------------------------------------------------------------------------------
function loadSettings() {
    getSetting("blocked_page_heading_text", (xhttp) => {
        document.getElementById("heading-text-entry").value = JSON.parse(xhttp.responseText)
    })

    getSetting("blocked_page_body_text", (xhttp) => {
        document.getElementById("body-text-entry").value = JSON.parse(xhttp.responseText)
    })

    getSetting("blocked_page_button_text", (xhttp) => {
        document.getElementById("button-text-entry").value = JSON.parse(xhttp.responseText)
    })
}

// Save Settings ----------------------------------------------------------------------------------
function saveSettings() {
    saveSetting("blocked_page_heading_text", document.getElementById("heading-text-entry").value,(xhttp) => {})
    saveSetting("blocked_page_body_text", document.getElementById("body-text-entry").value,(xhttp) => {})
    saveSetting("blocked_page_button_text", document.getElementById("button-text-entry").value,(xhttp) => {})
}

// URLS ===============================================================================================================
function getAllUrls(onDone) {
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("GET", `${settings["syncServerURL"]}/urls/all`, true);
        xhttp.send();
    })
}

function unblockURL(url, onDone){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/urls/unblock`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"url": `${url}`}));
    })
}

function blockURL(url, onDone) {
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/urls/block`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"url": url}));
    })
}


// Load URLs --------------------------------------------------------------------------------------
function loadUrls(){
    getAllUrls((xhttp) => {
        var urls = JSON.parse(xhttp.responseText)
        var urlsList = document.getElementById("urls-list")
        urlsList.innerHTML = "";
        for (let url of urls){
            var urlRow = document.createElement("li")
            urlRow.textContent = url
            urlRow.addEventListener("click", deleteUrl)
            urlsList.appendChild(urlRow)
        }
    })
}

// Delete URL ----------------------------------------------------------------------------------------
function deleteUrl(event){
    var url = event.target.innerHTML
    if (confirm(`Delete ${url}?`)) {
        unblockURL(decodeURI(url), (xhttp) => {
            loadUrls()
        })
    } 
}

// Add URL ----------------------------------------------------------------------------------------
function addUrl() {
    var url = document.getElementById("add-url-entry").value
    blockURL(url, (xhttp) => {
        loadUrls()
    })
}



// Export URLs ------------------------------------------------------------------------------------
function exportUrls() {
    getAllUrls((xhttp) => {
        var urls = JSON.parse(xhttp.responseText)
        let urlsString = setToStr(urls)
        var exportLink = document.createElement('a');
        exportLink.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(urlsString));
        exportLink.setAttribute('download', "urls.txt");    
        exportLink.style.display = 'none';
        document.body.appendChild(exportLink);
        exportLink.click();
        document.body.removeChild(exportLink);    
    })
}

// Appends a list of urls from file to the current list -------------------------------------------
function appendUrls(){
    const [file] = document.getElementById("urls-file-button").files;
    const reader = new FileReader();  
    reader.addEventListener("load", () => { 
        var urls = strToSet(reader.result)
        for (url of urls){
            blockURL(url, (xhttp) => {})    
        }
        loadUrls()
    }, false);
    if (file) {reader.readAsText(file)}    
}


function setToStr(urls){
    var string = ""
    for (let url of urls){
        string += url
        string += "\n"
    }
    return string
}

function strToSet(string, existingSet = new Set([])){
    for (let url of string.split("\n")){
        if (url){
            existingSet.add(url)
        }
    }
    return existingSet
}




document.addEventListener("DOMContentLoaded", initialize);
document.getElementById("save-sync-button").addEventListener("click", saveSyncSettings);
document.getElementById("save-settings-button").addEventListener("click", saveSettings);
document.getElementById("add-url-button").addEventListener("click", addUrl);
document.getElementById("export-urls-button").addEventListener("click", exportUrls);
document.getElementById("append-urls-button").addEventListener("click", appendUrls);

