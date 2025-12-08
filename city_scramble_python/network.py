"""
Simple Multiplayer Network Module for City Scramble
Uses a relay server with room codes for easy matchmaking
"""

import socket
import threading
import json
import random
import string
import time

DEFAULT_PORT = 7777

def get_local_ip():
    """Get local IP address that is visible to other computers"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class RelayServer:
    """Lightweight relay server forwarding messages between two players"""
    
    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self.running = False
        self.rooms = {}  # room_code -> [socket1, socket2]
        
    def start(self):
        """Start server in background thread"""
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server.bind(('0.0.0.0', self.port))
            self.server.listen(5)
            self.running = True
            thread = threading.Thread(target=self._run, daemon=True)
            thread.start()
            print(f"✓ Server läuft auf Port {self.port}")
            return True
        except:
            return False
    
    def _run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                threading.Thread(target=self._handle, args=(conn,), daemon=True).start()
            except:
                break
    
    def _handle(self, conn):
        room = None
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                
                if msg['type'] == 'create':
                    room = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    self.rooms[room] = [conn, None]
                    conn.send(json.dumps({'type': 'created', 'code': room}).encode())
                    
                elif msg['type'] == 'join':
                    room = msg['code']
                    if room in self.rooms and self.rooms[room][1] is None:
                        self.rooms[room][1] = conn
                        conn.send(json.dumps({'type': 'joined'}).encode())
                        self.rooms[room][0].send(json.dumps({'type': 'ready'}).encode())
                    else:
                        conn.send(json.dumps({'type': 'error'}).encode())
                        
                else:  # Relay message
                    if room and room in self.rooms:
                        other = self.rooms[room][1] if conn == self.rooms[room][0] else self.rooms[room][0]
                        if other:
                            other.send(data)
        except:
            pass
        finally:
            if room and room in self.rooms:
                del self.rooms[room]
                
    def stop(self):
        self.running = False
        self.server.close()


class GameClient:
    """Client for multiplayer connection"""
    
    def __init__(self):
        self.socket = None
        self.connected = False
        self.messages = []
        self.room_code = None
        
    def connect(self, host='127.0.0.1', port=DEFAULT_PORT):
        """Connect to server"""
        try:
            self.socket = socket.socket()
            self.socket.connect((host, port))
            self.connected = True
            threading.Thread(target=self._receive, daemon=True).start()
            return True
        except:
            return False
    
    def create_room(self):
        """Create and return room code"""
        self.send({'type': 'create'})
        for _ in range(50):  # Wait 5 seconds
            for msg in self.messages[:]:
                if msg.get('type') == 'created':
                    self.room_code = msg['code']
                    self.messages.remove(msg)
                    return self.room_code
            time.sleep(0.1)
        return None
    
    def join_room(self, code):
        """Join room by code"""
        self.send({'type': 'join', 'code': code})
        for _ in range(50):
            for msg in self.messages[:]:
                if msg.get('type') == 'joined':
                    self.room_code = code
                    self.messages.remove(msg)
                    return True
                elif msg.get('type') == 'error':
                    self.messages.remove(msg)
                    return False
            time.sleep(0.1)
        return False
    
    def send(self, data):
        """Send message"""
        if self.connected:
            try:
                self.socket.send(json.dumps(data).encode())
            except:
                self.connected = False
    
    def _receive(self):
        """Receive messages"""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if data:
                    self.messages.append(json.loads(data.decode()))
                else:
                    break
            except:
                break
        self.connected = False
    
    def get_messages(self):
        """Get and clear messages"""
        msgs = self.messages[:]
        self.messages.clear()
        return msgs
    
    def close(self):
        """Disconnect"""
        self.connected = False
        if self.socket:
            self.socket.close()


# Global server instance
_server = None

def ensure_server():
    """Ensure server is running"""
    global _server
    if _server is None:
        _server = RelayServer()
        return _server.start()
    return True
