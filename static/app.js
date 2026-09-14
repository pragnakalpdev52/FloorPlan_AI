const currentUserLabel = document.getElementById("current-user");
const logoutBtn = document.getElementById("logout-btn");
const sampleList = document.getElementById("sample-list");
const fileInput = document.getElementById("file-input");
const fileLabel = document.getElementById("file-label");
const dropzone = document.getElementById("dropzone");
const browseBtn = document.getElementById("browse-btn");
const detectBtn = document.getElementById("detect-btn");
const detectActiveBtn = document.getElementById("detect-active-btn");
const clearQueueBtn = document.getElementById("clear-queue-btn");
const overlay = document.getElementById("overlay");
const overlayStatus = document.getElementById("overlay-status");
const queuePanel = document.getElementById("queue-panel");
const queueList = document.getElementById("queue-list");
const queueBadge = document.getElementById("queue-badge");
const workspace = document.getElementById("workspace");
const activeTitle = document.getElementById("active-title");
const activeSubtitle = document.getElementById("active-subtitle");
const uploadHint = document.getElementById("upload-hint");
const inventoryBody = document.getElementById("inventory-body");
const roomCards = document.getElementById("room-cards");
const classCounts = document.getElementById("class-counts");
const jsonOutput = document.getElementById("json-output");
const statPills = document.getElementById("stat-pills");
const resultsCopy = document.getElementById("results-copy");
const lightbox = document.getElementById("lightbox");
const lightboxStage = document.getElementById("lightbox-stage");
const lightboxImage = document.getElementById("lightbox-image");
const lightboxTitle = document.getElementById("lightbox-title");
const lightboxZoomLevel = document.getElementById("lightbox-zoom-level");

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 6;
const ZOOM_FACTOR = 1.25;

let jobs = [];
let activeJobId = null;
let isDetecting = false;
let jobCounter = 0;
let lightboxZoom = 1;

const frameControllers = new Map();

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function formatBytes(size) {
  return `${(size / 1024).toFixed(1)} KB`;
}

function isImageFile(file) {
  if (!file) {
    return false;
  }
  if (file.type && file.type.startsWith("image/")) {
    return true;
  }
  return /\.(png|jpe?g|webp)$/i.test(file.name || "");
}

function createFrameController(frame) {
  const image = frame.querySelector("img");
  const scroller = frame.querySelector("[data-scroll]") || frame;
  const label = frame.querySelector("[data-zoom-label]");
  const state = {
    zoom: 1,
    title: frame.dataset.frame || "Image",
  };

  function applyZoom() {
    image.style.setProperty("--image-width", `${state.zoom * 100}%`);
    if (label) {
      label.textContent = `${Math.round(state.zoom * 100)}%`;
    }
  }

  function setSource(src, title) {
    state.title = title || state.title;
    if (!src) {
      image.removeAttribute("src");
      frame.classList.remove("has-image");
      state.zoom = 1;
      applyZoom();
      return;
    }
    const onReady = () => {
      frame.classList.add("has-image");
      state.zoom = 1;
      applyZoom();
      scroller.scrollTop = 0;
      scroller.scrollLeft = 0;
    };
    if (image.getAttribute("src") === src && image.complete && image.naturalWidth) {
      onReady();
      return;
    }
    image.onload = onReady;
    image.src = src;
  }

  function zoomBy(factor) {
    if (!frame.classList.contains("has-image")) {
      return;
    }
    const previous = state.zoom;
    const next = clamp(previous * factor, MIN_ZOOM, MAX_ZOOM);
    if (next === previous) {
      return;
    }
    const rect = scroller.getBoundingClientRect();
    const centerX = scroller.scrollLeft + rect.width / 2;
    const centerY = scroller.scrollTop + rect.height / 2;
    const ratio = next / previous;
    state.zoom = next;
    applyZoom();
    scroller.scrollLeft = centerX * ratio - rect.width / 2;
    scroller.scrollTop = centerY * ratio - rect.height / 2;
  }

  function fit() {
    state.zoom = 1;
    applyZoom();
    scroller.scrollTop = 0;
    scroller.scrollLeft = 0;
  }

  function expand() {
    if (!image.src) {
      return;
    }
    openLightbox(image.src, state.title);
  }

  frame.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const action = button.dataset.action;
      if (action === "zoom-in") {
        zoomBy(ZOOM_FACTOR);
      } else if (action === "zoom-out") {
        zoomBy(1 / ZOOM_FACTOR);
      } else if (action === "fit") {
        fit();
      } else if (action === "expand") {
        expand();
      }
    });
  });

  scroller.addEventListener(
    "wheel",
    (event) => {
      if (!frame.classList.contains("has-image")) {
        return;
      }
      if (!(event.ctrlKey || event.metaKey)) {
        return;
      }
      event.preventDefault();
      zoomBy(event.deltaY < 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR);
    },
    { passive: false }
  );

  image.addEventListener("dblclick", () => {
    if (!frame.classList.contains("has-image")) {
      return;
    }
    if (state.zoom === 1) {
      zoomBy(2);
    } else {
      fit();
    }
  });

  applyZoom();
  return { setSource, fit, zoomBy, expand };
}

