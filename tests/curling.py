import requests as req

url = "http://crkrv-khanrham1/poms/apps/eSpecWebApplication/SpecificationManagement.aspx/GetObjectVersions"

payload = { 
    "Approved": True,
    "DLL": "POMS_BaseObject_Lib",
    "Domain": "",
    "Folder": "",
    "IncludeLatest": False,
    "IncludeLatestApproved": False,
    "Latest": True,
    "Level": 10,
    "Location": 4,
    "ObjectID": "base_cont",
    "SearchSubType": "",
    "SubType": "MM_OBJ",
    "TreeIdentifier": "",
    "Type": "",
    "ignoreObsolete": False,
    "userID": "administrator"
}

res = req.post(url, json=payload)

print(res.json())