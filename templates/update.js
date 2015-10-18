var {{ prefix }}returned = true;
var {{ prefix }}last_content = "";
function {{ prefix }}request() {
    if (!{{ prefix }}returned)
        return;
    {{ prefix }}returned = false;
    var {{ prefix }}xmlhttp = new XMLHttpRequest();
    {{ prefix }}xmlhttp.onreadystatechange=function() {
        if ({{ prefix }}xmlhttp.readyState == 4 && {{ prefix }}xmlhttp.status == 200) {
            {{ prefix }}returned = true;
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
};

