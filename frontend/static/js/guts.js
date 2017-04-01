function request(url) {
    return new Promise(function(resolve, reject) {
        var request = new XMLHttpRequest();
        request.open("GET", url, true);
        request.onreadystatechange = function() {
            if (this.state < 200 || this.status >= 300)
                reject({staus: this.status, statusText: this.statusText});
            else if (this.readyState == 4) {
                resolve(JSON.parse(this.responseText));
            }
        };
        this.onerror = function() {
            reject({status: this.status, statusText: this.statusText});
        };
        request.send();
    });
}

var scoreboards;
var frozen = false;

function update() {
    if (!frozen) {
        request("/live/guts/update/").then(function (scores) {
            for (var division in scores) {
                if (scores.hasOwnProperty(division)) {
                    var teams = [];
                    for (var team in scores[division])
                        if (scores[division].hasOwnProperty(team))
                            teams.push(team);
                    teams.sort(function (a, b) {
                        return scores[division][b] - scores[division][a];
                    });

                    console.log(scoreboards);
                    while (scoreboards[division+"1"].firstChild)
                        scoreboards[division+"1"].removeChild(scoreboards[division+"1"].firstChild);
                    while (scoreboards[division+"2"].firstChild)
                        scoreboards[division+"2"].removeChild(scoreboards[division+"2"].firstChild);

                    var half = Math.ceil(teams.length / 2);

                    for (var i = 0; i < teams.length; i++)
                        scoreboards[division + (i < half ? "1" : "2")].insertRow().innerHTML += (
                            "<td>" + (i + 1) + "</td>" +
                            "<td class=\"team\">" + teams[i] + "</td>" +
                            "<td>" + Math.round(scores[division][teams[i]] * 1000) / 1000 + "</td>");
                }
            }
            console.log("Updated scoreboard!");
        });
    } else {
        console.log("Didn't update!");
    }
}

function freeze() {
    frozen = !frozen;
    if (frozen) document.getElementById("freeze").innerHTML = "Frozen!";
    else document.getElementById("freeze").innerHTML = "Freeze!"
}

window.onload = function() {
    scoreboards = {
        ramanujan1: document.getElementById("ramanujan1"),
        ramanujan2: document.getElementById("ramanujan2"),
        pascal1: document.getElementById("pascal1"),
        pascal2: document.getElementById("pascal2")};
    update();
    setInterval(update, 25*1000);
};
