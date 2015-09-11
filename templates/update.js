var returned = true;
var last_content = "";
function request() {
    if (!returned)
        return;
    returned = false;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function() {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            returned = true;
            update(xmlhttp.responseText);
        }
    };
    var target = "{{ target_url }}";
    xmlhttp.open("GET", target, true);
    xmlhttp.send();
}

function update(data) {
    if (data != last_content) {
        document.getElementById("{{ div }}").innerHTML = data;
        last_content = data;
    }
}

window.onload=function() {
    window.setInterval(request, 1000 * {{ update_interval }});
}

