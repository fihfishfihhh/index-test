const API = "";
const CONFIG = {
  loanDays: 5,
  maxBooksPerStudent: 3,
  faceConfidenceThreshold: 10,
  faceSizeThreshold: 10,
  livenessActions: ["open_mouth", "turn_head", "blink"],
};

const state = {
  mode: "borrow",
  stream: null,
  facingMode: "user",
  cameraReady: false,
  scanning: false,
  challenge: null,
  challengeNonce: "",
  currentDetection: null,
  devLoggedIn: false,
  lastResult: "",
  currentFaceDescriptor: null,
  currentFaceBox: null,
  faces: [],
};

const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const statusBar = document.getElementById("status-bar");
const statusText = document.getElementById("status-text");
const identityLabel = document.getElementById("identity-label");
const challengeBox = document.getElementById("challenge-box");

function setStatus(message, kind = "") {
  statusText.textContent = message;
  statusBar.classList.remove("show", "valid", "invalid");
  if (kind) statusBar.classList.add(kind, "show");
}

function showResult(text, valid) {
  statusBar.textContent = text;
  statusBar.classList.remove("valid", "invalid");
  statusBar.classList.add(valid ? "valid" : "invalid", "show");
  state.lastResult = text;
  setTimeout(() => {
    statusBar.classList.remove("show", "valid", "invalid");
  }, 3000);
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function computeFaceConfidence(box, videoWidth, videoHeight) {
  const faceArea = box.width * box.height;
  const frameArea = videoWidth * videoHeight;
  const sizeFactor = clamp(faceArea / (0.18 * frameArea), 0, 1);
  const normalizedDistance = clamp((1 - box.width / videoWidth) * 0.8 + (1 - box.height / videoHeight) * 0.2, 0, 1);
  const confidence = 100 * (1 - normalizedDistance) * sizeFactor;
  return Number(confidence.toFixed(1));
}

async function loadFaceModels() {
  const modelUrl = "https://cdn.jsdelivr.net/npm/@vladmandic/face-api@1.7.12/model/";
  await Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri(modelUrl),
    faceapi.nets.faceLandmark68Net.loadFromUri(modelUrl),
    faceapi.nets.faceRecognitionNet.loadFromUri(modelUrl),
  ]);
}

async function startCamera() {
  try {
    if (state.stream) {
      state.stream.getTracks().forEach(track => track.stop());
    }

    const constraints = { video: { facingMode: state.facingMode, width: { ideal: 1280 }, height: { ideal: 720 } } };
    state.stream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = state.stream;
    await video.play();
    state.cameraReady = true;
    setStatus("Camera đã sẵn sàng. Đang theo dõi khuôn mặt.", "");
    requestAnimationFrame(drawOverlay);
    startLoop();
  } catch (error) {
    setStatus("Không mở được camera. Hãy cho phép quyền camera hoặc dùng HTTPS.", "invalid");
  }
}

function toggleDevPanel() {
  const panel = document.getElementById("dev-panel");
  panel.classList.toggle("hidden");
}

