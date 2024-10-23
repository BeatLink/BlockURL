// Load Sync Settings -------------------------------------------------------------------------------------------------
async function loadSyncSettings() {
    console.log("Loading Sync Server URL")
    document.getElementById("sync-server-url").value = (await browser.storage.sync.get("syncServerURL"))["syncServerURL"];
}

// Save Sync Settings -------------------------------------------------------------------------------------------------
function saveSyncSettings() {
    console.log("Saving Sync Server URL")
    browser.storage.sync.set({"syncServerURL": document.getElementById("sync-server-url").value});
    browser.tabs.reload()
}

// Initialization -----------------------------------------------------------------------------------------------------
function initialize() {
    console.log("Loading Options Page")
    document.addEventListener("DOMContentLoaded", initialize);
    document.getElementById("save-sync-button").addEventListener("click", saveSyncSettings);    
    loadSyncSettings()
}

initialize()

