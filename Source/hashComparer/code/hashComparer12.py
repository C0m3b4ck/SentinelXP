import os
import hashlib
import difflib
from datetime import datetime
import sys

def read_config(config_file):
    if os.path.exists(config_file):
        # Read the config file and return its contents
        with open(config_file, 'r') as f:
            config = {}
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value.strip('"')
            return config
    else:
        # If no config file is found, look for the "hashes" folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        hashes_folder = os.path.join(script_dir, "hashes")
        if os.path.exists(hashes_folder):
            print("Using default 'hashes' folder.")
            return {"hashes_directory": hashes_folder}
    return None

def scan_directory(directory):
    file_paths = []
    total_files = 0  # Initialize total files counter
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths, total_files

def compute_hash(file_path, hash_type):
    try:
        if hash_type == 'sha256':
            h = hashlib.sha256()
        elif hash_type == 'md5':
            h = hashlib.md5()
        elif hash_type == 'sha1':
            h = hashlib.sha1()
        else:
            return None
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest().lower()
    except Exception as e:
        print("Error computing %s hash for %s: %s" % (hash_type, file_path, str(e)))
        return None

def compute_similarity(hash1, hash2):
    return difflib.SequenceMatcher(None, hash1, hash2).ratio() * 100

def save_scan_log(log_file, file_path, hashes, matches, similarity_scores):
    with open(log_file, 'a') as f:
        f.write("\nResults for file: %s\n" % file_path)
        f.write("SHA256: %s\nMD5: %s\nSHA1: %s\n" % (hashes['sha256'], hashes['md5'], hashes['sha1']))
        f.write("Matches:\n")
        for hash_type, matched in matches.items():
            f.write("%s: %s\n" % (hash_type.upper(), 'Match' if matched else 'No Match'))
        f.write("Similarity scores:\n")
        for hash_type, score in similarity_scores.items():
            f.write("%s Similarity: %.2f%%\n" % (hash_type.upper(), score))

def delete_file(file_path):
    try:
        os.remove(file_path)
        print("File deleted:", file_path)
    except Exception as e:
        print("Error deleting file:", str(e))

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = read_config(os.path.join(script_dir, "config.txt"))

    if not config or 'hashes_directory' not in config:
        print("Configuration error. Please ensure the 'config.txt' file is present and correctly configured.")
        return

    hashes_folder = config['hashes_directory']
    hash_databases = {
        'sha256': os.path.join(hashes_folder, "sha256.txt"),
        'md5': os.path.join(hashes_folder, "md5.txt"),
        'sha1': os.path.join(hashes_folder, "sha1.txt")
    }

    for db_path in hash_databases.values():
        if not os.path.exists(db_path):
            print("Error: Hash database file not found:", db_path)
            return

    print("-------++++++=========+++++++++-------")
    print("-+= Hash Comparer from Sentinel XP =+-")
    print("-------++++++=========+++++++++-------")

    while True:
        choice = raw_input("\nOptions:\n1. Scan a single file\n2. Scan a directory\n3. Exit\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            file_path = raw_input("Enter the path to the file: ").strip()
            if not os.path.isfile(file_path):
                print("Invalid file path.")
                continue
            
            hashes = {}
            for hash_type in ['sha256', 'md5', 'sha1']:
                print("Computing %s hash for %s..." % (hash_type, file_path))
                hashes[hash_type] = compute_hash(file_path, hash_type)
            
            matches = {hash_type: False for hash_type in ['sha256', 'md5', 'sha1']}
            similarity_scores = {hash_type: 0.0 for hash_type in ['sha256', 'md5', 'sha1']}

            for hash_type, db_path in hash_databases.items():
                with open(db_path, 'r') as f:
                    known_hashes = [line.strip() for line in f]
                    if hashes[hash_type] in known_hashes:
                        matches[hash_type] = True

                max_similarity = 0.0
                for known_hash in known_hashes:
                    similarity = compute_similarity(hashes[hash_type], known_hash)
                    if similarity > max_similarity:
                        max_similarity = similarity
                similarity_scores[hash_type] = max_similarity
            
            print("\nResults for file:", file_path)
            print("Hashes computed:")
            print("SHA256: %s" % hashes['sha256'])
            print("MD5: %s" % hashes['md5'])
            print("SHA1: %s" % hashes['sha1'])
            
            print("\nMatches found in hash databases:")
            for hash_type, matched in matches.items():
                print("%s: %s" % (hash_type.upper(), 'Match' if matched else 'No Match'))
            
            print("\nSimilarity scores:")
            for hash_type, score in similarity_scores.items():
                print("%s Similarity: %.2f%%" % (hash_type.upper(), score))
            
            save_scan_log(os.path.join(script_dir, "scan_log.txt"), file_path, hashes, matches, similarity_scores)

            if any(matches.values()):
                confirm_delete = raw_input("Potential malicious file detected. Delete file? (Y/N): ").strip().lower()
                if confirm_delete == 'y':
                    delete_file(file_path)
        
        elif choice == '2':
            directory = raw_input("\nEnter the path to the directory: ").strip()
            if not os.path.isdir(directory):
                print("Invalid directory path.")
                continue
            
            file_paths, total_files = scan_directory(directory)
            
            for file_path in file_paths:
                hashes = {}
                for hash_type in ['sha256', 'md5', 'sha1']:
                    print("Computing %s hash for %s..." % (hash_type, file_path))
                    hashes[hash_type] = compute_hash(file_path, hash_type)
                
                matches = {hash_type: False for hash_type in ['sha256', 'md5', 'sha1']}
                similarity_scores = {hash_type: 0.0 for hash_type in ['sha256', 'md5', 'sha1']}

                for hash_type, db_path in hash_databases.items():
                    with open(db_path, 'r') as f:
                        known_hashes = [line.strip() for line in f]
                        if hashes[hash_type] in known_hashes:
                            matches[hash_type] = True

                    max_similarity = 0.0
                    for known_hash in known_hashes:
                        similarity = compute_similarity(hashes[hash_type], known_hash)
                        if similarity > max_similarity:
                            max_similarity = similarity
                    similarity_scores[hash_type] = max_similarity
                
                print("\nResults for file:", file_path)
                print("Hashes computed:")
                print("SHA256: %s" % hashes['sha256'])
                print("MD5: %s" % hashes['md5'])
                print("SHA1: %s" % hashes['sha1'])
                
                print("\nMatches found in hash databases:")
                for hash_type, matched in matches.items():
                    print("%s: %s" % (hash_type.upper(), 'Match' if matched else 'No Match'))
                
                print("\nSimilarity scores:")
                for hash_type, score in similarity_scores.items():
                    print("%s Similarity: %.2f%%" % (hash_type.upper(), score))
                
                save_scan_log(os.path.join(script_dir, "scan_log.txt"), file_path, hashes, matches, similarity_scores)

                if any(matches.values()):
                    confirm_delete = raw_input("Potential malicious file detected. Delete file? (Y/N): ").strip().lower()
                    if confirm_delete == 'y':
                        delete_file(file_path)
            
            print("\nScanned %d files in total." % total_files)
        
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
