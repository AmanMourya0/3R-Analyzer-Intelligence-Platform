with open("tests/test_three_r_classifier.py", "r") as f:
    content = f.read()

content = content.replace(
    'monkeypatch.setattr(app.clustering.three_r_classifier, "SIMILARITY_THRESHOLD", 0.90)',
    'monkeypatch.setattr(app.clustering.three_r_classifier.settings, "SIMILARITY_THRESHOLD", 0.90)'
)

with open("tests/test_three_r_classifier.py", "w") as f:
    f.write(content)
