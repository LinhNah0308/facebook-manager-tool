from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# API Thêm tài khoản bằng Cookie
@app.route("/api/add_account", methods=["POST"])
def add_account():
    data = request.json
    cookie = data.get("cookie", "").strip()
    
    if not cookie:
        return jsonify({"success": False, "message": "Cookie không được để trống!"})
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": cookie
        }
        # Lấy thông tin cá nhân qua Graph API
        res = requests.get("https://graph.facebook.com/me?fields=id,name", headers=headers, timeout=10)
        user_data = res.json()
        
        if "id" not in user_data:
            return jsonify({"success": False, "message": "Cookie đã die hoặc không hợp lệ!"})
            
        uid = user_data["id"]
        name = user_data.get("name", "Unknown")
        
        # Lấy danh sách Fanpage quản lý
        pages_res = requests.get(f"https://graph.facebook.com/{uid}/accounts?fields=id,name", headers=headers, timeout=10)
        pages_data = pages_res.json()
        pages_list = pages_data.get("data", [])
        
        return jsonify({
            "success": True,
            "account": {
                "uid": uid,
                "name": name,
                "cookie": cookie,
                "status": "LIVE",
                "pages": pages_list
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi kết nối: {str(e)}"})

# API Check Live/Die Cookie
@app.route("/api/check_status", methods=["POST"])
def check_status():
    data = request.json
    cookie = data.get("cookie", "")
    try:
        headers = {"Cookie": cookie}
        res = requests.get("https://graph.facebook.com/me?fields=id", headers=headers, timeout=5)
        if "id" in res.text:
            return jsonify({"status": "LIVE"})
        else:
            return jsonify({"status": "DIE"})
    except:
        return jsonify({"status": "DIE"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