async function loginDev() {
  const key = document.getElementById("dev-key").value.trim();
  const res = await fetch(`${API}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key }),
  });
  const data = await res.json();
  if (data.ok) {
    state.devLoggedIn = true;
    setStatus("Đăng nhập dev thành công.", "");
    refreshLogs();
    return;
  }
  setStatus(data.message || "Khóa dev không hợp lệ.", "invalid");
}

async function searchStudent() {
  const name = document.getElementById("student-name").value.trim();
  if (!name) {
    setStatus("Nhập tên học sinh để tra cứu.", "invalid");
    return;
  }
  const res = await fetch(`${API}/api/student-detail?name=${encodeURIComponent(name)}`);
  const data = await res.json();
  const box = document.getElementById("student-summary");
  if (!data.student) {
    box.innerHTML = `<strong>Không tìm thấy.</strong><br>Học sinh chưa có dữ liệu hoặc tên nhập sai.`;
    return;
  }
  const overdue = (data.overdue || []).length;
  const borrowed = (data.borrowed || []).length;
  box.innerHTML = `
    <strong>${data.student.name}</strong><br>
    Lớp: ${data.student.class_name || "—"}<br>
    Đã mượn: ${borrowed} cuốn<br>
    Quá hạn: ${overdue} cuốn<br>
    ${overdue ? "Cần xử lý trả sách ngay." : "Không có sách quá hạn."}
  `;
}

async function searchBook() {
  const q = document.getElementById("book-query").value.trim();
  const res = await fetch(`${API}/api/books?q=${encodeURIComponent(q)}`);
  const data = await res.json();
  const box = document.getElementById("book-summary");
  if (!data.items || !data.items.length) {
    box.innerHTML = "Không tìm thấy sách phù hợp.";
    return;
  }
  box.innerHTML = data.items.map(item => `
    <div><strong>${item.title}</strong> (${item.code})</div>
    <div>Còn lại: ${item.available_qty}</div>
  `).join("<br>");
}

async function registerStudent() {
  if (!state.devLoggedIn) {
    setStatus("Cần đăng nhập dev trước khi lưu khuôn mặt.", "invalid");
    return;
  }

  const name = document.getElementById("student-register-name").value.trim();
  const className = document.getElementById("student-register-class").value.trim();
  if (!name || !className) {
    setStatus("Nhập đầy đủ họ tên và lớp.", "invalid");
    return;
  }
  if (!state.currentFaceDescriptor) {
    setStatus("Chưa nhận diện được khuôn mặt trong khung hình.", "invalid");
    return;
  }

  const payload = {
    name,
    class_name: className,
    face_descriptors: [Array.from(state.currentFaceDescriptor)],
  };

  const res = await fetch(`${API}/api/students/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Dev-Key": document.getElementById("dev-key").value.trim() },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (data.ok) {
    setStatus("Đã lưu khuôn mặt và thông tin học sinh.", "");
  } else {
    setStatus(data.message || "Không lưu được.", "invalid");
  }
}

async function addBook() {
  if (!state.devLoggedIn) {
    setStatus("Cần đăng nhập dev trước khi thêm sách.", "invalid");
    return;
  }
  const code = document.getElementById("book-code").value.trim();
  const title = document.getElementById("book-title").value.trim();
  const qty = Number(document.getElementById("book-qty").value || 0);
  const res = await fetch(`${API}/api/books`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Dev-Key": document.getElementById("dev-key").value.trim() },
    body: JSON.stringify({ code, title, quantity: qty }),
  });
  const data = await res.json();
  if (data.ok) {
    setStatus("Đã thêm sách vào kho.", "");
  } else {
    setStatus(data.message || "Không thêm được sách.", "invalid");
  }
}

async function backupDb() {
  if (!state.devLoggedIn) {
    setStatus("Cần đăng nhập dev trước khi sao lưu.", "invalid");
    return;
  }
  const res = await fetch(`${API}/api/backup`, { headers: { "X-Dev-Key": document.getElementById("dev-key").value.trim() } });
  const data = await res.json();
  setStatus(data.message || "Đã sao lưu.", data.ok ? "" : "invalid");
}

