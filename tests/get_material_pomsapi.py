import requests as req

mat = req.get("http://crkrv-khanrham1/poms-api/v1/Material/base")
print(mat.json())
