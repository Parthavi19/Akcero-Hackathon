# cleanup_artifacts.py
from app.db import SessionLocal
from app import models

db = SessionLocal()
meeting_id = "d0c9bd96-b609-4420-a6bf-0004c6059d81"
artifacts = db.query(models.Artifact).filter_by(meeting_id=meeting_id).all()
seen = set()
keepers = []
for a in artifacts:
    if a.transcript_text not in seen:
        seen.add(a.transcript_text)
        keepers.append(a.id)
    else:
        db.delete(a)
db.commit()
db.close()
print(f"Kept artifacts: {keepers}")
print("Duplicate artifacts removed.")
