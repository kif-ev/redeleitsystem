var {{ prefix }}returned = true;
var {{ prefix }}last_content = "";
var {{ prefix }}no_return_counter = 0;
var {{ prefix }}notification_div = null;
function {{ prefix }}request() {
    if (!{{ prefix }}returned) {
        {{ prefix }}no_return_counter += 1;
        console.log("Connection lost");
        if ({{ prefix }}no_return_counter > 5) {
            if ({{ prefix }}notification_div != null) {
                {{ prefix }}notification_div.innerHTML = "Connection lost, retrying";
                console.log("Retrying");
            }
        } else {
            return;
        }
    } else {
        if ({{ prefix }}notification_div.innerHTML == "Connection lost, retrying") {
            {{ prefix }}notification_div.innerHTML = "";
        }
    }
    {{ prefix }}returned = false;
    var {{ prefix }}xmlhttp = new XMLHttpRequest();
    {{ prefix }}xmlhttp.onreadystatechange=function() {
        if ({{ prefix }}xmlhttp.readyState == 4 && {{ prefix }}xmlhttp.status == 200) {
            {{ prefix }}returned = true;
            {{ prefix }}no_return_counter = 0;
            {{ prefix }}update({{ prefix }}xmlhttp.responseText);
        }
    };
    var {{ prefix }}target = "{{ target_url }}";
    {{ prefix }}xmlhttp.open("GET", {{ prefix }}target, true);
    {{ prefix }}xmlhttp.send();
}

function {{ prefix }}update({{ prefix }}data) {
    if ({{ prefix }}data != {{ prefix }}last_content) {
        document.getElementById("{{ div }}").innerHTML = {{ prefix }}data;
        {{ prefix }}last_content = {{ prefix }}data;
    }
}

var {{ prefix }}f = window.onload;
window.onload=function() {
    {{ prefix }}f();
    window.setInterval({{ prefix }}request, 1000 * {{ update_interval }});
    {{ prefix }}notification_div = document.getElementById("rede-layout-notification");
};

