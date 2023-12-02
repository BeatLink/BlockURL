/*
    This content script runs on every page. First it queries the api to find out if the page should be blocked. 
    If the page should be blocked, it loads the blocked page
    If the page shouldn't be blocked, instead it checks to see if links within the page should be blocked
*/

// Helper Functions ===================================================================================================

import(browser.runtime.getURL('api.js')).then((module) => {

    function queryURLs (urls, callback, callbackArgs){
        module.queryURLs(urls, callback, callbackArgs)
    }

    function unblock(){
        browser.runtime.sendMessage({unblockRequested: window.location.href})
    }

    // Blocking Page ======================================================================================================
    "use strict";

    function blockPage(){
        console.log("Blocking: " + window.location.href);

        // Setup Document
        document.documentElement.innerHTML = '';
        document.body.style = `
            margin: 0;
            background-color: #f6f6f6; 
            color: #000;
            font-size: 16px;
            font-family: sans-serif; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            width:100%;
        `

        // Create Header
        const heading = document.createElement("h1");
        heading.style = `
            color: #000;
            background-color: #f6f6f6; 
            font-family: sans-serif; 
            font-size: 4em;
            font-weight: normal;
            margin: 0.25em;
            padding: 0.25em;
            border-bottom: 1px solid #a2a9b1;
            overflow: hidden;
        `
        document.body.appendChild(heading);
        
        // Create Paragraph
        const body = document.createElement('p')
        body.style = `
            color: #000;
            font-family: sans-serif; 
            font-size: 1.5em;
            margin: 0;
        `
        document.body.appendChild(body)
        
        // Setup Button
        let button = document.createElement('button')
        button.style = `
            display: inline-flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            font-size: 1.5em;
            line-height: 1.2;
            color: #FFFFFF;
            background-color: #0088FF;
            margin: 1.5em;
            padding: 0.5em;
            border: 2px solid transparent;
            border-radius: 0.5em;
        `
        button.addEventListener("click", unblock);
        document.body.appendChild(button)

        let settingsDict = {
            "blocked_page_heading_text": heading,
            "blocked_page_body_text": body,
            "blocked_page_button_text": button
        }
        
        for (key in settingsDict){
            module.getSetting(key, (xhttp, key) => {
                settingsDict[key].textContent = xhttp.responseText.replaceAll('"', '');
            }, key)    
        }
    }

    // Block Links on page ================================================================================================
    function createBlockedLinksStyle(){
        // Create CSS Class for blocked links
        var css = '.blockurl-hide { display: none !important; }'
        var head = document.head || document.getElementsByTagName('head')[0]
        var style = document.createElement('style');
        head.appendChild(style);
        style.appendChild(document.createTextNode(css));
    }

    function blockLinks(){
        console.log("Blocking matching links on current page")
        createBlockedLinksStyle()
        var links = [...document.getElementsByTagName("a")];
        var urls = links.map((link) => link.href);        
        queryURLs(urls, (xhttp, links) => {
            var results = JSON.parse(xhttp.responseText)
            for (var link of links){
                var url = link.href 
                url = url.endsWith('/') ? url.slice(0, -1) : url;
                if (results[url]){
                    link.classList.add("blockurl-hide")
                }
            }
        }, links)
    }     



    // Main ===============================================================================================================
    function main_script() {
        console.log("Checking to see if page should be blocked")
        var url = window.location.href
        url = url.endsWith('/') ? url.slice(0, -1) : url;
        queryURLs([url], (xhttp) => {
            var results = JSON.parse(xhttp.responseText)
            if (results[url]) {
                blockPage()
            } else {
                blockLinks()
            }
        })
    }

    main_script()
})
