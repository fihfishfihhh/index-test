APP_NAME = "Thư viện trường học"
SECRET_KEY = "dev-secret-change-me-123"
DEV_KEY = "library-dev-key-2025"
DB_PATH = "data/library.db"
UPLOAD_FOLDER = "uploads"
EXPORT_FOLDER = "exports"
TIME_ZONE = "Asia/Ho_Chi_Minh"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024
LOAN_DAYS = 5
MAX_BOOKS_PER_STUDENT = 3
FACE_CONFIDENCE_THRESHOLD = 10.0
FACE_SIZE_THRESHOLD = 10.0
LIVENESS_ACTIONS = ["open_mouth", "turn_head", "blink"]

# Công thức đề xuất: % = 100 * (1 - normalized_distance) * size_factor
# normalized_distance dựa trên khoảng cách mắt-mũi, lệch khung mặt so với trung tâm.
# size_factor = min(1, face_area / target_area), target_area = 0.18 * frame_area
# Nếu % < 10 => không cho quét.
FACE_CONFIDENCE_FORMULA = "confidence_percent = 100 * (1 - normalized_distance) * size_factor"
