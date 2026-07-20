"use strict";
/* magnuslodefalk.com — theme toggle (persisted), shared with the lab-site design system. */
(function () {
  const saved = localStorage.getItem("ml-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  const btn = document.querySelector("#themebtn");
  if (btn) btn.addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme")
      || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("ml-theme", next);
  });
})();
