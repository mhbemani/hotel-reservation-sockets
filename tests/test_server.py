"""End-to-end tests: start the real server on a copy of the project and talk to it over TCP."""
import json, os, shutil, socket, subprocess, sys, tempfile, time, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8766
ADMIN_ID, USER_ID, RICH_USER_ID = 0, 8, 7   # ids from the demo data in server/data/UsersInfo.json


def call(action, params):
    with socket.create_connection(("127.0.0.1", PORT), timeout=5) as s:
        s.sendall((json.dumps({"action": action, "params": params}) + "\n").encode())
        buf = b""
        while b"\n" not in buf:
            buf += s.recv(65536)
    return json.loads(buf.split(b"\n")[0])


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.copy = os.path.join(cls.tmp, "hotel")
        shutil.copytree(ROOT, cls.copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "logs"))
        cfg_path = os.path.join(cls.copy, "server", "data", "config.json")
        with open(cfg_path) as f:
            cfg = json.load(f)
        cfg["commandChannelPort"] = PORT
        with open(cfg_path, "w") as f:
            json.dump(cfg, f)
        cls.proc = subprocess.Popen([sys.executable, "server.py"], cwd=os.path.join(cls.copy, "server"),
                                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
        cls.proc.stdin.write("21-02-2025\n")
        cls.proc.stdin.flush()
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", PORT), timeout=1).close()
                break
            except OSError:
                time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.proc.kill()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_admin_sees_all_users_without_passwords(self):
        r = call("view_all_users", {"id": ADMIN_ID})
        self.assertEqual(r["code"], "001")
        self.assertFalse(any("password" in u for u in r["data"]))

    def test_non_admin_cannot_list_users(self):
        self.assertEqual(call("view_all_users", {"id": USER_ID})["code"], "403")
        self.assertEqual(call("view_all_users", {})["code"], "403")

    def test_non_admin_cannot_manage_rooms(self):
        r = call("admin_rooms", {"id": USER_ID, "cmd": "add", "room": "998", "price": 1, "maxCapacity": 1})
        self.assertEqual(r["code"], "403")

    def test_booking_rejects_non_positive_beds(self):
        for beds in (-5, 0):
            r = call("booking", {"id": USER_ID, "room": "211", "beds": beds, "checkin": "01-03-2025", "checkout": "03-03-2025"})
            self.assertEqual(r["code"], "401")

    def test_valid_booking_succeeds(self):
        r = call("booking", {"id": RICH_USER_ID, "room": "211", "beds": 1, "checkin": "10-03-2025", "checkout": "12-03-2025"})
        self.assertEqual(r["code"], "104")


if __name__ == "__main__":
    unittest.main()
