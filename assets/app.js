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

/* Anti-spam e-mail: assemble the real address from data-attributes at runtime.
   The static HTML only carries an obfuscated "(at)"/"(dot)" string, so scrapers
   never see a live mailto; JS users get a real, clickable link. */
(function () {
  document.querySelectorAll("a.email[data-u][data-d]").forEach((a) => {
    const addr = a.getAttribute("data-u") + "@" + a.getAttribute("data-d");
    a.setAttribute("href", "mailto:" + addr);
    if (a.dataset.reveal !== "keep") a.textContent = addr;
  });
})();