async function restoreDb() {
  if (!state.devLoggedIn) {
    setStatus("Cần đăng nhập dev trước khi phục hồi.", "invalid");
    return;
  }
  const input = document.getElementById("restore-file");
  const file = input.files[0];
  if (!file) {
    setStatus("Chọn file sao lưu .sqlite.", "invalid");
    return;
  }
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/api/restore`, {
    method: "POST",
    headers: { "X-Dev-Key": document.getElementById("dev-key").value.trim() },
    body: form,
  });
  const data = await res.json();
  setStatus(data.message || "Đã phục hồi.", data.ok ? "" : "invalid");
}

async function exportLog() {
  if (!state.devLoggedIn) {
    setStatus("Cần đăng nhập dev trước khi xuất log.", "invalid");
    return;
  }
  const res = await fetch(`${API}/api/export-log`, { headers: { "X-Dev-Key": document.getElementById("dev-key").value.trim() } });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "library-log.json";
  a.click();
  URL.revokeObjectURL(url);
  setStatus("Đã xuất file log JSON.", "");
}

async function refreshLogs() {
  if (!state.devLoggedIn) return;
  const res = await fetch(`${API}/api/logs`, { headers: { "X-Dev-Key": document.getElementById("dev-key").value.trim() } });
  const data = await res.json();
  const logList = document.getElementById("log-list");
  if (!data.items || !data.items.length) {
    logList.innerHTML = "<div class='log-item'>Chưa có nhật ký.</div>";
    return;
  }
  logList.innerHTML = data.items.map(item => `
    <div class='log-item'>
      <strong>${item.action}</strong><br>
      Học sinh: ${item.student_name || "—"}<br>
      Sách: ${item.book_name || "—"}<br>
      Thời gian: ${item.created_at || "—"}
    </div>
  `).join("");
}

function getRandomAction() {
  const actions = CONFIG.livenessActions;
  return actions[Math.floor(Math.random() * actions.length)];
}

function startLivenessChallenge() {
  const action = getRandomAction();
  state.challenge = action;
  state.challengeNonce = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const labels = {
    open_mouth: "MỞ MIỆNG",
    turn_head: "QUAY MẶT",
    blink: "NHẮM MẮT",
  };
  challengeBox.textContent = `YÊU CẦU: ${labels[action]}`;
  challengeBox.classList.remove("hidden");
  setStatus(`Kiểm tra chống mạo danh: ${labels[action]}.`, "");
}

function evaluateLiveness(landmarks) {
  if (!landmarks) return false;
  const parts = landmarks.positions;
  const mouthTop = parts[61];
  const mouthBottom = parts[67];
  const leftEyeTop = parts[159];
  const rightEyeTop = parts[386];
  const nose = parts[30];
  const leftEye = parts[36];
  const rightEye = parts[45];

  const mouthOpen = Math.abs(mouthBottom.y - mouthTop.y) > 7;
  const blinkRatio = (Math.abs(leftEye.y - leftEyeTop.y) + Math.abs(rightEye.y - rightEyeTop.y)) / 2;
  const eyeClosed = blinkRatio < 3;
  const headTurn = Math.abs(nose.x - ((leftEye.x + rightEye.x) / 2)) > 12;

  if (state.challenge === "open_mouth") return mouthOpen;
  if (state.challenge === "turn_head") return headTurn;
  if (state.challenge === "blink") return eyeClosed;
  return false;
}

async function detectAndProcess() {
  if (!state.cameraReady || !state.scanning) return;

  const detection = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.5 }))
    .withFaceLandmarks()
    .withFaceDescriptors();

  const canvasWidth = video.videoWidth || 640;
  const canvasHeight = video.videoHeight || 480;
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (detection.length > 0) {
    detection.sort((a, b) => b.detection.box.area - a.detection.box.area);
    const mainFace = detection[0];
    const box = mainFace.detection.box;
    const confidence = computeFaceConfidence(box, canvasWidth, canvasHeight);
    state.currentFaceDescriptor = mainFace.descriptor;
    state.currentFaceBox = box;
    state.faces = detection;

    const labelText = `${Math.round(confidence)}%${confidence < CONFIG.faceConfidenceThreshold ? " — quá nhỏ" : ""}`;
    identityLabel.style.display = "block";
    identityLabel.textContent = labelText;

    const drawBox = (face, color) => {
      const { x, y, width, height } = face.detection.box;
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, width, height);
    };

    drawBox(mainFace, "#38d39f");
    const nowAction = evaluateLiveness(mainFace.landmarks);
    if (state.challenge) {
      if (nowAction) {
        challengeBox.textContent = `ĐẠT: ${state.challenge}`;
        state.challenge = null;
        setTimeout(() => challengeBox.classList.add("hidden"), 1100);
      }
    }

    if (detection.length > 1) {
      const second = detection[1];
      const secondBox = second.detection.box;
      const secondArea = secondBox.width * secondBox.height;
      if (secondArea > (box.width * box.height) * 0.7) {
        showResult("KHÔNG HỢP LỆ: phát hiện nhiều khuôn mặt quá gần.", false);
        return;
      }
      drawBox(second, "#ff9f43");
    }

    if (confidence < CONFIG.faceConfidenceThreshold) {
      showResult("KHÔNG HỢP LỆ: độ tin cậy thấp, đến gần hơn.", false);
      return;
    }
  } else {
    identityLabel.style.display = "none";
  }

  if (!state.challenge && Math.random() < 0.35) {
    startLivenessChallenge();
  }

  const code = await readQRCode();
  if (code && state.currentFaceDescriptor && state.challenge === null) {
    const studentName = document.getElementById("student-name").value.trim();
    if (!studentName) {
      setStatus("Nhập tên học sinh trước khi quét.", "invalid");
      return;
    }
    const payload = {
      student_name: studentName,
      book_code: code,
      action_type: state.mode,
      face_confidence: computeFaceConfidence(state.currentFaceBox, canvas.width, canvas.height),
      face_size: (state.currentFaceBox.width * state.currentFaceBox.height) / (canvas.width * canvas.height) * 100,
      nearby_face_count: Math.max(0, state.faces.length - 1),
      liveness_ok: !!state.challenge || !!state.lastResult,
      challenge_nonce: state.challengeNonce,
      session_key: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      device_fps: 30,
    };
    const res = await fetch(`${API}/api/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (result.status === "valid") {
      showResult(`HỢP LỆ: ${result.message}`, true);
      setStatus(result.message, "valid");
    } else {
      showResult(result.message || "KHÔNG HỢP LỆ.", false);
      setStatus(result.message || "KHÔNG HỢP LỆ.", "invalid");
    }
    state.scanning = false;
    state.challenge = null;
    challengeBox.classList.add("hidden");
  }
}

