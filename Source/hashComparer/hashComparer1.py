import hashlib
import os

def read_config(config_file):
    config = {}
    if not os.path.exists(config_file):
        return None
    with open(config_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

def compute_hash(file_path, hash_type='sha256'):
    try:
        hash_func = hashlib.new(hash_type)
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                hash_func.update(data)
        return hash_func.hexdigest()
    except Exception as e:
        print("Error computing %s hash: %s" % (hash_type, str(e)))
        return None

def load_hash_db(file_path):
    try:
        hashes = set()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    hash_val = line.strip().lower()
                    if hash_val:
                        hashes.add(hash_val)
        return hashes
    except Exception as e:
        print("Error loading hash database: %s" % str(e))
        return None

def main():
    config_file = 'settings/hash_paths.conf'
    config = read_config(config_file)
    
    if not config:
        print("Could not find configuration file or it's empty")
        return
    
    hash_paths = {}
    for key, value in config.items():
        if os.path.exists(value):
            hash_paths[key] = value
        else:
            print("Path %s does not exist" % value)
    
    if not hash_paths:
        print("No valid paths found in configuration file")
        return
    
    sha256_db = set()
    md5_db = set()
    sha1_db = set()
    
    for db_type, path in hash_paths.items():
        full_path = os.path.join(path, 'full_%s.txt' % db_type)
        if db_type == 'sha256':
            sha256_db.update(load_hash_db(full_path))
        elif db_type == 'md5':
            md5_db.update(load_hash_db(full_path))
        elif db_type == 'sha1':
            sha1_db.update(load_hash_db(full_path))
    
    while True:
        file_path = raw_input("Enter file path to scan (or 'q' to quit): ")
        if file_path.lower() == 'q':
            break
        
        if not os.path.exists(file_path):
            print("File does not exist")
            continue
        
        sha256_hash = compute_hash(file_path, 'sha256')
        md5_hash = compute_hash(file_path, 'md5')
        sha1_hash = compute_hash(file_path, 'sha1')
        
        found_malware = False
        if sha256_hash in sha256_db:
            print("!!! SHA256 hash match found - potentially malicious file !!!")
            found_malware = True
        if md5_hash in md5_db:
            print("!!! MD5 hash match found - potentially malicious file !!!")
            found_malware = True
        if sha1_hash in sha1_db:
            print("!!! SHA1 hash match found - potentially malicious file !!!")
            found_malware = True
        
        if not found_malware:
            print("No matches found in malware databases")
        
        print("\nHashes computed:")
        print("SHA256: %s" % sha256_hash)
        print("MD5: %s" % md5_hash)
        print("SHA1: %s\n" % sha1_hash)

if __name__ == "__main__":
    print("-------++++++=========+++++++++-------")
    print("-+= Hash Comparer from Sentinel XP =+-")
    print("-------++++++=========+++++++++-------")
    print("\n")
    main()
