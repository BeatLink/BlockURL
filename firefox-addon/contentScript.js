/*
    This content script runs on every page. First it queries the api to find out if the page should be blocked. 
    If the page should be blocked, it loads the blocked page
    If the page shouldn't be blocked, instead it checks to see if links within the page should be blocked
*/

// Helper Functions ===================================================================================================

function queryURL(url, onDone, onDoneArgs){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        url = url.endsWith('/') ? url.slice(0, -1) : url;
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp, onDoneArgs) }
        xhttp.open("POST", `${settings["syncServerURL"]}/urls/check`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"url": url}));
    })
}

function unblock(){
    browser.runtime.sendMessage({unblockRequested: window.location.href})
}

function getSetting(key, onDone){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/settings/get`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"key": key}));
    })
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
    
    getSetting("blocked_page_heading_text", (xhttp)=>{
        heading.textContent = xhttp.responseText.replaceAll('"', '');
    })
    
    getSetting("blocked_page_body_text", (xhttp) => {
        body.textContent = xhttp.responseText.replaceAll('"', '')
    })
    
    getSetting("blocked_page_button_text", (xhttp) => {
        button.textContent = xhttp.responseText.replaceAll('"', '')
    })
}

// Block Links on page ================================================================================================
function blockLinks(){
    console.log("Blocking matching links on current page")

    // Create CSS Class for blocked links
    var css = '.blockurl-hide { display: none !important; }'
    var head = document.head || document.getElementsByTagName('head')[0]
    var style = document.createElement('style');
    head.appendChild(style);
    style.appendChild(document.createTextNode(css));

    var links = document.getElementsByTagName("a");
    var length = links.length
    for (var i = 0; i < length; i++) {
        console.log(links[i].href)
        queryURL(links[i].href, (xhttp, link) => {
            if (JSON.parse(xhttp.responseText)){
                link.classList.add("blockurl-hide")
            }    
        }, links[i])
    }     
}

// Main ===============================================================================================================
function main_script() {
    console.log("Checking to see if page should be blocked")
    queryURL(window.location.href, (xhttp) => {
        if (JSON.parse(xhttp.responseText)) {
            blockPage()
        } else {
            // Block applicable links currently on the page
            blockLinks()

            // Setup an observer to monitor the DOM for changes and reblock any URLs
            const observer = new MutationObserver((mutationList, observer) => { blockLinks() });
            observer.observe(head, { attributes: true, childList: true, subtree: true });
        }
    })
}

main_script()
