function email(username, domain) {
    var address = username + '@' + domain;
    document.write('<a href="mailto:' + address + '">' + address + "</a>");
}
