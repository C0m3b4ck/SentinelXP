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
        current_dir = os.path.dirname(os.path.abspath(sys.executable))
        hashes_folder = os.path.join(current_dir, "hashes")
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
        if any(matches.values()):
            f.write("Potential malicious file detected!\n")
        else:
            for db_type, score in similarity_scores.items():
                if score > 0.0:
                    f.write("Similarity Score (%s): %.2f%%\n" % (db_type.upper(), score))

def delete_file(file_path):
    try:
        os.remove(file_path)
        print("File deleted: %s" % file_path)
    except Exception as e:
        print("Error deleting file %s: %s" % (file_path, str(e)))

def main():
    config = read_config('config.ini')
    if not config:
        print("No configuration found. Using default paths.")
    
    hash_databases = {}
    current_dir = os.path.dirname(os.path.abspath(sys.executable))
    hash_databases['sha256'] = os.path.join(current_dir, 'hashes', 'sha256.txt')
    hash_databases['md5'] = os.path.join(current_dir, 'hashes', 'md5.txt')
    hash_databases['sha1'] = os.path.join(current_dir, 'hashes', 'sha1.txt')

    log_dir = os.path.join(current_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    log_file = os.path.join(log_dir, 'fhash_compare_%s.txt' % timestamp)

    while True:
        print("\nOptions:")
        print("1. Scan a single file")
        print("2. Scan a directory")
        print("3. Exit")
        
        choice = raw_input("Enter your choice (1-3): ")
        
        if choice == '1':
            file_path = raw_input("\nEnter the path to the file: ").strip()
            if os.path.isfile(file_path):
                hashes = {}
                for hash_type in ['sha256', 'md5', 'sha1']:
                    print("Computing %s hash..." % hash_type)
                    hashes[hash_type] = compute_hash(file_path, hash_type)
                
                matches = {'sha256': False, 'md5': False, 'sha1': False}
                for hash_type in ['sha256', 'md5', 'sha1']:
                    computed_hash = hashes.get(hash_type)
                    if computed_hash:
                        with open(hash_databases[hash_type], 'r') as f:
                            known_hashes = [line.strip() for line in f]
                            if computed_hash in known_hashes:
                                matches[hash_type] = True
                
                similarity_scores = {}
                for hash_type in ['sha256', 'md5', 'sha1']:
                    computed_hash = hashes.get(hash_type)
                    if computed_hash:
                        with open(hash_databases[hash_type], 'r') as f:
                            known_hashes = [line.strip() for line in f]
                            max_similarity = 0
                            for known_hash in known_hashes:
                                similarity = compute_similarity(computed_hash, known_hash)
                                if similarity > max_similarity:
                                    max_similarity = similarity
                            similarity_scores[hash_type] = max_similarity
                
                print("\nResults for file:", file_path)
                output = []
                output.append("\nHashes computed:")
                output.append("SHA256: %s" % (hashes['sha256'] if hashes.get('sha256') else "Error computing SHA256"))
                output.append("MD5: %s" % (hashes['md5'] if hashes.get('md5') else "Error computing MD5"))
                output.append("SHA1: %s" % (hashes['sha1'] if hashes.get('sha1') else "Error computing SHA1"))
                
                output.append("\nMatches found in hash databases:")
                for hash_type, matched in matches.items():
                    output.append("%s: %s" % (hash_type.upper(), 'Match' if matched else 'No match'))
                
                output.append("\nSimilarity scores:")
                for hash_type, score in similarity_scores.items():
                    output.append("%s Similarity: %.2f%%" % (hash_type.upper(), score))
                    
                print "\n".join(output)
                
                save_scan_log(log_file, file_path, hashes, matches, similarity_scores)

                if any(matches.values()):
                    confirm_delete = raw_input("Potential malicious file detected. Delete file? (Y/N): ").strip().lower()
                    if confirm_delete == 'y':
                        delete_file(file_path)
            else:
                print("Invalid file path.")
        
        elif choice == '2':
            directory = raw_input("\nEnter the path to the directory: ").strip()
            if os.path.isdir(directory):
                file_paths, total_files = scan_directory(directory)
                for file_path in file_paths:
                    hashes = {}
                    for hash_type in ['sha256', 'md5', 'sha1']:
                        print("Computing %s hash for %s..." % (hash_type, file_path))
                        hashes[hash_type] = compute_hash(file_path, hash_type)
                    
                    matches = {'sha256': False, 'md5': False, 'sha1': False}
                    for hash_type in ['sha256', 'md5', 'sha1']:
                        computed_hash = hashes.get(hash_type)
                        if computed_hash:
                            with open(hash_databases[hash_type], 'r') as f:
                                known_hashes = [line.strip() for line in f]
                                if computed_hash in known_hashes:
                                    matches[hash_type] = True
                    
                    similarity_scores = {}
                    for hash_type in ['sha256', 'md5', 'sha1']:
                        computed_hash = hashes.get(hash_type)
                        if computed_hash:
                            with open(hash_databases[hash_type], 'r') as f:
                                known_hashes = [line.strip() for line in f]
                                max_similarity = 0
                                for known_hash in known_hashes:
                                    similarity = compute_similarity(computed_hash, known_hash)
                                    if similarity > max_similarity:
                                        max_similarity = similarity
                                similarity_scores[hash_type] = max_similarity
                    
                    print("\nResults for file:", file_path)
                    output = []
                    output.append("\nHashes computed:")
                    output.append("SHA256: %s" % (hashes['sha256'] if hashes.get('sha256') else "Error computing SHA256"))
                    output.append("MD5: %s" % (hashes['md5'] if hashes.get('md5') else "Error computing MD5"))
                    output.append("SHA1: %s" % (hashes['sha1'] if hashes.get('sha1') else "Error computing SHA1"))
                    
                    output.append("\nMatches found in hash databases:")
                    for hash_type, matched in matches.items():
                        output.append("%s: %s" % (hash_type.upper(), 'Match' if matched else 'No match'))
                    
                    output.append("\nSimilarity scores:")
                    for hash_type, score in similarity_scores.items():
                        output.append("%s Similarity: %.2f%%" % (hash_type.upper(), score))
                        
                    print "\n".join(output)
                    
                    save_scan_log(log_file, file_path, hashes, matches, similarity_scores)

                    if any(matches.values()):
                        confirm_delete = raw_input("Potential malicious file detected. Delete file? (Y/N): ").strip().lower()
                        if confirm_delete == 'y':
                            delete_file(file_path)
                print("\nScanned %d files in total." % total_files)
            else:
                print("Invalid directory path.")
        
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    print("-------++++++=========+++++++++-------")
    print("-+= Hash Comparer from Sentinel XP =+-")
    print("-------++++++=========+++++++++-------")
    main()
