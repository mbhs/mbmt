let clicking = false;

document.addEventListener("mousedown", () => clicking = true);
document.addEventListener("mouseup", () => clicking = false);

$(".question-label").mouseenter((e) => {
  if (clicking) e.target.children[0].checked = true;
});

$(".question-label").mouseleave((e) => {
  if (clicking) e.target.children[0].checked = true;
});
