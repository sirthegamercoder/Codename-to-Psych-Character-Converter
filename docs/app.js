(function () {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const addBtn = document.getElementById("addBtn");
  const clearBtn = document.getElementById("clearBtn");
  const fileListContainer = document.getElementById("fileListContainer");
  const convertBtn = document.getElementById("convertBtn");
  const progressArea = document.getElementById("progressArea");
  const progressFill = document.getElementById("progressFill");
  const statusMsg = document.getElementById("statusMsg");
  const statsArea = document.getElementById("statsArea");
  const statTotal = document.getElementById("statTotal");
  const statSuccess = document.getElementById("statSuccess");
  const statFailed = document.getElementById("statFailed");
  const statCurrent = document.getElementById("statCurrent");

  let selectedFiles = [];
  let fileContents = new Map();
  let fileStatus = new Map();
  let fileTypes = new Map();
  let isConverting = false;
  let successCount = 0,
    failCount = 0;
  let fileSystemSupported = null;

  function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
  }

  function getStatusIcon(status) {
    switch (status) {
      case "converting":
        return "⏳";
      case "success":
        return "✅";
      case "error":
        return "❌";
      default:
        return "🕒";
    }
  }

  function getFileTypeIcon(fileType) {
    return fileType === "xml" ? "📄" : "📋";
  }

  function updateStatusMessage(text, type = "info") {
    statusMsg.textContent = text;
    statusMsg.classList.remove("error", "success");
    if (type === "error") statusMsg.classList.add("error");
    else if (type === "success") statusMsg.classList.add("success");
  }

  function updateStats() {
    statTotal.textContent = selectedFiles.length;
    statSuccess.textContent = successCount;
    statFailed.textContent = failCount;
    const converting = Array.from(fileStatus.values()).filter(
      (v) => v === "converting",
    ).length;
    statCurrent.textContent = converting;
    statsArea.style.display = selectedFiles.length > 0 ? "flex" : "none";
  }

  function renderFileList() {
    if (selectedFiles.length === 0) {
      fileListContainer.innerHTML = `<div class="empty-message">No file(s) selected</div>`;
      convertBtn.disabled = true;
      statsArea.style.display = "none";
      return;
    }
    convertBtn.disabled = false;
    statsArea.style.display = "flex";
    statTotal.textContent = selectedFiles.length;

    let html = "";
    selectedFiles.forEach((file, idx) => {
      const status = fileStatus.get(file.name) || "pending";
      const fileType = fileTypes.get(file.name) || "unknown";
      const sizeKB = (file.size / 1024).toFixed(1);
      const typeDisplay = fileType === "xml" ? "XML" : "JSON";
      const typeClass = fileType === "xml" ? "xml" : "json";
      html += `
            <div class="file-chip ${status}" data-filename="${file.name}">
              <span class="status-icon">${getStatusIcon(status)}</span>
              <span class="file-type-badge ${typeClass}">${typeDisplay}</span>
              <span class="fname">${escapeHtml(file.name)}</span>
              <span class="fsize">${sizeKB} KB</span>
              <button class="remove-btn" data-index="${idx}" ${isConverting ? "disabled" : ""}>
                <span class="material-symbols-outlined" style="font-size:1.2rem;">close</span>
              </button>
            </div>
          `;
    });
    fileListContainer.innerHTML = html;

    if (!isConverting) {
      document.querySelectorAll(".remove-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          const idx = parseInt(btn.dataset.index);
          removeFile(idx);
        });
      });
    }
    updateStats();
  }

  function updateFileChipStatus(filename, status) {
    const chip = document.querySelector(
      `.file-chip[data-filename="${filename}"]`,
    );
    if (chip) {
      chip.className = `file-chip ${status}`;
      const iconSpan = chip.querySelector(".status-icon");
      if (iconSpan) iconSpan.textContent = getStatusIcon(status);
    }
    fileStatus.set(filename, status);
    updateStats();
  }

  function removeFile(index) {
    if (isConverting) {
      updateStatusMessage("Cannot remove during conversion", "error");
      return;
    }
    const removed = selectedFiles[index];
    if (!removed) return;
    selectedFiles.splice(index, 1);
    fileContents.delete(removed.name);
    fileStatus.delete(removed.name);
    fileTypes.delete(removed.name);
    renderFileList();
    updateStatusMessage(`Removed ${removed.name}`, "info");
  }

  function clearAll() {
    if (isConverting) {
      updateStatusMessage("Cannot clear during conversion", "error");
      return;
    }
    selectedFiles = [];
    fileContents.clear();
    fileStatus.clear();
    fileTypes.clear();
    successCount = 0;
    failCount = 0;
    renderFileList();
    updateStatusMessage("Cleared all files", "info");
    progressArea.style.display = "none";
    progressFill.style.width = "0%";
  }

  function addFiles(files) {
    const valid = Array.from(files).filter((f) => {
      const ext = f.name.toLowerCase().split(".").pop();
      if (!["xml", "json"].includes(ext)) {
        updateStatusMessage(`Skipped "${f.name}" (not XML or JSON)`, "error");
        return false;
      }
      if (selectedFiles.some((ex) => ex.name === f.name)) {
        updateStatusMessage(`Skipped "${f.name}" (already added)`, "error");
        return false;
      }
      return true;
    });
    if (valid.length === 0) return;

    valid.forEach((file) => {
      const ext = file.name.toLowerCase().split(".").pop();
      const fileType = ext === "xml" ? "xml" : "json";
      selectedFiles.push(file);
      fileStatus.set(file.name, "pending");
      fileTypes.set(file.name, fileType);
      const reader = new FileReader();
      reader.onload = (e) => {
        fileContents.set(file.name, e.target.result);
        updateFileChipStatus(file.name, "pending");
        updateStatusMessage(
          `Loaded "${file.name}" (${fileType.toUpperCase()})`,
          "success",
        );
      };
      reader.onerror = () => {
        updateStatusMessage(`Failed to read "${file.name}"`, "error");
        const idx = selectedFiles.findIndex((f) => f.name === file.name);
        if (idx !== -1) {
          selectedFiles.splice(idx, 1);
          fileStatus.delete(file.name);
          fileTypes.delete(file.name);
          renderFileList();
        }
      };
      reader.readAsText(file, "UTF-8");
    });

    renderFileList();
    updateStatusMessage(`Added ${valid.length} file(s)`, "success");
  }

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    if (!isConverting) dropZone.classList.add("drag-over");
  });
  dropZone.addEventListener("dragleave", () =>
    dropZone.classList.remove("drag-over"),
  );
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (isConverting) {
      updateStatusMessage("Cannot add during conversion", "error");
      return;
    }
    if (e.dataTransfer.files.length) addFiles(Array.from(e.dataTransfer.files));
  });

  addBtn.addEventListener("click", () => {
    if (!isConverting) fileInput.click();
  });
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      addFiles(Array.from(e.target.files));
      fileInput.value = "";
    }
  });
  clearBtn.addEventListener("click", clearAll);

  function hexToRgb(hexColor) {
    let hex = hexColor.replace("#", "");
    if (hex.length === 3)
      hex = hex
        .split("")
        .map((c) => c + c)
        .join("");
    try {
      const r = parseInt(hex.substring(0, 2), 16);
      const g = parseInt(hex.substring(2, 4), 16);
      const b = parseInt(hex.substring(4, 6), 16);
      if (isNaN(r) || isNaN(g) || isNaN(b)) return [161, 161, 161];
      return [r, g, b];
    } catch {
      return [161, 161, 161];
    }
  }

  function parseIndices(str) {
    if (!str) return [];
    const res = new Set();
    const parts = str.split(",");
    for (let part of parts) {
      part = part.trim();
      if (part.includes("..")) {
        const [start, end] = part.split("..").map(Number);
        if (!isNaN(start) && !isNaN(end))
          for (let i = start; i <= end; i++) res.add(i);
      } else if (!isNaN(Number(part))) res.add(Number(part));
    }
    return Array.from(res).sort((a, b) => a - b);
  }

  function getAttr(el, name, def = null) {
    return el.getAttribute(name) ?? def;
  }
  function getFloat(el, name, def) {
    const v = el.getAttribute(name);
    return v === null ? def : parseFloat(v) || def;
  }
  function getBool(el, name, def) {
    const v = el.getAttribute(name);
    return v === null ? def : ["true", "1", "yes"].includes(v.toLowerCase());
  }

  function convertXmlToPsych(xmlString) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlString, "text/xml");
    const err = doc.querySelector("parsererror");
    if (err) throw new Error("Invalid XML: " + err.textContent);
    const root = doc.documentElement;
    if (root.tagName !== "character")
      throw new Error("Root must be <character>");

    const x = getFloat(root, "x", 0),
      y = getFloat(root, "y", 0);
    const sprite = getAttr(root, "sprite", "characters/BOYFRIEND");
    const scale = getFloat(root, "scale", 1);
    const camx = getFloat(root, "camx", 0),
      camy = getFloat(root, "camy", 0);
    const icon = getAttr(root, "icon", "face");
    const holdTime = getFloat(root, "holdTime", 4);
    const flipX = getBool(root, "flipX", false);
    const colorHex = getAttr(root, "color", "#A1A1A1");
    const rgb = hexToRgb(colorHex);

    const anims = root.querySelectorAll("anim");
    const psychAnims = [];
    for (let a of anims) {
      const name = getAttr(a, "name", "");
      const anim = getAttr(a, "anim", "");
      const ax = getFloat(a, "x", 0),
        ay = getFloat(a, "y", 0);
      const fps = Math.round(getFloat(a, "fps", 24));
      const loop = getBool(a, "loop", false);
      const indicesRaw = getAttr(a, "indices", null);
      const indices = indicesRaw ? parseIndices(indicesRaw) : [];
      psychAnims.push({
        anim: name,
        name: anim,
        fps: fps,
        loop: loop,
        indices: indices,
        offsets: [parseInt(ax) || 0, parseInt(ay) || 0],
      });
    }

    return {
      animations: psychAnims,
      image: "characters/" + sprite,
      scale: scale,
      sing_duration: holdTime,
      healthicon: icon,
      position: [x, y],
      camera_position: [camx, camy],
      flip_x: flipX,
      no_antialiasing: false,
      healthbar_colors: rgb,
      vocals_file: null,
    };
  }

  function convertVSliceToPsych(jsonString) {
    let data;
    try {
      data = JSON.parse(jsonString);
    } catch (e) {
      throw new Error("Invalid JSON: " + e.message);
    }

    if (!data.assetPath && (!data.animations || data.animations.length === 0)) {
      throw new Error('Invalid V-Slice: missing "assetPath" or "animations"');
    }

    const psychChar = {};

    let imagePath = data.assetPath || "";
    if (imagePath) {
      if (imagePath.startsWith("shared:")) {
        imagePath = imagePath.substring(7);
      }
      psychChar.image = imagePath;
    } else {
      const anims = data.animations || [];
      if (anims.length > 0) {
        const prefix = anims[0].prefix || "";
        if (prefix) {
          const parts = prefix.split("/");
          if (parts.length > 1) {
            psychChar.image =
              parts.slice(0, -1).join("/") + "/" + parts[parts.length - 1];
          } else {
            psychChar.image = prefix;
          }
        } else {
          psychChar.image = "characters/bf";
        }
      } else {
        psychChar.image = "characters/bf";
      }
    }

    psychChar.scale = data.scale !== undefined ? data.scale : 1.0;

    psychChar.sing_duration =
      data.singTime !== undefined ? data.singTime : data.sing_duration || 4.0;

    const healthIcon = data.healthIcon;
    if (healthIcon && typeof healthIcon === "object") {
      psychChar.healthicon = healthIcon.id || "face";
    } else {
      psychChar.healthicon = healthIcon || "face";
    }

    const pos = data.offsets || data.position || [0, 0];
    psychChar.position = [pos[0] || 0, pos[1] || 0];

    const camPos = data.cameraOffsets || data.camera_position || [0, 0];
    psychChar.camera_position = [camPos[0] || 0, camPos[1] || 0];

    psychChar.flip_x =
      data.flipX !== undefined ? data.flipX : data.flip_x || false;

    psychChar.no_antialiasing =
      data.isPixel !== undefined ? data.isPixel : data.no_antialiasing || false;

    const healthColors = data.healthbarColors || data.healthbar_colors;
    if (healthColors && healthColors.length >= 3) {
      psychChar.healthbar_colors = healthColors.slice(0, 3);
    } else {
      psychChar.healthbar_colors = [161, 161, 161];
    }

    psychChar.vocals_file = data.vocalsFile || data.vocals_file || null;

    const anims = data.animations || [];
    const psychAnims = [];
    for (const anim of anims) {
      const animName = anim.name || anim.anim || "";
      const animPrefix = anim.prefix || anim.animation || "";
      const fps = anim.frameRate || anim.fps || 24;
      const loop = anim.looped !== undefined ? anim.looped : anim.loop || false;
      const indices = anim.frameIndices || anim.indices || [];
      const offsets = anim.offsets || [0, 0];
      psychAnims.push({
        anim: animName,
        name: animPrefix,
        fps: fps,
        loop: loop,
        indices: indices,
        offsets: [parseInt(offsets[0]) || 0, parseInt(offsets[1]) || 0],
      });
    }
    psychChar.animations = psychAnims;

    return psychChar;
  }

  function convertFile(content, fileType) {
    if (fileType === "xml") {
      return convertXmlToPsych(content);
    } else if (fileType === "json") {
      return convertVSliceToPsych(content);
    } else {
      throw new Error("Unsupported file type: " + fileType);
    }
  }

  async function saveFile(content, defaultName) {
    if (fileSystemSupported === null)
      fileSystemSupported = "showSaveFilePicker" in window;
    if (fileSystemSupported) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: defaultName,
          types: [
            { description: "JSON", accept: { "application/json": [".json"] } },
          ],
        });
        const w = await handle.createWritable();
        await w.write(content);
        await w.close();
        return { success: true, name: handle.name };
      } catch (err) {
        if (err.name !== "AbortError")
          return { success: false, error: err.message };
        return { success: false, cancelled: true };
      }
    } else {
      const blob = new Blob([content], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = defaultName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      return { success: true, name: defaultName };
    }
  }

  async function startConversion() {
    if (isConverting) return;
    if (selectedFiles.length === 0) {
      updateStatusMessage("No files to convert", "error");
      return;
    }
    const missing = selectedFiles.filter((f) => !fileContents.has(f.name));
    if (missing.length) {
      updateStatusMessage(
        `Waiting for ${missing.length} file(s) to load`,
        "error",
      );
      return;
    }

    isConverting = true;
    convertBtn.disabled = true;
    clearBtn.disabled = true;
    addBtn.disabled = true;
    progressArea.style.display = "flex";
    successCount = 0;
    failCount = 0;
    const total = selectedFiles.length;

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      const content = fileContents.get(file.name);
      const fileType = fileTypes.get(file.name) || "xml";
      progressFill.style.width = `${(i / total) * 100}%`;
      updateStatusMessage(
        `Converting ${i + 1}/${total}: ${file.name} (${fileType.toUpperCase()})`,
        "info",
      );

      updateFileChipStatus(file.name, "converting");
      updateStats();

      try {
        const jsonObj = convertFile(content, fileType);
        const jsonStr = JSON.stringify(jsonObj, null, 2);
        const outName = file.name.replace(/\.(xml|json)$/i, ".json");
        const result = await saveFile(jsonStr, outName);

        if (result.success) {
          successCount++;
          updateFileChipStatus(file.name, "success");
          updateStatusMessage(`Converted: ${file.name}`, "success");
        } else if (!result.cancelled) {
          failCount++;
          updateFileChipStatus(file.name, "error");
          updateStatusMessage(`Failed: ${file.name}`, "error");
        } else {
          updateStatusMessage("Cancelled by user", "error");
          break;
        }
      } catch (err) {
        failCount++;
        updateFileChipStatus(file.name, "error");
        updateStatusMessage(`Error: ${err.message}`, "error");
      }
      updateStats();
    }

    progressFill.style.width = "100%";
    if (successCount === total)
      updateStatusMessage(`All ${successCount} converted!`, "success");
    else if (successCount)
      updateStatusMessage(`${successCount} ok, ${failCount} failed`, "info");
    else updateStatusMessage("No files converted", "error");

    setTimeout(() => {
      progressArea.style.display = "none";
      progressFill.style.width = "0%";
    }, 2800);
    isConverting = false;
    convertBtn.disabled = false;
    clearBtn.disabled = false;
    addBtn.disabled = false;
  }

  convertBtn.addEventListener("click", startConversion);

  renderFileList();
})();