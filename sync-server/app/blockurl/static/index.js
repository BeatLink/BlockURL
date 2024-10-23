import { getSetting, saveSetting, getAllURLs, blockURLs, unblockURLs } from "./api.js"

// Settings Management ================================================================================================

// Settings Dict ------------------------------------------------------------------------------------------------------
let settingsDict = {
    "blocked_page_heading_text": "heading-text-entry",
    "blocked_page_body_text": "body-text-entry",
    "blocked_page_button_text": "button-text-entry"
}

// Load Settings ------------------------------------------------------------------------------------------------------
async function loadSettings() {
    console.log("Loading Settings")
    for (var key in settingsDict){
        document.getElementById(settingsDict[key]).value = ""
        document.getElementById(settingsDict[key]).value = await getSetting(key)
    }
}

// Save Settings ------------------------------------------------------------------------------------------------------
function saveSettings() {
    console.log("Saving Settings")
    for (var key in settingsDict){ 
        saveSetting(
            key, 
            document.getElementById(settingsDict[key]).value, 
            (response) => {}
        ) 
    }
}

// URLS ===============================================================================================================

// Load URLs ----------------------------------------------------------------------------------------------------------
async function loadURLs(){
    console.log("Loading URLs")
    var urls = await getAllURLs()
    urls.sort()
    var urlsList = document.getElementById("urls-list")
    urlsList.innerHTML = "";
    for (let url of urls){
        var urlRow = document.createElement("li")
        var urlLink = document.createElement('a');
        urlLink.setAttribute('href', url);
        urlLink.innerHTML  = url;
        urlRow.appendChild(urlLink);
        let deleteButton = document.createElement("span");
        deleteButton.innerHTML = "Delete"
        deleteButton.addEventListener("click", deleteURL.bind(null, url))
        urlRow.appendChild(deleteButton)
        urlsList.appendChild(urlRow)
    }
}

// Delete URL ---------------------------------------------------------------------------------------------------------
async function deleteURL(url){
    console.log("Deleting URL")
    if (confirm(`Delete ${url}?`)) {
        await unblockURLs([url])
        await loadURLs()
    } 
}

// Add URL ------------------------------------------------------------------------------------------------------------
async function addURL() {
    console.log("Adding URL")
    var url = document.getElementById("add-url-entry").value
    await blockURLs([url])
    await loadURLs()
}

// Export URLs --------------------------------------------------------------------------------------------------------
async function exportURLs() {
    console.log("Exporting URLs")
    var urls = await getAllURLs()
    let urlsString = urls.join("\n")
    var exportLink = document.createElement('a');
    exportLink.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(urlsString));
    exportLink.setAttribute('download', "urls.txt");    
    exportLink.style.display = 'none';
    document.body.appendChild(exportLink);
    exportLink.click();
    document.body.removeChild(exportLink);    
}

// AppendURLs ---------------------------------------------------------------
function appendURLs(){
    console.log("Appending URLs from File")
    const [file] = document.getElementById("urls-file-button").files;
    const reader = new FileReader();  
    reader.addEventListener("load", async () => { 
        var urls = reader.result.split("\n")
        urls = urls.filter((entry) => { return entry.trim() != ''; });
        await blockURLs(urls)
        await loadURLs()
    }, false);
    if (file) { 
        reader.readAsText(file)
    }    
}

// Initialization =====================================================================================================
async function initialize() {
    console.log("Loading Options Page")
    await loadSettings()
    await loadURLs()
}

document.addEventListener("DOMContentLoaded", initialize);
document.getElementById("save-settings-button").addEventListener("click", saveSettings);
document.getElementById("add-url-button").addEventListener("click", addURL);
document.getElementById("export-urls-button").addEventListener("click", exportURLs);
document.getElementById("append-urls-button").addEventListener("click", appendURLs);