function initFrames() {
  document.querySelectorAll(".image-frame").forEach((frame) => {
    frameControllers.set(frame.dataset.frame, createFrameController(frame));
  });
}

function applyLightboxZoom() {
  lightboxImage.style.setProperty("--image-width", `${lightboxZoom * 100}%`);
  lightboxZoomLevel.textContent = `${Math.round(lightboxZoom * 100)}%`;
}

function openLightbox(src, title) {
  lightboxTitle.textContent = title || "Fullscreen";
  lightbox.hidden = false;
  lightboxZoom = 1;
  applyLightboxZoom();
  lightboxImage.src = src;
  lightboxStage.scrollTop = 0;
  lightboxStage.scrollLeft = 0;
}

function closeLightbox() {
  lightbox.hidden = true;
  lightboxImage.removeAttribute("src");
}

function zoomLightbox(factor) {
  const previous = lightboxZoom;
  const next = clamp(previous * factor, MIN_ZOOM, MAX_ZOOM);
  if (next === previous) {
    return;
  }
  const rect = lightboxStage.getBoundingClientRect();
  const centerX = lightboxStage.scrollLeft + rect.width / 2;
  const centerY = lightboxStage.scrollTop + rect.height / 2;
  const ratio = next / previous;
  lightboxZoom = next;
  applyLightboxZoom();
  lightboxStage.scrollLeft = centerX * ratio - rect.width / 2;
  lightboxStage.scrollTop = centerY * ratio - rect.height / 2;
}

document.getElementById("lightbox-close").addEventListener("click", closeLightbox);
document.getElementById("lightbox-zoom-in").addEventListener("click", () => zoomLightbox(ZOOM_FACTOR));
document.getElementById("lightbox-zoom-out").addEventListener("click", () => zoomLightbox(1 / ZOOM_FACTOR));
document.getElementById("lightbox-zoom-reset").addEventListener("click", () => {
  lightboxZoom = 1;
  applyLightboxZoom();
  lightboxStage.scrollTop = 0;
  lightboxStage.scrollLeft = 0;
});

lightboxStage.addEventListener(
  "wheel",
  (event) => {
    if (!(event.ctrlKey || event.metaKey)) {
      return;
    }
    event.preventDefault();
    zoomLightbox(event.deltaY < 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR);
  },
  { passive: false }
);

lightboxImage.addEventListener("dblclick", () => {
  if (lightboxZoom === 1) {
    zoomLightbox(2);
  } else {
    lightboxZoom = 1;
    applyLightboxZoom();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !lightbox.hidden) {
    closeLightbox();
  }
});

document.querySelectorAll(".view-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".view-tab").forEach((item) => item.classList.remove("is-active"));
    document.querySelectorAll(".viewer-pane").forEach((pane) => pane.classList.remove("is-active"));
    tab.classList.add("is-active");
    document.querySelector(`[data-pane="${tab.dataset.view}"]`)?.classList.add("is-active");
  });
});

function openFilePicker() {
  fileInput.value = "";
  fileInput.click();
}

function updateQueueChrome() {
  const count = jobs.length;
  queuePanel.hidden = count === 0;
  workspace.hidden = count === 0;
  detectBtn.disabled = count === 0 || isDetecting;
  detectActiveBtn.disabled = !activeJobId || isDetecting;
  queueBadge.hidden = count === 0;
  queueBadge.textContent = `${count} image${count === 1 ? "" : "s"} in queue`;
  fileLabel.textContent = count === 0 ? "No files selected" : `${count} file${count === 1 ? "" : "s"} ready`;
  uploadHint.textContent =
    count === 0
      ? "Add one or more floor plans to start."
      : `Queue ready. Run all, or select one card and run active only.`;
}

function renderQueue() {
  queueList.innerHTML = jobs
    .map((job) => {
      const statusClass =
        job.status === "done"
          ? "is-done"
          : job.status === "running"
            ? "is-running"
            : job.status === "error"
              ? "is-error"
              : "is-pending";
      return `<article class="queue-card ${job.id === activeJobId ? "is-active" : ""}" data-job-id="${job.id}">
        <img class="queue-thumb" src="${job.previewUrl}" alt="" />
        <div class="queue-meta">
          <strong title="${job.file.name}">${job.file.name}</strong>
          <span>${formatBytes(job.file.size)}</span>
          <div><span class="queue-status ${statusClass}">${job.status}</span></div>
        </div>
        <button class="queue-remove" type="button" data-remove-id="${job.id}" title="Remove">×</button>
      </article>`;
    })
    .join("");

  queueList.querySelectorAll(".queue-card").forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("[data-remove-id]")) {
        return;
      }
      setActiveJob(card.dataset.jobId);
    });
  });

  queueList.querySelectorAll("[data-remove-id]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      removeJob(button.dataset.removeId);
    });
  });

  updateQueueChrome();
}

