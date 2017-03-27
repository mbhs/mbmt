function request(url) {
    return new Promise(function(resolve, reject) {
        var request = new XMLHttpRequest();
        request.open("GET", url, true);
        request.onreadystatechange = function() {
            if (this.state < 200 || this.status >= 300)
                reject({staus: this.status, statusText: this.statusText});
            else if (this.readyState == 4) {
                console.log(JSON.parse(this.responseText));
                resolve(JSON.parse(this.responseText));
            }
        };
        this.onerror = function() {
            reject({status: this.status, statusText: this.statusText});
        };
        request.send();
    });
}

var scoreboards = {
    Ramanujan: document.getElementById("ramanujan").getElementsByTagName("tbody")[0],
    Pascal: document.getElementById("pascal").getElementsByTagName("tbody")[0],
};

function update() {
    request("/live/guts/update/").then(function(scoreboard) {
        for (var division in scoreboard) {
            if (scoreboard.hasOwnProperty(division)) {
                var teams = [];
                for (var team in scoreboard[division])
                    if (scoreboard[division].hasOwnProperty(team))
                        teams.push(team);
                teams.sort(function(a, b) {
                    return scoreboard[division][b] - scoreboard[division][a];
                });
                while (scoreboards[division].firstChild)
                    scoreboards[division].removeChild(scoreboards[division].firstChild);
                for (var i = 0; i < teams.length; i++)
                    scoreboards[division].innerHTML += (
                        "<tr><td>" + teams[i] + "</td><td>" +
                        Math.round(scoreboard[division][teams[i]]*1000)/1000 +
                        "</td></tr>");
            }
        }
    });
}
