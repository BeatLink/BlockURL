import { getSetting, saveSetting, getAllURLs, blockURLs, unblockURLs } from "/api.js"

// Sync Server ========================================================================================================

// Load Sync Settings -------------------------------------------------------------------------------------------------
async function loadSyncSettings() {
    console.log("Loading Sync Server URL")
    document.getElementById("sync-server-url").value = (await browser.storage.sync.get("syncServerURL"))["syncServerURL"];
}

// Save Sync Settings ----------------------------------------------------------------------------------
function saveSyncSettings() {
    console.log("Saving Sync Server URL")
    browser.storage.sync.set({"syncServerURL": document.getElementById("sync-server-url").value});
    browser.tabs.reload()
}


// Settings Management ================================================================================================

// Settings Dict ------------------------------------------------------------------------------------------------------
let settingsDict = {
    "blocked_page_heading_text": "heading-text-entry",
    "blocked_page_body_text": "body-text-entry",
    "blocked_page_button_text": "button-text-entry"
}

// Load Settings ------------------------------------------------------------------------------------------------------
function loadSettings() {
    console.log("Loading Settings")
    for (var key in settingsDict){
        document.getElementById(settingsDict[key]).value = ""
        getSetting(key, (xhttp, key) => { document.getElementById(settingsDict[key]).value = JSON.parse(xhttp.responseText) }, key)
    }
}

// Save Settings ------------------------------------------------------------------------------------------------------
function saveSettings() {
    console.log("Saving Settings")
    for (var key in settingsDict){ saveSetting(key, document.getElementById(settingsDict[key]).value, (xhttp) => {}) }
}

// URLS ===============================================================================================================

// Load URLs ----------------------------------------------------------------------------------------------------------
function loadURLs(){
    console.log("Loading URLs")
    getAllURLs((xhttp) => {
        var urls = JSON.parse(xhttp.responseText)
        urls.sort()
        var urlsList = document.getElementById("urls-list")
        urlsList.innerHTML = "";
        for (let url of urls){
            var urlRow = document.createElement("li")
            urlRow.textContent = url
            urlRow.addEventListener("click", deleteURL)
            urlsList.appendChild(urlRow)
        }
    })
}

// Delete URL ---------------------------------------------------------------------------------------------------------
function deleteURL(event){
    console.log("Deleting URL")
    var url = event.target.innerHTML
    if (confirm(`Delete ${url}?`)) {
        unblockURLs([decodeURI(url)], () => { loadURLs() })
    } 
}

// Add URL ------------------------------------------------------------------------------------------------------------
function addURL() {
    console.log("Adding URL")
    var url = document.getElementById("add-url-entry").value
    blockURLs([url], () => { loadURLs() })
}

// Export URLs --------------------------------------------------------------------------------------------------------
function exportURLs() {
    console.log("Exporting URLs")
    getAllURLs((xhttp) => {
        var urls = JSON.parse(xhttp.responseText)
        let urlsString = urls.join("\n")
        var exportLink = document.createElement('a');
        exportLink.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(urlsString));
        exportLink.setAttribute('download', "urls.txt");    
        exportLink.style.display = 'none';
        document.body.appendChild(exportLink);
        exportLink.click();
        document.body.removeChild(exportLink);    
    })
}

// AppendURLs ---------------------------------------------------------------
function appendURLs(){
    console.log("Appending URLs from File")
    const [file] = document.getElementById("urls-file-button").files;
    const reader = new FileReader();  
    reader.addEventListener("load", () => { 
        var urls = reader.result.split("\n")
        blockURLs(urls, (xhttp) => {loadURLs()})
    }, false);
    if (file) { 
        reader.readAsText(file)
    }    
}

// Initialization =====================================================================================================
function initialize() {
    console.log("Loading Options Page")
    loadSyncSettings()
    loadSettings()
    loadURLs()
}

document.addEventListener("DOMContentLoaded", initialize);
document.getElementById("save-sync-button").addEventListener("click", saveSyncSettings);
document.getElementById("save-settings-button").addEventListener("click", saveSettings);
document.getElementById("add-url-button").addEventListener("click", addURL);
document.getElementById("export-urls-button").addEventListener("click", exportURLs);
document.getElementById("append-urls-button").addEventListener("click", appendURLs);