function getActiveJob() {
  return jobs.find((job) => job.id === activeJobId) || null;
}

function setActiveJob(jobId) {
  activeJobId = jobId;
  renderQueue();
  const job = getActiveJob();
  if (!job) {
    return;
  }
  activeTitle.textContent = job.file.name;
  activeSubtitle.textContent = `${formatBytes(job.file.size)} · ${job.status}`;
  frameControllers.get("original")?.setSource(job.previewUrl, job.file.name);
  frameControllers.get("compare-original")?.setSource(job.previewUrl, job.file.name);
  const annotatedSrc = job.result?.annotated_data_url || "";
  frameControllers.get("annotated")?.setSource(annotatedSrc, `${job.file.name} · detected`);
  frameControllers.get("compare-annotated")?.setSource(annotatedSrc, `${job.file.name} · detected`);
  renderDetails(job);
}

function renderDetails(job) {
  const result = job.result;
  if (!result) {
    resultsCopy.textContent =
      job.status === "error"
        ? `Error on ${job.file.name}: ${job.error || "Detection failed."}`
        : `Waiting for detection on ${job.file.name}.`;
    statPills.innerHTML = `<span class="pill">${job.status}</span>`;
    inventoryBody.innerHTML = `<tr><td colspan="4">No results yet for this image.</td></tr>`;
    roomCards.innerHTML = "";
    classCounts.innerHTML = "";
    jsonOutput.textContent = "";
    return;
  }

  resultsCopy.textContent =
    `File: ${result.filename} · engine ${result.engine || "pipeline"} · ` +
    `${result.image_width}×${result.image_height} · hash ${result.content_hash} · ` +
    `${result.object_count} objects` +
    (result.door_count != null ? ` · ${result.door_count} doors` : "") +
    (result.window_count != null ? ` · ${result.window_count} windows` : "") +
    (result.furniture_count != null ? ` · ${result.furniture_count} furniture` : "") +
    (result.roboflow_count != null ? ` · ${result.roboflow_count} roboflow` : "") +
    ` · ${result.inference_ms} ms`;

  statPills.innerHTML = `
    <span class="pill">${result.filename}</span>
    <span class="pill">${result.engine || "pipeline"}</span>
    <span class="pill">${result.door_count || 0} doors</span>
    <span class="pill">${result.window_count || 0} windows</span>
    <span class="pill">${result.furniture_count || 0} furniture</span>
    <span class="pill">${result.roboflow_count || 0} roboflow</span>
    <span class="pill">${result.inference_ms} ms</span>
  `;

  if (!result.objects.length) {
    inventoryBody.innerHTML = `<tr><td colspan="5">No detections on this upload.</td></tr>`;
  } else {
    inventoryBody.innerHTML = result.objects
      .map((item) => {
        const box = item.bbox.join(", ");
        const source = item.source || "—";
        return `<tr>
          <td>${item.id}</td>
          <td>${item.label}</td>
          <td>${Math.round(item.confidence * 100)}%</td>
          <td>${source}</td>
          <td>${box}</td>
        </tr>`;
      })
      .join("");
  }

  roomCards.innerHTML =
    (result.rooms || [])
      .map(
        (room) => `<article class="room-card">
          <strong>${room.name}</strong>
          <span>${room.object_count} detected objects</span>
        </article>`
      )
      .join("") || `<p class="panel-copy">No room regions extracted.</p>`;

  classCounts.innerHTML = Object.entries(result.summary || {})
    .map(
      ([className, count]) => `<div class="count-chip">
        <strong>${className.replaceAll("_", " ")}</strong>
        <span>${count}</span>
      </div>`
    )
    .join("");

  jsonOutput.textContent = JSON.stringify(
    {
      filename: result.filename,
      content_hash: result.content_hash,
      image_width: result.image_width,
      image_height: result.image_height,
      object_count: result.object_count,
      room_count: result.room_count,
      summary: result.summary,
      objects: result.objects,
      rooms: result.rooms,
      inference_ms: result.inference_ms,
    },
    null,
    2
  );
}

