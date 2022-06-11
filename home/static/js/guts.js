let scoreboards;
let frozen = false;

function update() {

  console.log("Updating...");
  if (frozen) console.log("Didn't update!");

  $.ajax("/grading/live/guts/update/").then(scores => {
    scores = JSON.parse(scores);

    for (let division of Object.keys(scores)) {
      const teams = [];
      for (const team in scores[division])
        if (scores[division].hasOwnProperty(team))
          teams.push(team);
      teams.sort((a, b) => scores[division][b] - scores[division][a]);

      scoreboards[division + "1"].empty();
      scoreboards[division + "2"].empty();

      const half = Math.ceil(teams.length / 2);

      for (let i = 0; i < teams.length; i++)
        scoreboards[division + (i < half ? "1" : "2")].append(
          "<tr><td>" + (i + 1) + "</td>" +
          "<td class='team'>" + teams[i] + "</td>" +
          "<td>" + Math.round(scores[division][teams[i]] * 1000) / 1000 + "</td></tr>");
    }
    console.log("Updated scoreboard!");
  }, error => console.log(error));
}

function freeze() {
  frozen = !frozen;
  if (frozen) document.getElementById("freeze").innerHTML = "Frozen!";
  else document.getElementById("freeze").innerHTML = "Freeze!"
}

window.onload = function() {
  scoreboards = {};
  for (let scoreboard of document.getElementsByClassName("scoreboard-body"))
    scoreboards[scoreboard.id] = $(scoreboard);
  update();
  setInterval(update, 25*1000);
};
