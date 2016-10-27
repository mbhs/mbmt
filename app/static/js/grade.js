var students = $($($("#students").children()[0]).children()[0]).children();
var teams = $($($("#teams").children()[0]).children()[0]).children();
var search = $("#search");

search.focus();

function update() {
    for (var i = 0; i < students.length; i++) {
        var student = $(students[i + 1]);

        if ($(student.children()[0]).text().toLowerCase().startsWith(search.val().toLowerCase())) student.show();
        else student.hide();
    }

    for (var i = 0; i < teams.length; i++) {
        var team = $(teams[i+1]);

        if ($(team.children()[1]).text().toLowerCase().startsWith(search.val().toLowerCase())) team.show();
        else team.hide();
    }
}