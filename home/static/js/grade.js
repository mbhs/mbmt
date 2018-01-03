var items = $($(document.getElementById("students") || document.getElementById("teams")).children()[0]).children();
var search = $("#search");

search.focus();

function update() {
    for (var i = 0; i < items.length; i++) {
        var item = $(items[i + 1]);
        if ($(item.children()[1]).text().toLowerCase().includes(search.val().toLowerCase())) item.show();
        else item.hide();
    }
}
