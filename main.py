import os
import time
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cryptography.fernet import Fernet

class SecureSyncHandler(FileSystemEventHandler):
    def __init__(self, secret_key, target_storage):
        self.fernet = Fernet(secret_key)
        self.target_storage = target_storage

    def on_modified(self, event):
        if not event.is_directory:
            self.sync_file(event.src_path)

    def sync_file(self, file_path):
        try:
            filename = os.path.basename(file_path)
            print(f"[*] Обнаружено изменение файла: {filename}. Шифрование...")
            
            with open(file_path, "rb") as f:
                raw_data = f.read()
                
            encrypted_data = self.fernet.encrypt(raw_data)
            destination = os.path.join(self.target_storage, f"{filename}.enc")
            
            with open(destination, "wb") as f:
                f.write(encrypted_data)
                
            print(f"[+] Файл {filename} защищен и синхронизирован в облако/облачный диск.")
        except Exception as e:
            print(f"[!] Ошибка синхронизации: {e}")

class CloudSyncEdge:
    def __init__(self, watch_dir, target_dir):
        self.watch_dir = watch_dir
        self.target_dir = target_dir
        
        # Генерируем ключ шифрования (в реальном проекте он хранится в .env)
        self.key = Fernet.generate_key()
        
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

    def start_monitoring(self):
        event_handler = SecureSyncHandler(self.key, self.target_dir)
        observer = Observer()
        observer.schedule(event_handler, path=self.watch_dir, recursive=False)
        observer.start()
        print(f"[+] Система запущена. Мониторинг папки: {self.watch_dir}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    # Локальные пути для демонстрации
    source_folder = "./MyDocuments"
    cloud_folder = "./NetworkCloudStorage"
    
    if not os.path.exists(source_folder): os.makedirs(source_folder)
        
    agent = CloudSyncEdge(source_folder, cloud_folder)
    # Запуск в отдельном потоке, чтобы не вешать систему
    monitor_thread = Thread(target=agent.start_monitoring, daemon=True)
    monitor_thread.start()
    
    print("[*] Создайте или измените любой файл в папке 'MyDocuments' для теста...")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("[*] Остановка CloudSync.")