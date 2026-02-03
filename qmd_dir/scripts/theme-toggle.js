<script>
(function () {
  const html = document.documentElement;

  // Bootstrap theme via attribute
  const storedTheme = localStorage.getItem("theme") || "light";
  html.setAttribute("data-bs-theme", storedTheme);

  const toggle = document.getElementById("theme-toggle");
  if (!toggle) return;

  toggle.textContent = storedTheme === "dark" ? "◑" : "◐";

  toggle.addEventListener("click", () => {
    const current = html.getAttribute("data-bs-theme") || "light";
    const next = current === "dark" ? "light" : "dark";

    html.setAttribute("data-bs-theme", next);
    localStorage.setItem("theme", next);
    toggle.textContent = next === "dark" ? "◑" : "◐";
  });
})()
</script>
