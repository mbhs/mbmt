
const present = $("#present").append("<tbody>");
const absent = $("#absent").append("<tbody>");
const students = [];



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
  $.ajax("/grading/api/attendance/").then(data => {

    while (present.lastChild) present.removeChild(present.lastChild);

    for (let row of JSON.parse(data)) {
      let student = new Student(row);
      students.push(student);

      if (student.attending) {
        let item = $(
          "<tr><td>" + student.name + "</td>" +
          "<td>" + student.school + "</td>" +
          "<td><a href='" + "" + "'>Mark absent</a></td></tr>");
          items.push(item);
          present.append(item);
      }
      else {
        let item = $(
          "<tr><td>" + student.name + "</td>" +
          "<td>" + student.school + "</td>" +
          "<td><a href='" + "" + "'>Mark present</a></td></tr>");
        items.push(item);
        absent.append(item);
      }

    }
  }, error => {

  });
}


get();