async function readQRCode() {
  if (typeof BarcodeDetector !== "undefined") {
    try {
      const detector = new BarcodeDetector({ formats: ["qr_code", "code_128", "ean_13"] });
      const codes = await detector.detect(video);
      if (codes && codes.length) {
        return codes[0].rawValue.trim();
      }
    } catch (error) {
      // fallback to jsQR
    }
  }

  const tempCanvas = document.createElement("canvas");
  const w = video.videoWidth || 640;
  const h = video.videoHeight || 480;
  tempCanvas.width = w;
  tempCanvas.height = h;
  const context = tempCanvas.getContext("2d", { willReadFrequently: true });
  context.drawImage(video, 0, 0, w, h);
  const imageData = context.getImageData(0, 0, w, h);
  const qr = jsQR(imageData.data, w, h);
  return qr && qr.data ? qr.data.trim() : null;
}

function startLoop() {
  if (!state.cameraReady) return;
  const loop = async () => {
    if (state.cameraReady && state.scanning) {
      await detectAndProcess();
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}

function setMode(mode) {
  state.mode = mode;
  document.getElementById("mode-borrow").classList.toggle("active", mode === "borrow");
  document.getElementById("mode-return").classList.toggle("active", mode === "return");
}

async function startScan() {
  if (!state.cameraReady) {
    setStatus("Bật camera trước khi quét.", "invalid");
    return;
  }
  state.scanning = true;
  state.challenge = null;
  state.challengeNonce = "";
  challengeBox.classList.add("hidden");
  setStatus(`Chế độ: ${state.mode === "borrow" ? "Mượn" : "Trả"}. Đang chờ quét...`, "");
  startLivenessChallenge();
}

window.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadFaceModels();
  } catch (error) {
    setStatus("Không tải được mô tưởng nhận diện khuôn mặt. Hãy kiểm tra kết nối internet.", "invalid");
  }

  document.getElementById("start-camera").addEventListener("click", startCamera);
  document.getElementById("flip-camera").addEventListener("click", () => {
    state.facingMode = state.facingMode === "user" ? "environment" : "user";
    startCamera();
  });
  document.getElementById("start-scan").addEventListener("click", startScan);
  document.getElementById("mode-borrow").addEventListener("click", () => setMode("borrow"));
  document.getElementById("mode-return").addEventListener("click", () => setMode("return"));
  document.getElementById("toggle-dev").addEventListener("click", toggleDevPanel);
  document.getElementById("login-dev").addEventListener("click", loginDev);
  document.getElementById("search-student").addEventListener("click", searchStudent);
  document.getElementById("search-book").addEventListener("click", searchBook);
  document.getElementById("register-student").addEventListener("click", registerStudent);
  document.getElementById("add-book").addEventListener("click", addBook);
  document.getElementById("export-log").addEventListener("click", exportLog);
  document.getElementById("backup-db").addEventListener("click", backupDb);
  document.getElementById("restore-db").addEventListener("click", restoreDb);
  document.getElementById("refresh-log").addEventListener("click", refreshLogs);

  document.querySelectorAll(".tab").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(btn => btn.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(panel => panel.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(button.dataset.tab).classList.add("active");
    });
  });

  setMode("borrow");
  refreshLogs();
});

function drawOverlay() {
  const width = video.videoWidth || 640;
  const height = video.videoHeight || 480;
  canvas.width = width;
  canvas.height = height;
  ctx.clearRect(0, 0, width, height);
  requestAnimationFrame(drawOverlay);
}

















































































































































