var keyhash_forward = "";
var keyhash_backward = "";
var changehash = 0;
var notificationArea;
var timeout;

function hashkey(e) {
    return e.keyCode + ";" + e.charCode;
}

function clickNextSpeaker() {
    var link = document.getElementById("next-statement-button");
    link.click();
}

function clickPreviousSpeaker() {
    var link = document.getElementById("previous-statement-button");
    link.click();
}

window.onkeypress = function(e) {
    if (changehash == 2) {
        keyhash_forward = hashkey(e);
        changehash = 1;
        sessionStorage["keyhash_forward"] = keyhash_forward;
        notificationArea.innerHTML = "Please click the backward key.";
    } else if (changehash == 1) {
        keyhash_backward = hashkey(e);
        changehash = 0;
        sessionStorage["keyhash_backward"] = keyhash_backward;
        notificationArea.innerHTML = "Both keys have been set.";
        timeout = window.setTimeout(function() { notificationArea.innerHTML = ""; }, 5000);
    } else {
        if (hashkey(e) == keyhash_forward) {
            clickNextSpeaker();
        } else if (hashkey(e) == keyhash_backward) {
            clickPreviousSpeaker();
        }
    }
};

function setkeyhash() {
    changehash = 2;
    notificationArea.innerHTML = "Please click the forward key.";
    window.clearTimeout(timeout);
}

var nextbuttoncachedonloadfunction = window.onload;
window.onload = function() {
    nextbuttoncachedonloadfunction();
    var found = false;
    if (sessionStorage["keyhash_forward"]) {
        keyhash_forward = sessionStorage["keyhash_forward"];
        found = true;
    }
    if (sessionStorage["keyhash_backward"]) {
        keyhash_backward = sessionStorage["keyhash_backward"];
        found = true;
    }
    notificationArea = document.getElementById("rede-layout-notification");
};
