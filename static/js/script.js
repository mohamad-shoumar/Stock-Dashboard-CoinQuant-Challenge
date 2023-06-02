document.addEventListener("DOMContentLoaded", function () {
  const icon = document.getElementById("icon");
  icon.onclick = function () {
    document.body.classList.toggle("dark-theme");
    if (document.body.classList.contains("dark-theme")) {
      icon.src = "static/assets/moon.png";
    } else {
      icon.src = "static/assets/sun.png";
    }
  };
});
