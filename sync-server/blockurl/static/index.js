import { getSetting, saveSetting, getSortedURLs, blockURLs, unblockURLs } from "./api.js"

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
    for (var key in settingsDict) {
        document.getElementById(settingsDict[key]).value = ""
        document.getElementById(settingsDict[key]).value = await getSetting(key)
    }
}

// Save Settings ------------------------------------------------------------------------------------------------------
function saveSettings() {
    console.log("Saving Settings")
    for (var key in settingsDict) {
        saveSetting(
            key,
            document.getElementById(settingsDict[key]).value,
            (response) => { }
        )
    }
}

// URLS ===============================================================================================================

let urlsTable = null

// Load URLs ----------------------------------------------------------------------------------------------------------
async function loadURLs() {
    console.log("Loading URLs")
    var urls = await getSortedURLs("created_at", true, null)

    if (!urlsTable) {
        urlsTable = new Tabulator("#urls-table", {
            data: urls,
            layout: "fitColumns",
            placeholder: "No URLs blocked yet",
            columns: [
                {
                    title: "URL",
                    field: "url",
                    widthGrow: 3,
                    formatter: "link",
                    formatterParams: { target: "_blank" }
                },
                {
                    title: "Domain",
                    field: "domain",
                    widthGrow: 1,
                    headerFilter: "input"
                },
                {
                    title: "Added",
                    field: "created_at",
                    widthGrow: 1,
                    sorter: "string"
                },
                {
                    title: "",
                    width: 90,
                    hozAlign: "center",
                    headerSort: false,
                    formatter: () => "<button class='table-delete-btn'>Delete</button>",
                    cellClick: async (e, cell) => {
                        const url = cell.getRow().getData().url
                        await deleteURL(url)
                    }
                }
            ],
            initialSort: [{ column: "created_at", dir: "desc" }],
            height: "auto",
            pagination: true,
            paginationSize: 50,
            paginationSizeSelector: [25, 50, 100, 250],
        })
    } else {
        urlsTable.setData(urls)
    }
}

// Delete URL ---------------------------------------------------------------------------------------------------------
async function deleteURL(url) {
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
    document.getElementById("add-url-entry").value = ""
    await loadURLs()
}

// Export URLs --------------------------------------------------------------------------------------------------------
async function exportURLs() {
    console.log("Exporting URLs")
    var urls = await getSortedURLs("created_at", true, null)
    let urlsString = urls.map((entry) => entry.url).join("\n")
    var exportLink = document.createElement('a')
    exportLink.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(urlsString))
    exportLink.setAttribute('download', "urls.txt")
    exportLink.style.display = 'none'
    document.body.appendChild(exportLink)
    exportLink.click()
    document.body.removeChild(exportLink)
}

// AppendURLs ---------------------------------------------------------------
function appendURLs() {
    console.log("Appending URLs from File")
    const [file] = document.getElementById("urls-file-button").files
    const reader = new FileReader()
    reader.addEventListener("load", async () => {
        var urls = reader.result.split("\n")
        urls = urls.filter((entry) => { return entry.trim() != '' })
        await blockURLs(urls)
        await loadURLs()
    }, false)
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

document.addEventListener("DOMContentLoaded", initialize)
document.getElementById("save-settings-button").addEventListener("click", saveSettings)
document.getElementById("add-url-button").addEventListener("click", addURL)
document.getElementById("export-urls-button").addEventListener("click", exportURLs)
document.getElementById("append-urls-button").addEventListener("click", appendURLs)