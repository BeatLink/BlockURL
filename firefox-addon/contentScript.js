/*
    This content script runs on every page. First it queries the api to find out if the page should be blocked.
    If the page should be blocked, it loads the blocked page
    If the page shouldn't be blocked, instead it checks to see if links within the page should be blocked
*/
"use strict"

async function blockURLContentScript() {
    function normalizeURL(url) {
        return url.endsWith('/') ? url.slice(0, -1) : url
    }
    // Unblock ============================================================================================================
    async function unblock() {
        let url = normalizeURL(window.location.href)
        try {
            await browser.runtime.sendMessage({ unblockRequested: [url] })
        } catch (err) {
            console.error("BlockURL: failed to send unblock message", err)
        }
    }
    // Blocking Page ======================================================================================================
    async function blockPage() {
        console.log("Blocking: " + window.location.href)
        const html = await (await fetch(browser.runtime.getURL("blocked.html"))).text()
        const parser = new DOMParser()
        const newDoc = parser.parseFromString(html, "text/html")
        // Rewrite relative stylesheet hrefs to extension-resource URLs.
        // Without this, the link would resolve against the current page's
        // origin (since we're injecting into the real page's document) and
        // silently fail to load.
        newDoc.head.querySelectorAll('link[rel="stylesheet"]').forEach((link) => {
            link.href = browser.runtime.getURL(link.getAttribute('href'))
        })
        document.head.replaceChildren(...newDoc.head.childNodes)
        document.body.replaceChildren(...newDoc.body.childNodes)
        var button = document.getElementById("button")
        button.addEventListener("click", unblock)
        let settingsDict = {
            "blocked_page_heading_text": document.getElementById("heading"),
            "blocked_page_body_text": document.getElementById("text"),
            "blocked_page_button_text": document.getElementById("button")
        }
        for (var key in settingsDict) {
            var response = await browser.runtime.sendMessage({ getSetting: key })
            settingsDict[key].textContent = response
        }
    }
    // Block Links on page ================================================================================================
    // Track elements we've already inspected and URLs we've already resolved
    // so that repeated DOM mutations don't trigger a full re-scan and
    // re-query of every link/image on the page every single time - only
    // genuinely new elements/URLs are sent to the sync server.
    const processedElements = new WeakSet()
    const urlBlockStatusCache = new Map() // url -> boolean (blocked?)

    async function blockLinks() {
        console.log("Blocking matching links on current page")
        var urlMap = new Object()
        var types = {
            "a": "href",
            "img": "src"
        }
        for (var type in types) {
            var elements = [...document.querySelectorAll(type)]
            elements.forEach((element, _) => {
                if (processedElements.has(element)) {
                    return
                }
                let url = element[types[type]]
                if (!url) {
                    return
                }
                url = normalizeURL(url)

                // Already know the answer for this URL from an earlier scan -
                // apply it immediately without going back to the server.
                if (urlBlockStatusCache.has(url)) {
                    if (urlBlockStatusCache.get(url)) {
                        element.style.setProperty('display', 'none', 'important')
                    }
                    processedElements.add(element)
                    return
                }

                if (url in urlMap) {
                    urlMap[url].push(element)
                } else {
                    urlMap[url] = []
                    urlMap[url].push(element)
                }
            })
        }
        var urls = Object.keys(urlMap)
        if (urls.length === 0) {
            // Nothing new to check - skip the round trip entirely.
            return
        }
        var response = await browser.runtime.sendMessage({ queryURLs: urls })
        for (var url in response) {
            urlBlockStatusCache.set(url, response[url])
            for (var element of urlMap[url]) {
                processedElements.add(element)
                if (response[url]) {
                    element.style.setProperty('display', 'none', 'important')
                }
            }
        }
    }
    // Debounced wrapper so rapid/frequent DOM mutations don't trigger a full
    // re-scan + re-query of every link on the page on every single change.
    let blockLinksTimeout = null
    function scheduleBlockLinks() {
        clearTimeout(blockLinksTimeout)
        blockLinksTimeout = setTimeout(blockLinks, 200)
    }
    // Main ===============================================================================================================
    async function main_script() {
        console.log("Checking to see if page should be blocked")
        var url = normalizeURL(window.location.href)
        // Prevents running on its own sync server page
        var settings = await browser.storage.sync.get("syncServerURL")
        var syncServerURL = settings["syncServerURL"]
        if (!syncServerURL) {
            return
        }
        syncServerURL = normalizeURL(syncServerURL)
        if (url == syncServerURL) {
            return
        }
        var response = await browser.runtime.sendMessage({ queryURLs: [url] })
        if (response[url]) {
            await blockPage()
        } else {
            const body = document.body
            const observerOptions = {
                childList: true,
                subtree: true,
            }
            const observer = new MutationObserver(scheduleBlockLinks)
            observer.observe(document.body, observerOptions)
            blockLinks()
        }
    }
    main_script()
}
blockURLContentScript()