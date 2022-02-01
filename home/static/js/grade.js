
const url = new URL(window.location.href);
$("#search").val(url.searchParams.get("search"));
