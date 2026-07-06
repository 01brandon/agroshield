import json, sys

BASE = "https://agroshield-production-f5fc.up.railway.app"

def build_collection():
    collection = {
        "info": {
            "name": "AgroShield API",
            "description": "Complete API collection for AgroShield. Run Auth - Login first to save your access token automatically.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}]},
        "variable": [
            {"key": "base_url", "value": BASE, "type": "string"},
            {"key": "access_token", "value": "", "type": "string"},
            {"key": "refresh_token", "value": "", "type": "string"},
        ],
        "item": []
    }

    def folder(name, requests):
        return {"name": name, "item": requests}

    def req(method, name, path, body=None, auth=True, description=""):
        headers = [{"key": "Content-Type", "value": "application/json"}]
        if auth:
            headers.append({"key": "Authorization", "value": "Bearer {{access_token}}"})
        item = {
            "name": name,
            "request": {
                "method": method,
                "header": headers,
                "url": {"raw": "{{base_url}}" + path, "host": ["{{base_url}}"], "path": [p for p in path.split("/") if p]},
                "description": description
            },
            "event": [{
                "listen": "test",
                "script": {"exec": [
                    "if (pm.response.code === 200 || pm.response.code === 201) {",
                    "  try {",
                    "    var json = pm.response.json();",
                    "    if (json.access)  pm.environment.set('access_token',  json.access);",
                    "    if (json.refresh) pm.environment.set('refresh_token', json.refresh);",
                    "    if (json.id)      pm.environment.set('last_id', json.id);",
                    "  } catch(e) {}",
                    "}",
                    "pm.test('Status ok', function() {",
                    "  pm.expect(pm.response.code).to.be.oneOf([200,201,204]);",
                    "});"
                ], "type": "text/javascript"}
            }]
        }
        if body:
            item["request"]["body"] = {"mode": "raw", "raw": json.dumps(body, indent=2), "options": {"raw": {"language": "json"}}}
        return item

    collection["item"] = [
        folder("Auth", [
            req("POST", "Register",         "/api/auth/register/",        {"first_name":"John","last_name":"Doe","email":"john@farm.com","password":"Testpass123!","password2":"Testpass123!","role":"farmer","phone":"+254712345678","country":"Kenya"}, False),
            req("POST", "Login",            "/api/auth/login/",           {"email":"brandonmukuria@gmail.com","password":"Testpass123!"}, False),
            req("POST", "Refresh Token",    "/api/auth/token/refresh/",   {"refresh":"{{refresh_token}}"}, False),
            req("POST", "Logout",           "/api/auth/logout/",          {"refresh":"{{refresh_token}}"}),
            req("GET",  "Get Profile",      "/api/auth/profile/"),
            req("PATCH","Update Profile",   "/api/auth/profile/",         {"first_name":"Brandon","phone":"+254725035925","country":"Kenya"}),
            req("POST", "Change Password",  "/api/auth/change-password/", {"old_password":"Testpass123!","new_password":"NewPass456!"}),
        ]),
        folder("Farms", [
            req("GET",    "List My Farms",  "/api/farms/"),
            req("POST",   "Create Farm",    "/api/farms/",  {"name":"Green Valley Farm","location_name":"Nakuru, Kenya","latitude":-0.3031,"longitude":36.08,"size_hectares":"5.50","primary_crop":"maize","description":"Family farm in the Rift Valley."}),
            req("GET",    "Get Farm",       "/api/farms/1/"),
            req("PATCH",  "Update Farm",    "/api/farms/1/", {"description":"Updated description."}),
            req("DELETE", "Delete Farm",    "/api/farms/1/"),
        ]),
        folder("Crop Disease Detection", [
            req("GET",    "List Scans",      "/api/disease/"),
            req("POST",   "Submit Scan",     "/api/disease/", {"farm":1,"cloudinary_url":"https://res.cloudinary.com/dfk5falaw/image/upload/v1/agroshield/scans/sample.jpg","notes":"Yellowing on lower leaves"}),
            req("GET",    "Get Scan",        "/api/disease/1/"),
            req("DELETE", "Delete Scan",     "/api/disease/1/"),
        ]),
        folder("Weather", [
            req("GET",  "List Alerts",       "/api/weather/alerts/"),
            req("GET",  "List Readings",     "/api/weather/readings/"),
            req("POST", "Refresh Weather",   "/api/weather/readings/refresh/"),
        ]),
        folder("Marketplace", [
            req("GET",  "Browse Listings",     "/api/marketplace/listings/"),
            req("POST", "Create Listing",      "/api/marketplace/listings/", {"farm":1,"crop":"maize","grade":"A","quantity_kg":"500","price_per_kg":"45.00","description":"Fresh harvest.","is_auction":False}),
            req("GET",  "My Listings",         "/api/marketplace/listings/mine/"),
            req("GET",  "List Bids",           "/api/marketplace/bids/"),
            req("POST", "Place Bid",           "/api/marketplace/bids/", {"listing":1,"amount":"22000.00"}),
            req("POST", "Accept Bid",          "/api/marketplace/bids/1/accept/"),
            req("POST", "Reject Bid",          "/api/marketplace/bids/1/reject/"),
            req("GET",  "List Escrow",         "/api/marketplace/escrow/"),
            req("POST", "Pay Escrow (M-Pesa)", "/api/marketplace/escrow/1/pay/", {"phone":"0725035925"}),
            req("POST", "Release Escrow",      "/api/marketplace/escrow/1/release/"),
        ]),
        folder("Community Forum", [
            req("GET",  "List Posts",        "/api/forum/posts/"),
            req("POST", "Create Post",       "/api/forum/posts/", {"title":"Why are my maize leaves turning yellow?","body":"Yellowing from the bottom leaves upward in Nakuru.","crop_tag":"maize"}),
            req("POST", "AI Co-Pilot Answer","/api/forum/posts/1/ai_answer/"),
            req("POST", "Upvote Post",       "/api/forum/posts/1/upvote/"),
            req("GET",  "List Replies",      "/api/forum/replies/?post=1"),
            req("POST", "Add Reply",         "/api/forum/replies/", {"post":1,"body":"This looks like nitrogen deficiency."}),
        ]),
        folder("Carbon Credits", [
            req("GET",  "List Activities",   "/api/carbon/"),
            req("POST", "Log Activity",      "/api/carbon/", {"farm":1,"practice":"agroforestry","area_hectares":"5.0","estimated_tonnes":"12.5"}),
            req("GET",  "Get Activity",      "/api/carbon/1/"),
            req("DELETE","Delete Activity",  "/api/carbon/1/"),
        ]),
        folder("Finance", [
            req("GET",  "List Ledger",       "/api/finance/ledger/"),
            req("POST", "Log Entry",         "/api/finance/ledger/", {"farm":1,"entry_type":"sale","description":"Maize sale to cooperative","amount":"22500.00","date":"2026-07-01"}),
            req("GET",  "P&L Summary",       "/api/finance/ledger/summary/"),
            req("DELETE","Delete Entry",     "/api/finance/ledger/1/"),
        ]),
        folder("Satellite", [
            req("GET",  "List NDVI Readings","/api/satellite/"),
            req("POST", "Refresh NDVI",      "/api/satellite/refresh/"),
        ]),
        folder("Global Search", [
            req("GET", "Search All", "/api/search/?q=maize"),
        ]),
        folder("Cooperatives", [
            req("GET",  "List Cooperatives", "/api/cooperatives/"),
            req("POST", "Create Cooperative","/api/cooperatives/", {"name":"Nakuru Farmers Cooperative","description":"Joint marketing.","location":"Nakuru, Kenya"}),
        ]),
        folder("Livestock", [
            req("GET",  "List Animals",      "/api/livestock/animals/"),
            req("POST", "Add Animal",        "/api/livestock/animals/", {"farm":1,"species":"cattle","breed":"Friesian","tag_number":"KE-001"}),
            req("GET",  "List Health Records","/api/livestock/health/"),
            req("POST", "Log Health Record", "/api/livestock/health/", {"animal":1,"symptom":"limping on left front leg","treatment":"applied iodine, rest recommended"}),
        ]),
        folder("Soil", [
            req("GET",  "List Soil Readings","/api/soil/"),
            req("POST", "Log Soil Reading",  "/api/soil/", {"farm":1,"ph":6.5,"nitrogen":45,"phosphorus":30,"potassium":200,"source":"manual"}),
        ]),
        folder("Seeds", [
            req("GET",  "List Seeds",        "/api/seeds/"),
        ]),
        folder("Traceability", [
            req("GET",  "List Batches",      "/api/traceability/batches/"),
            req("POST", "Add Entry",         "/api/traceability/entries/", {"batch":1,"action":"transported","notes":"Delivered to Nakuru depot"}),
        ]),
        folder("Drones", [
            req("GET",  "List Operators",    "/api/drones/operators/"),
            req("POST", "Book Drone",        "/api/drones/bookings/", {"operator":1,"service_date":"2026-07-15","area_hectares":5,"total_cost":"2500.00"}),
            req("GET",  "My Bookings",       "/api/drones/bookings/"),
        ]),
        folder("Equipment", [
            req("GET",  "List Equipment",    "/api/equipment/listings/"),
            req("POST", "Book Equipment",    "/api/equipment/bookings/", {"equipment":1,"start_date":"2026-07-10","end_date":"2026-07-12","total_cost":"3000.00"}),
        ]),
        folder("Alerts", [
            req("GET",  "List Food Security Alerts", "/api/alerts/"),
        ]),
        folder("Account Settings", [
            req("GET",  "Account Page",      "/dashboard/account/"),
        ]),
    ]

    return collection

collection = build_collection()
with open("postman_collection.json", "w") as f:
    json.dump(collection, f, indent=2)

total = sum(len(folder["item"]) for folder in collection["item"])
print(f"generated postman_collection.json")
print(f"folders: {len(collection['item'])}")
print(f"total requests: {total}")
