/*
    This content script runs on every page. First it queries the api to find out if the page should be blocked.
    If the page should be blocked, it loads the blocked page
    If the page shouldn't be blocked, instead it checks to see if links within the page should be blocked
*/

"use strict";

async function blockURLContentScript() {
    // Unblock ============================================================================================================
    function unblock(){
        browser.runtime.sendMessage({unblockRequested: [window.location.href]})
    }

    // Blocking Page ======================================================================================================
    async function blockPage(){
        console.log("Blocking: " + window.location.href);
        const html = await (await fetch(browser.runtime.getURL("blocked.html"))).text()
        document.querySelector('html').innerHTML = html;
        var button = document.getElementById("button")
        button.addEventListener("click", unblock);
        let settingsDict = {
            "blocked_page_heading_text": document.getElementById("heading"),
            "blocked_page_body_text": document.getElementById("text"),
            "blocked_page_button_text": document.getElementById("button")
        }
        for (var key in settingsDict){
            var response = await browser.runtime.sendMessage({getSetting: key})
            settingsDict[key].textContent = response.replaceAll('"', '');
        }
    }

    // Block Links on page ================================================================================================
    async function blockLinks(){
        console.log("Blocking matching links on current page")
        // Find all blocked links and block them
        var urlMap = new Object();
        var types = {
            "a": "href",
            "img": "src"
        }
        for (var type in types){
            var elements = [...document.querySelectorAll(type)]
            elements.forEach((element, _) => {
                url = element[types[type]]
                url = url.endsWith('/') ? url.slice(0, -1) : url;
                if (url in urlMap) {
                    urlMap[url].push(element)
                } else {
                    urlMap[url] = []
                    urlMap[url].push(element)
                }

            })
        }
        var urls = Object.keys(urlMap)
        var response = await browser.runtime.sendMessage({queryURLs: urls})
        for (var url in response){
            if (response[url]) {
                for (var element of urlMap[url])
                element.style.setProperty('display', 'none', 'important');
            }
        }
    }

    // Main ===============================================================================================================
    async function main_script() {
        console.log("Checking to see if page should be blocked")
        var url = window.location.href
        url = url.endsWith('/') ? url.slice(0, -1) : url;
        var response = await browser.runtime.sendMessage({queryURLs: [url]})
        if (response[url]) {
            blockPage()
        } else {
            const body = document.body;
            const observerOptions = {
                childList: true,
                subtree: true,
            };

            const observer = new MutationObserver(blockLinks);
            observer.observe(document.body, observerOptions);

            blockLinks()
        }
    }
    main_script()
}

blockURLContentScript()
