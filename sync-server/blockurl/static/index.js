import { getSetting, saveSetting, getSortedURLs, blockURLs, unblockURLs, getStats } from "./api.js"

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

// METRICS ============================================================================================================

// Load Metrics -------------------------------------------------------------------------------------------------------
async function loadMetrics() {
    console.log("Loading Metrics")
    const stats = await getStats()
    document.getElementById("metric-total-urls").textContent = formatCount(stats["total_urls"])
    document.getElementById("metric-unique-domains").textContent = formatCount(stats["unique_domains"])
}

function formatCount(value) {
    return typeof value === "number" ? value.toLocaleString() : "0"
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
                    sorter: "string",
                    formatter: (cell) => {
                        const raw = cell.getValue()
                        if (!raw) return ""
                        // SQLite's datetime('now') returns UTC without a "Z" suffix;
                        // append it so the browser parses it as UTC instead of local time.
                        const date = new Date(raw.replace(' ', 'T') + 'Z')
                        if (isNaN(date.getTime())) return raw
                        return date.toLocaleString()
                    }
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
        await loadMetrics()
    }
}

// Add URL ------------------------------------------------------------------------------------------------------------
async function addURL() {
    console.log("Adding URL")
    var url = document.getElementById("add-url-entry").value
    await blockURLs([url])
    document.getElementById("add-url-entry").value = ""
    await loadURLs()
    await loadMetrics()
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
async function appendURLs() {
    console.log("Appending URLs from File")
    const [file] = document.getElementById("urls-file-button").files
    if (!file) {
        showImportStatus("Choose a file to import first.", true)
        return
    }

    showImportStatus(`Importing ${file.name}...`)
    let result
    try {
        const text = await file.text()
        const urls = text.split("\n").map((entry) => entry.trim()).filter((entry) => entry != '')
        if (urls.length == 0) {
            showImportStatus(`${file.name} contains no URLs.`, true)
            return
        }
        result = await blockURLsInBatches(urls)
    } catch (error) {
        console.error(error)
        showImportStatus(`Could not import ${file.name}: ${error.message}`, true)
        return
    }

    showImportStatus(describeImport(file.name, result))
    await loadURLs()
    await loadMetrics()
}

// Send a big import in server-sized batches and add up the counts -----------------------------------------------------
const IMPORT_BATCH_SIZE = 5000

async function blockURLsInBatches(urls) {
    const totals = { received: 0, added: 0, merged: 0 }
    for (let start = 0; start < urls.length; start += IMPORT_BATCH_SIZE) {
        const batch = urls.slice(start, start + IMPORT_BATCH_SIZE)
        const response = await blockURLs(batch)
        if (!response || typeof response["received"] != "number") {
            throw new Error(response && response["error"] ? response["error"] : "unexpected response from server")
        }
        totals.received += response["received"]
        totals.added += response["added"]
        totals.merged += response["merged"]
    }
    return totals
}

// Turn the server's import counts into a sentence ----------------------------------------------------------------------
function describeImport(fileName, result) {
    const received = formatCount(result["received"])
    const added = formatCount(result["added"])
    const merged = formatCount(result["merged"])
    return `Imported ${received} URLs from ${fileName}: ${added} added, ${merged} merged (already blocked or repeated).`
}

// Import Status Message ------------------------------------------------------------------------------------------------
function showImportStatus(message, isError = false) {
    const status = document.getElementById("import-status")
    status.textContent = message
    status.classList.toggle("error", isError)
    document.getElementById("import-status-row").hidden = false
}

// Initialization =====================================================================================================
async function initialize() {
    console.log("Loading Options Page")
    await loadSettings()
    await loadURLs()
    await loadMetrics()
}

document.addEventListener("DOMContentLoaded", initialize)
document.getElementById("save-settings-button").addEventListener("click", saveSettings)
document.getElementById("add-url-button").addEventListener("click", addURL)
document.getElementById("export-urls-button").addEventListener("click", exportURLs)
document.getElementById("append-urls-button").addEventListener("click", appendURLs)