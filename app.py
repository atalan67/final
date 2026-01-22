import socket
import threading
from flask import Flask
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

def handle_remote_to_ws(remote_socket, ws):
    """وظيفة لنقل البيانات من الأنترنت الحقيقي إلى المستخدم عبر النفق"""
    try:
        while True:
            data = remote_socket.recv(4096)
            if not data: break
            ws.send(data)
    except:
        pass
    finally:
        remote_socket.close()

@sock.route('/proxy')
def handle_tunnel(ws):
    remote_socket = None
    try:
        while True:
            # استقبال البيانات من التطبيق (العميل)
            message = ws.receive()
            if not message: break

            # إذا كان أول اتصال، خاصنا نعرفو الوجهة
            if remote_socket is None:
                # 'قالب': العميل كيصيفط أول باكيت فيها العنوان والبورت (مثلا "google.com:443")
                try:
                    target_info = message.decode('utf-8').split(':')
                    target_host = target_info[0]
                    target_port = int(target_info[1])

                    # فتح الاتصال بالأنترنت
                    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    remote_socket.connect((target_host, target_port))

                    # تشغيل خيط لنقل البيانات العكسية (من الأنترنت للتليفون)
                    threading.Thread(target=handle_remote_to_ws, args=(remote_socket, ws), daemon=True).start()
                    continue # كمل باش تبدا تصيفط الداتا الحقيقية
                except:
                    break

            # صيفط الداتا الحقيقية للأنترنت
            remote_socket.sendall(message)
    except:
        pass
    finally:
        if remote_socket: remote_socket.close()

if __name__ == "__main__":
    import os
    # البورت اللي كتعطيه ليك الاستضافة (Render/PythonAnywhere)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
      
