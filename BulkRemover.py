import os

directory = "ScrappedPositions"

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith("_specific.json"):
            os.remove(os.path.join(root, file))
