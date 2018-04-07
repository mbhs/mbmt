
const present = $("<tbody>");
$("#present").append(present);
const absent = $("<tbody>");
$("#absent").append(absent);
const students = [];

const loading = $("#loading");
loading.css("visibility", "hidden");

const items = [];
const search = $("#search");

search.focus();

function update() {
    for (let i = 0; i < items.length; i++) {
        let item = items[i];
        if ($(item.children()[0]).text().toLowerCase().includes(search.val().toLowerCase())) item.show();
        else item.hide();
    }
}


class Student {

  constructor(row) {
    this.id = row[0];
    this.name = row[1];
    this.school = row[3];
    this.attending = row[2];
  }

}

function get() {

  loading.css("visibility", "visible");
  $.ajax("/grading/api/attendance/?_=" + new Date().getTime()).then(data => {

    present.empty();
    absent.empty();

    for (let row of JSON.parse(data)) {
      let student = new Student(row);
      students.push(student);

      if (student.attending) {
        let item = $(
          "<tr><td>" + student.name + "</td>" +
          "<td>" + student.school + "</td>" +
          "<td><a id='mark-" + student.id + "' onclick='post(" + student.id + ", false)'>Mark absent</a></td></tr>");
          items.push(item);
          present.append(item);
      } else {
        let item = $(
          "<tr><td>" + student.name + "</td>" +
          "<td>" + student.school + "</td>" +
          "<td><a id='mark-" + student.id + "' onclick='post(" + student.id + ", true)'>Mark present</a></td></tr>");
        items.push(item);
        absent.append(item);
      }
    }

    loading.css("visibility", "hidden");
  }, error => {
    window.alert("Failed to access attendance API.");
    loading.css("visibility", "hidden");
  });
}


function post(id, attending) {
  $.post("/grading/api/attendance/", {id: id, attending: attending}).then(() => {
    $("#mark-" + id).text("Awaiting refresh");
    setTimeout(get, 300);
  })
}


get();

setInterval(get, 15*1000);
