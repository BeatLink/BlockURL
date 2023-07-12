// Initialization ---------------------------------------------------------------------------------
function initialize() {
    loadSettings()
    loadUrls()
}

// Load Settings ----------------------------------------------------------------------------------
function loadSettings() {
    browser.storage.local.get("settings").then((items) => {
        document.getElementById("heading-text-entry").value = items.settings.headingText
        document.getElementById("body-text-entry").value = items.settings.bodyText
        document.getElementById("button-text-entry").value = items.settings.buttonText
    });
}

// Save Settings ----------------------------------------------------------------------------------
function saveSettings() {
    var settings = {
        "headingText": document.getElementById("heading-text-entry").value,
        "bodyText":  document.getElementById("body-text-entry").value,
        "buttonText": document.getElementById("button-text-entry").value
    }
    browser.storage.local.set({settings});
}

// Add URL ----------------------------------------------------------------------------------------
function addUrl() {
    browser.storage.local.get("urls").then((items) => {
        var urls = items.urls
        var url = document.getElementById("add-url-entry").value
        urls.add(url)
        browser.storage.local.set({urls})
        loadUrls()
    })
}

// Delete URL ----------------------------------------------------------------------------------------
function deleteUrl(event){
    browser.storage.local.get("urls").then((items) => {
        var urls = items.urls
        var url = event.target.innerHTML
        if (confirm(`Delete ${url}?`)) {
            urls.delete(url)
            browser.storage.local.set({urls})
            loadUrls()
        } 
    })
}

// Load URLs --------------------------------------------------------------------------------------
function loadUrls(){
    browser.storage.local.get("urls").then((items) => {
        var urlsList = document.getElementById("urls-list")
        urlsList.innerHTML = "";
        for (let url of items.urls){
            var urlRow = document.createElement("li")
            urlRow.textContent = url
            urlRow.addEventListener("click", deleteUrl)
            urlsList.appendChild(urlRow)
        }
  })
}

// Export URLs ------------------------------------------------------------------------------------
function exportUrls() {
    browser.storage.local.get("urls").then((items) => {
        let urls = setToStr(items.urls)
        var exportLink = document.createElement('a');
        exportLink.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(urls));
        exportLink.setAttribute('download', "urls.txt");    
        exportLink.style.display = 'none';
        document.body.appendChild(exportLink);
        exportLink.click();
        document.body.removeChild(exportLink);    
    })
}

// Replaces the list of URLS from file ------------------------------------------------------------
function replaceUrls() {
    const [file] = document.getElementById("urls-file-button").files;
    const reader = new FileReader();  
    reader.addEventListener("load", () => { 
        var urls = strToSet(reader.result)
        browser.storage.local.set({urls})
        loadUrls()
    }, false);
    if (file) {reader.readAsText(file)}
}

// Appends a list of urls from file to the current list -------------------------------------------
function appendUrls(){
    browser.storage.local.get("urls").then((items) => {
        const [file] = document.getElementById("urls-file-button").files;
        const reader = new FileReader();  
        reader.addEventListener("load", () => { 
            var urls = strToSet(reader.result, items.urls)
            browser.storage.local.set({urls})
            loadUrls()
        }, false);
        if (file) {reader.readAsText(file)}
    
    })
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
document.getElementById("save-settings-button").addEventListener("click", saveSettings);
document.getElementById("add-url-button").addEventListener("click", addUrl);
document.getElementById("export-urls-button").addEventListener("click", exportUrls);
document.getElementById("replace-urls-button").addEventListener("click", replaceUrls);
document.getElementById("append-urls-button").addEventListener("click", appendUrls);

