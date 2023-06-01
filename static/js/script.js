document.addEventListener("DOMContentLoaded", function () {
  const toggleSwitch = document.querySelector("#dark-mode-toggle");
  const darkModeStyle = document.querySelector("#dark-mode-style");

  toggleSwitch.addEventListener("change", function () {
    if (this.checked) {
      document.body.classList.add("dark-mode");
      darkModeStyle.disabled = false;
    } else {
      document.body.classList.remove("dark-mode");
      darkModeStyle.disabled = true;
    }
  });
});
