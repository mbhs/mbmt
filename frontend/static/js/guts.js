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

var scoreboards;

function update() {
    request("/live/guts/update/").then(function(scores) {
        for (var division in scores) {
            if (scores.hasOwnProperty(division)) {
                var teams = [];
                for (var team in scores[division])
                    if (scores[division].hasOwnProperty(team))
                        teams.push(team);
                teams.sort(function(a, b) {
                    return scores[division][b] - scores[division][a];
                });

                while (scoreboards[division].firstChild)
                    scoreboards[division].removeChild(scoreboards[division].firstChild);
                console.log(scoreboards[division]);
                for (var i = 0; i < teams.length; i++)
                    scoreboards[division].insertRow().innerHTML += (
                        "<td>" + teams[i] + "</td><td>" +
                        Math.round(scores[division][teams[i]]*1000)/1000 +
                        "</td>");
            }
        }
    });
}

window.onload = function() {
    scoreboards = {
        Ramanujan: document.getElementById("ramanujan").getElementsByTagName("tbody")[0],
        Pascal: document.getElementById("pascal").getElementsByTagName("tbody")[0]};
    update();
    setInterval(update, 30*1000);
};
