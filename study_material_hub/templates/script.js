const api = "http://127.0.0.1:8000/api"; // Change if deployed

// LOGIN
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${api}/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();
  if (data.access) {
    localStorage.setItem("access", data.access);
    alert("Login successful!");
    window.location.href = "index.html";
  } else {
    alert("Login failed.");
  }
});

// SIGNUP
document.getElementById("signupForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${api}/signup/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });

  const data = await res.json();
  alert(data.message || "Signup complete. Please login.");
  window.location.href = "login.html";
});

// FETCH STUDY MATERIALS
async function fetchMaterials() {
  const res = await fetch(`${api}/materials/`);
  const data = await res.json();

  const list = document.getElementById("materialList");
  list.innerHTML = "";
  data.forEach((item) => {
    list.innerHTML += `<li>${item.title} - ${item.subject} (${item.year})</li>`;
  });
}

// UPLOAD MATERIAL
document.getElementById("uploadForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const token = localStorage.getItem("access");

  const formData = new FormData();
  formData.append("title", document.getElementById("title").value);
  formData.append("subject", document.getElementById("subject").value);
  formData.append("year", document.getElementById("year").value);
  formData.append("file", document.getElementById("file").files[0]);

  const res = await fetch(`${api}/materials/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  const data = await res.json();
  alert("Uploaded!");
  window.location.href = "index.html";
});
