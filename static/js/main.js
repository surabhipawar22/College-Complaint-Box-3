/* ═══════════════════════════════════════════════════════
   main.js — Student Complaint Submission Logic
   ═══════════════════════════════════════════════════════ */

// AUTO-DETECT API URL
const API_BASE = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost" ?
    "http://127.0.0.1:5000" :
    "";

// ── DOM refs ─────────────────────────────────────────────────
const form = document.getElementById("complaintForm");
const anonToggle = document.getElementById("anonymousToggle");
const identityFields = document.getElementById("identityFields");
const anonNote = document.getElementById("anonNote");
const submitBtn = document.getElementById("submitBtn");
const titleInput = document.getElementById("title");
const descInput = document.getElementById("description");
const titleCount = document.getElementById("titleCount");
const descCount = document.getElementById("descCount");
const successToast = document.getElementById("successToast");
const errorToast = document.getElementById("errorToast");

// ── Anonymous toggle ─────────────────────────────────────────
if (anonToggle) {
    anonToggle.addEventListener("change", function() {
        const isAnon = anonToggle.checked;
        if (identityFields && anonNote) {
            if (isAnon) {
                identityFields.style.display = "none";
                anonNote.textContent = "Your identity will not be recorded.";
            } else {
                identityFields.style.display = "block";
                anonNote.textContent = "Your name & email will be recorded.";
            }
        }
    });
}

// ── Character counters ───────────────────────────────────────
if (titleInput && titleCount) {
    titleInput.addEventListener("input", function() {
        titleCount.textContent = titleInput.value.length + " / 200";
    });
}

if (descInput && descCount) {
    descInput.addEventListener("input", function() {
        descCount.textContent = descInput.value.length + " / 5000";
    });
}

// ── Form submission ──────────────────────────────────────────
if (form) {
    form.addEventListener("submit", async function(e) {
        e.preventDefault();
        clearErrors();

        const isAnon = anonToggle ? anonToggle.checked : false;

        // Traditional null-checks (removes all ?. errors)
        const nameEl = document.getElementById("name");
        const emailEl = document.getElementById("email");
        const deptEl = document.getElementById("department");

        const name = isAnon ? null : (nameEl ? nameEl.value.trim() : null);
        const email = isAnon ? null : (emailEl ? emailEl.value.trim() : null);
        const department = deptEl ? deptEl.value : "";
        const title = titleInput ? titleInput.value.trim() : "";
        const description = descInput ? descInput.value.trim() : "";

        // Client-side validation
        let hasError = false;

        if (!department) {
            showFieldError("dept-error", "Please select a department.");
            if (deptEl) deptEl.classList.add("invalid");
            hasError = true;
        }
        if (!title) {
            showFieldError("title-error", "Please enter a complaint title.");
            if (titleInput) titleInput.classList.add("invalid");
            hasError = true;
        }
        if (!description) {
            showFieldError("desc-error", "Please describe your complaint.");
            if (descInput) descInput.classList.add("invalid");
            hasError = true;
        }
        if (email && !isValidEmail(email)) {
            showFieldError("email-error", "Please enter a valid email.");
            if (emailEl) emailEl.classList.add("invalid");
            hasError = true;
        }

        if (hasError) return;

        setLoading(true);

        try {
            const res = await fetch(API_BASE + "/submit_complaint", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    department: department,
                    title: title,
                    description: description,
                    anonymous: isAnon
                }),
            });

            const data = await res.json();

            if (!res.ok) {
                showToast(errorToast, data.error || "Submission failed.");
                return;
            }

            // SUCCESS logic
            const displayId = document.getElementById("displayId");
            if (displayId) displayId.innerText = data.id;

            const successModal = document.getElementById("successModal");
            if (successModal) {
                successModal.classList.add("open");
            } else {
                showToast(successToast, "✓ Complaint #" + data.id + " submitted!");
            }

            form.reset();
            if (titleCount) titleCount.textContent = "0 / 200";
            if (descCount) descCount.textContent = "0 / 5000";
            if (isAnon && identityFields) identityFields.style.display = "none";

        } catch (err) {
            console.error(err);
            showToast(errorToast, "Network error. Please check connection.");
        } finally {
            setLoading(false);
        }
    });
}

// ── Helpers ──────────────────────────────────────────────────
function clearErrors() {
    const errors = document.querySelectorAll(".field-error");
    const invalids = document.querySelectorAll(".invalid");
    errors.forEach(function(el) { el.textContent = ""; });
    invalids.forEach(function(el) { el.classList.remove("invalid"); });
}

function showFieldError(id, msg) {
    const el = document.getElementById(id);
    if (el) el.textContent = msg;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function setLoading(loading) {
    if (!submitBtn) return;
    if (loading) {
        submitBtn.classList.add("loading");
        submitBtn.disabled = true;
    } else {
        submitBtn.classList.remove("loading");
        submitBtn.disabled = false;
    }
}

let toastTimeout;

function showToast(el, msg) {
    if (!el) return;
    clearTimeout(toastTimeout);
    el.textContent = msg;
    el.classList.add("show");
    toastTimeout = setTimeout(function() { el.classList.remove("show"); }, 4500);
}