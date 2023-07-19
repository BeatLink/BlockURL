"use strict";

console.log("Blocking: " + window.location.href);

function unblock(){
    browser.runtime.sendMessage({unblockRequested: window.location.href})
}

browser.storage.local.get("settings").then((items) => {

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
    heading.textContent = items.settings['headingText'];
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
    body.textContent = items.settings['bodyText']
    body.style = `
        color: #000;
        font-family: sans-serif; 
        font-size: 1.5em;
        margin: 0;
    `
    document.body.appendChild(body)

    // Setup Button
    let button = document.createElement('button')
    button.textContent = items.settings['buttonText']
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
})