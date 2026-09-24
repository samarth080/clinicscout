const labels = {
  joint_replacement_offered: "Joint replacement offered",
  knee_replacement_mentioned: "Knee replacement mentioned",
  hip_replacement_mentioned: "Hip replacement mentioned",
  rehab_capability: "Rehab / physiotherapy capability",
  ortho_lead: "Orthopaedic lead named",
  physio_lead: "Physiotherapy lead named",
  volume_signal: "Volume signal",
};

const runButton = document.querySelector("#run");
const message = document.querySelector("#message");
const results = document.querySelector("#results");
const fields = document.querySelector("#fields");
const stats = document.querySelector("#stats");
const download = document.querySelector("#download");
let latest = null;

function showMessage(text, isError = false) {
  message.textContent = text;
  message.className = `message${isError ? " error" : ""}`;
  message.hidden = !text;
}

function render(data) {
  latest = data;
  fields.replaceChildren();
  for (const [key, label] of Object.entries(labels)) {
    const item = data.fields[key];
    const card = document.createElement("article");
    card.className = "field";

    const name = document.createElement("p");
    name.className = "field-name";
    name.textContent = label;

    const value = document.createElement("span");
    value.className = `value${item.value === "Unknown" ? " unknown" : ""}`;
    value.textContent = item.value;

    const evidence = document.createElement("p");
    evidence.className = "evidence";
    evidence.textContent = item.value === "Unknown" ? "The page did not support an answer." : `“${item.evidence}”`;

    card.append(name, value, evidence);
    if (item.flag) {
      const flag = document.createElement("p");
      flag.className = "flag";
      flag.textContent = item.flag;
      card.append(flag);
    }
    fields.append(card);
  }

  const answered = Object.values(data.fields).filter((item) => item.value !== "Unknown").length;
  stats.innerHTML = `<span class="stat"><strong>${answered}/7</strong> answered</span><span class="stat"><strong>${data.contact_phones.length}</strong> phones found</span><span class="stat"><strong>${data.mode}</strong> mode</span>`;
  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

runButton.addEventListener("click", async () => {
  const url = document.querySelector("#url").value.trim();
  const text = document.querySelector("#text").value.trim();
  const mode = document.querySelector('input[name="mode"]:checked').value;
  if (!url && !text) {
    showMessage("Give a public hospital URL or paste page text.", true);
    return;
  }

  runButton.disabled = true;
  runButton.textContent = "Reading the page…";
  showMessage("");
  results.hidden = true;
  try {
    const response = await fetch("/api/scout", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ url, text, mode }),
    });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || "ClinicScout could not read that page.");
    if (data.error) showMessage(data.error);
    render(data);
  } catch (error) {
    showMessage(error.message || "Something went wrong. Try the baseline or paste the page text.", true);
  } finally {
    runButton.disabled = false;
    runButton.textContent = "Run ClinicScout";
  }
});

download.addEventListener("click", () => {
  if (!latest) return;
  const blob = new Blob([JSON.stringify(latest, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "clinicscout.json";
  link.click();
  URL.revokeObjectURL(link.href);
});
