function request(url) {
    return new Promise(function(resolve, reject) {
        const request = new XMLHttpRequest();
        request.open("GET", url, true);
        request.onreadystatechange = () => {
            if (this.state < 200 || this.status >= 300)
                reject({staus: this.status, statusText: this.statusText});
            else if (this.readyState === 4) {
                resolve(JSON.parse(this.responseText));
            }
        };
        this.onerror = () => reject({status: this.status, statusText: this.statusText});
        request.send();
    });
}

let scoreboards;
let frozen = false;

function update() {
    if (frozen) console.log("Didn't update!");
    request("/grading/live/guts/update/").then(function(scores) {
        for (const division in scores) {
            if (scores.hasOwnProperty(division)) {
                const teams = [];
                for (const team in scores[division])
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

                const half = Math.ceil(teams.length / 2);

                for (const i = 0; i < teams.length; i++)
                    scoreboards[division + (i < half ? "1" : "2")].insertRow().innerHTML += (
                        "<td>" + (i + 1) + "</td>" +
                        "<td class=\"team\">" + teams[i] + "</td>" +
                        "<td>" + Math.round(scores[division][teams[i]] * 1000) / 1000 + "</td>");
            }
        }
        console.log("Updated scoreboard!");
    });
}

function freeze() {
    frozen = !frozen;
    if (frozen) document.getElementById("freeze").innerHTML = "Frozen!";
    else document.getElementById("freeze").innerHTML = "Freeze!"
}

window.onload = function() {
    scoreboards = {
        ramanujan1: document.getElementById("first1"),
        ramanujan2: document.getElementById("first2"),
        pascal1: document.getElementById("second1"),
        pascal2: document.getElementById("second2")};
    update();
    setInterval(update, 25*1000);
};
