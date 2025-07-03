#include <iostream>
#include <fstream>
#include <string>
#include <windows.h>

using namespace std;

void SaveSettings(const string& path, const bool usbAutorunDisabled,
                  const bool fileSharingDisabled, const bool 
internetOnStartupDisabled) {
    // Create directory if it doesn't exist
    string dir = "settings";
    system("mkdir settings 2> NUL");
    
    ofstream configFile(path.c_str()); // Fixed: Added .c_str()
    if (configFile.is_open()) {
        configFile << "[Settings]\n";
        configFile << "DisableUSBAutorun=" << (usbAutorunDisabled ? 
"Enabled" : "Disabled") << "\n";
        configFile << "DisableFileSharing=" << (fileSharingDisabled ? 
"Enabled" : "Disabled") << "\n";
        configFile << "DisableInternetOnStartup=" << 
(internetOnStartupDisabled ? "Enabled" : "Disabled");
        configFile.close();
    } else {
        cerr << "Unable to create configuration file.\n";
    }
}

struct Configuration {
    bool disableUSBAutorun;
    bool disableFileSharing;
    bool disableInternetOnStartup;
};

Configuration LoadSettings(const string& path) {
    Configuration config = {true, true, true}; // Default values
    ifstream configFile(path.c_str()); // Fixed: Added .c_str()
    
    if (configFile.is_open()) {
        string line;
        while (getline(configFile, line)) {
            if (line.find("[Settings]") != string::npos) continue; 
// Skip header
            
            size_t equalsPos = line.find('=');
            if (equalsPos == string::npos) continue; // Invalid format
            
            string key = line.substr(0, equalsPos);
            string value = line.substr(equalsPos + 1);
            
            if (key == "DisableUSBAutorun") {
                config.disableUSBAutorun = (value == "Enabled");
            } else if (key == "DisableFileSharing") {
                config.disableFileSharing = (value == "Enabled");
            } else if (key == "DisableInternetOnStartup") {
                config.disableInternetOnStartup = (value == "Enabled");
            }
        }
        configFile.close();
    } else {
        // If file doesn't exist, save default settings
        SaveSettings(path, true, true, true);
    }
    
    return config;
}

void ShowMenu() {
    cout << "\nSystem Configuration Menu:\n"
          << "1. Disable USB Autorun\n"
          << "2. Disable File Sharing\n"
          << "3. Disable Internet on Startup\n"
          << "4. Save and Exit\n"
          << "5. Restore Defaults\n"
          << "6. Show Current Settings\n"
          << "Enter your choice (1-6): ";
}

char GetMenuChoice() {
    char choice;
    cin >> choice;
    return tolower(choice);
}

void DisplayCurrentSettings(const Configuration& config) {
    cout << "\nCurrent Settings:\n";
    cout << "USB Autorun: " << (config.disableUSBAutorun ? "Disabled" : 
"Enabled") << endl;
    cout << "File Sharing: " << (config.disableFileSharing ? "Disabled" : 
"Enabled") << endl;
    cout << "Internet on Startup: " << 
(config.disableInternetOnStartup ? "Disabled" : "Enabled") << endl;
}

void ProcessMenuChoice(char choice, Configuration& config) {
    switch (choice) {
        case '1':
            config.disableUSBAutorun = !config.disableUSBAutorun;
            cout << "USB Autorun is now " << 
(config.disableUSBAutorun ? "Disabled" : "Enabled") << "\n";
            break;
        case '2':
            config.disableFileSharing = !config.disableFileSharing;
            cout << "File Sharing is now " << 
(config.disableFileSharing ? "Disabled" : "Enabled") << "\n";
            break;
        case '3':
            config.disableInternetOnStartup = 
!config.disableInternetOnStartup;
            cout << "Internet on Startup is now " << 
(config.disableInternetOnStartup ? "Disabled" : "Enabled") << "\n";
            break;
        case '4':
            SaveSettings("settings/fortifier.conf", 
config.disableUSBAutorun, 
                        config.disableFileSharing, 
config.disableInternetOnStartup);
            cout << "Settings saved and exiting...\n";
            exit(0);
        case '5':
            config = LoadSettings("settings/fortifier.conf");
            cout << "Defaults restored.\n";
            break;
        case '6':
            DisplayCurrentSettings(config);
            break;
        default:
            cout << "Invalid choice. Please try again.\n";
            break;
    }
}

void DisableUSBAutorun(const bool disable) {
    if (disable) {
        HKEY hKey;
        LONG result = RegOpenKeyEx(
            HKEY_LOCAL_MACHINE,
            
"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
            0, KEY_SET_VALUE | KEY_CREATE_SUB_KEY, &hKey
        );

        if (result == ERROR_SUCCESS) {
            DWORD noAutorun = 1;
            result = RegSetValueEx(
                hKey,
                "NoAutorun",
                0,
                REG_DWORD,
                reinterpret_cast<BYTE*>(&noAutorun),
                sizeof(noAutorun)
            );

            if (result != ERROR_SUCCESS) {
                cerr << "Failed to disable USB Autorun.\n";
            } else {
                cout << "USB Autorun disabled successfully.\n";
            }

            RegCloseKey(hKey);
        } else {
            cerr << "Failed to open registry key for disabling USBAutorun." << endl;
        }
    };
}

void DisableFileSharing(const bool disable) {
    if (disable) {
        HKEY hKey;
        LONG result = RegOpenKeyEx(
            HKEY_LOCAL_MACHINE,
            "SYSTEM\\CurrentControlSet\\Services\\LanmanServer",
            0, KEY_SET_VALUE, &hKey
        );

        if (result == ERROR_SUCCESS) {
            DWORD startValue = 4;
            result = RegSetValueEx(
                hKey,
                "Start",
                0,
                REG_DWORD,
                reinterpret_cast<BYTE*>(&startValue),
                sizeof(startValue)
            );

            if (result != ERROR_SUCCESS) {
                cerr << "Failed to disable File Sharing.\n";
            } else {
                cout << "File Sharing disabled successfully.\n";
            }

            RegCloseKey(hKey);
        } else {
            cerr << "Failed to open registry key for disabling File Sharing." << endl;
        };
    };
}

void DisableInternetOnStartup(const bool disable) {
    if (disable) {
        HKEY hKey;
        LONG result = RegOpenKeyEx(
            HKEY_CURRENT_USER,
            
"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
            0, KEY_SET_VALUE | KEY_CREATE_SUB_KEY, &hKey
        );

        if (result == ERROR_SUCCESS) {
            DWORD noInternetConnection = 1;
            result = RegSetValueEx(
                hKey,
                "NoDialSound",
                0,
                REG_DWORD,
                reinterpret_cast<BYTE*>(&noInternetConnection),
                sizeof(noInternetConnection)
            );

            if (result != ERROR_SUCCESS) {
                cerr << "Failed to disable Internet Connection on Startup.\n";
            } else {
                cout << "Internet Connection on Startup disabled successfully.\n";
            }

            RegCloseKey(hKey);
        } else {
            cerr << "Failed to open registry key for disabling Internet on Startup." << endl;
        }
    };
}

int main() {
    Configuration config = LoadSettings("settings/fortifier.conf");
    
    while (true) {
        ShowMenu();
        char choice = GetMenuChoice();
        ProcessMenuChoice(choice, config);
    }
}
