import os

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
        current_dir = os.path.dirname(os.path.realpath(__file__))
        hashes_folder = os.path.join(current_dir, "hashes")
        if os.path.exists(hashes_folder):
            print "Using default 'hashes' folder."
            return {"hashes_directory": hashes_folder}
    return None

def scan_directory(directory):
    import os
    file_paths = []
    total_files = 0  # Initialize total files counter
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths, total_files

def compute_hash(file_path, hash_type):
    import hashlib
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
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest().lower()
    except Exception as e:
        print "Error computing %s hash for %s: %s" % (hash_type, file_path, str(e))
        return None

def compute_similarity(hash1, hash2):
    import difflib
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

def main():
    config = read_config('config.ini')
    if not config:
        print "No configuration found. Using default paths."
    
    hash_databases = {}
    current_dir = os.path.dirname(os.path.realpath(__file__))
    hash_databases['sha256'] = os.path.join(current_dir, 'hashes', 'sha256.txt')
    hash_databases['md5'] = os.path.join(current_dir, 'hashes', 'md5.txt')
    hash_databases['sha1'] = os.path.join(current_dir, 'hashes', 'sha1.txt')

    log_file = os.path.join(current_dir, 'scan_log.txt')
    
    while True:
        print "\nOptions:"
        print "1. Scan a single file"
        print "2. Scan a directory"
        print "3. Exit"
        
        choice = raw_input("Enter your choice (1-3): ")
        
        if choice == '1':
            file_path = raw_input("\nEnter the path to the file: ").strip()
            if os.path.isfile(file_path):
                hashes = {}
                for hash_type in ['sha256', 'md5', 'sha1']:
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
                
                print "\nResults for file:", file_path
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
            else:
                print "Invalid file path."
        
        elif choice == '2':
            dir_path = raw_input("\nEnter the path to the directory: ").strip()
            if os.path.isdir(dir_path):
                files, total_files = scan_directory(dir_path)  # Get files and total count
                scanned_files = 0  # Initialize scanned files counter
                for file in files:
                    print "\nScanning: %s (%d/%d - %.1f%%)" % (file, scanned_files + 1, total_files, ((scanned_files + 1) / float(total_files)) * 100)
                    hashes = {}
                    for hash_type in ['sha256', 'md5', 'sha1']:
                        hashes[hash_type] = compute_hash(file, hash_type)
                    
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
                    
                    output = []
                    output.append("\nResults for file: %s" % file)
                    output.append("Hashes computed:")
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
                    
                    save_scan_log(log_file, file, hashes, matches, similarity_scores)
                    scanned_files += 1
                
                print "\nScan completed! Total files processed:", total_files
            else:
                print "Invalid directory path."
        
        elif choice == '3':
            break
        
        else:
            print "Invalid choice. Please enter 1, 2, or 3."

if __name__ == "__main__":
    main()
