// Live search + dark theme - Bilkul!
console.log("College Events Pro loaded!");
function toggleTheme(){
  const h=document.documentElement;
  const dark=h.getAttribute('data-bs-theme')==='dark';
  h.setAttribute('data-bs-theme',dark?'light':'dark');
  try{localStorage.setItem('theme',dark?'light':'dark')}catch(e){}
  const b=document.getElementById('themeBtn'); if(b)b.textContent=dark?'🌙':'☀️';
}
document.addEventListener("DOMContentLoaded", () => {
  try{if(localStorage.getItem('theme')==='dark'){const b=document.getElementById('themeBtn');if(b)b.textContent='☀️'}}catch(e){}
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
