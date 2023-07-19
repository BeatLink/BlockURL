browser.storage.local.get("urls").then((items) => {
    var links = document.getElementsByTagName("a");
    var length = links.length;
    for (var i = 0; i < length; i++) {
       if (items.urls.has(links[i].href)){
            links[i].style = "display: none !important"
       }
    }

})