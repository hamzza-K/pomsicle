import requests as req

sess = req.Session()

body = {
    "Approved": True,
    "DLL": "POMS_BaseObject_Lib",
    "Domain": "",
    "Folder": "",
    "IncludeLatest": False,
    "IncludeLatestApproved": False,
    "Latest": True,
    "Level": 10,
    "Location": 4,
    "ObjectID": "177406",
    "SearchSubType": "",
    "SubType": "MM_OBJ",
    "TreeIdentifier": "",
    "Type": "",
    "ignoreObsolete": False,
    "userID": "administrator"
}

url = "http://crkrv-khanrham1/poms/apps/eSpecWebApplication/SpecificationManagement.aspx/GetObjectVersions"

resp = sess.post(url, json=body)

print(resp.json())