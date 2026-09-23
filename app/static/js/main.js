// Live search + animations - Bilkul!
console.log("College Events Pro loaded!");
document.addEventListener("DOMContentLoaded", () => {
  const inp = document.getElementById("liveSearch");
  if (inp) {
    inp.addEventListener("input", () => {
      const q = inp.value.toLowerCase();
      document.querySelectorAll(".event-card").forEach(c => {
        c.style.display = c.innerText.toLowerCase().includes(q) ? "" : "none";
      });
    });
  }
});
