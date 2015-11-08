var keyhash = "";
var changehash = false;
var notificationArea;
var timeout;

function hashkey(e) {
    return e.keyCode + ";" + e.charCode;
}

function clickNextSpeaker() {
    var link = document.getElementById("next-statement-button");
    link.click();
}

window.onkeypress = function(e) {
    if (changehash) {
        keyhash = hashkey(e);
        changehash = false;
        sessionStorage["keyhash"] = keyhash;
        notificationArea.innerHTML = "Key has been set.";
        timeout = window.setTimeout(function() { notificationArea.innerHTML = ""; }, 5000);
    } else {
        if (hashkey(e) == keyhash) {
            clickNextSpeaker();
        }
    }
};

function setkeyhash() {
    changehash = true;
    notificationArea.innerHTML = "Please click the key.";
    window.clearTimeout(timeout);
}

var nextbuttoncachedonloadfunction = window.onload;
window.onload = function() {
    nextbuttoncachedonloadfunction();
    if (sessionStorage["keyhash"]) {
        keyhash = sessionStorage["keyhash"];
    }
    notificationArea = document.getElementById("rede-layout-notification");
};
