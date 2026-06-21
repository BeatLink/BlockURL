const DEFAULT_SYNC_SERVER_URL = "http://127.0.0.1:8000"

function normalizeURL(url) {
    return url.endsWith('/') ? url.slice(0, -1) : url
}

// Load Sync Settings -------------------------------------------------------------------------------------------------
async function loadSyncSettings() {
    console.log("Loading Sync Server URL")
    const settings = await browser.storage.sync.get("syncServerURL")
    document.getElementById("sync-server-url").value = settings["syncServerURL"] || DEFAULT_SYNC_SERVER_URL
}

// Save Sync Settings -------------------------------------------------------------------------------------------------
async function saveSyncSettings() {
    console.log("Saving Sync Server URL")
    const input = document.getElementById("sync-server-url")
    const url = normalizeURL(input.value.trim())
    input.value = url
    await browser.storage.sync.set({ "syncServerURL": url })
    showSavedConfirmation()
    browser.tabs.reload()
}

// Brief visual confirmation that settings were saved -----------------------------------------------------------------
function showSavedConfirmation() {
    const button = document.getElementById("save-sync-button")
    const originalText = button.textContent
    button.textContent = "Saved"
    setTimeout(() => { button.textContent = originalText }, 1200)
}

// Initialization -----------------------------------------------------------------------------------------------------
function initialize() {
    console.log("Loading Options Page")
    document.getElementById("save-sync-button").addEventListener("click", saveSyncSettings)
    loadSyncSettings()
}
initialize()