function addFiles(fileList) {
  const incoming = Array.from(fileList || []).filter(isImageFile);
  if (!incoming.length) {
    alert("Please choose PNG, JPG, or WEBP floor-plan images.");
    return;
  }

  incoming.forEach((file) => {
    jobCounter += 1;
    const id = `job-${jobCounter}-${Date.now()}`;
    jobs.push({
      id,
      file,
      previewUrl: URL.createObjectURL(file),
      status: "pending",
      result: null,
      error: null,
    });
  });

  if (!activeJobId && jobs.length) {
    setActiveJob(jobs[jobs.length - 1].id);
  } else {
    renderQueue();
    if (activeJobId) {
      setActiveJob(activeJobId);
    }
  }
}

function removeJob(jobId) {
  const index = jobs.findIndex((job) => job.id === jobId);
  if (index < 0) {
    return;
  }
  URL.revokeObjectURL(jobs[index].previewUrl);
  jobs.splice(index, 1);
  if (activeJobId === jobId) {
    activeJobId = jobs[0]?.id || null;
  }
  renderQueue();
  if (activeJobId) {
    setActiveJob(activeJobId);
  } else {
    workspace.hidden = true;
  }
}

function clearQueue() {
  jobs.forEach((job) => URL.revokeObjectURL(job.previewUrl));
  jobs = [];
  activeJobId = null;
  renderQueue();
  workspace.hidden = true;
}

async function detectJob(job) {
  job.status = "running";
  job.error = null;
  renderQueue();
  overlayStatus.textContent = `Detecting ${job.file.name}…`;

  const form = new FormData();
  form.append("file", job.file, job.file.name || "floorplan.png");
  const response = await fetch("/api/detect", {
    method: "POST",
    body: form,
    cache: "no-store",
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Detection failed." }));
    throw new Error(error.detail || "Detection failed.");
  }
  job.result = await response.json();
  job.status = "done";
}

async function runDetection(jobIds) {
  if (isDetecting || !jobIds.length) {
    return;
  }
  isDetecting = true;
  updateQueueChrome();
  overlay.hidden = false;

  try {
    for (const jobId of jobIds) {
      const job = jobs.find((item) => item.id === jobId);
      if (!job) {
        continue;
      }
      try {
        await detectJob(job);
      } catch (error) {
        job.status = "error";
        job.error = error.message;
      }
      renderQueue();
      if (job.id === activeJobId) {
        setActiveJob(job.id);
      }
    }
  } finally {
    isDetecting = false;
    overlay.hidden = true;
    updateQueueChrome();
    const active = getActiveJob();
    if (active?.status === "done") {
      document.querySelector('[data-view="compare"]')?.click();
    }
  }
}

async function loadSamples() {
  const response = await fetch("/api/samples");
  const samples = await response.json();
  sampleList.innerHTML = "";
  samples.forEach((sample) => {
    const button = document.createElement("button");
    button.className = "sample-card";
    button.type = "button";
    button.innerHTML = `<strong>${sample.title}</strong><span>Add to queue</span>`;
    button.addEventListener("click", async () => {
      const imageResponse = await fetch(sample.image_url);
      if (!imageResponse.ok) {
        alert("Could not load sample image.");
        return;
      }
      const blob = await imageResponse.blob();
      const file = new File([blob], sample.filename, { type: blob.type || "image/png" });
      addFiles([file]);
      document.querySelectorAll(".sample-card").forEach((card) => card.classList.remove("is-selected"));
      button.classList.add("is-selected");
    });
    sampleList.appendChild(button);
  });
}

dropzone.addEventListener("click", (event) => {
  if (event.target === browseBtn || browseBtn.contains(event.target)) {
    return;
  }
  openFilePicker();
});

dropzone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    openFilePicker();
  }
});

browseBtn.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  openFilePicker();
});

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragover");
  addFiles(event.dataTransfer.files);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files?.length) {
    addFiles(fileInput.files);
  }
});

detectBtn.addEventListener("click", () => {
  const pending = jobs.filter((job) => job.status !== "done").map((job) => job.id);
  runDetection(pending.length ? pending : jobs.map((job) => job.id));
});

detectActiveBtn.addEventListener("click", () => {
  if (activeJobId) {
    runDetection([activeJobId]);
  }
});

clearQueueBtn.addEventListener("click", clearQueue);

async function requireSession() {
  const response = await fetch("/api/me", { cache: "no-store" });
  const data = await response.json().catch(() => ({}));
  if (!data.authenticated) {
    window.location.href = "/login";
    return false;
  }
  currentUserLabel.textContent = data.user;
  return true;
}

logoutBtn.addEventListener("click", async () => {
  await fetch("/api/logout", { method: "POST" }).catch(() => {});
  window.location.href = "/login";
});

initFrames();
requireSession().then((ok) => {
  if (!ok) {
    return;
  }
  loadSamples().catch((error) => {
    sampleList.innerHTML = `<p class="panel-copy">${error.message}</p>`;
  });
});
