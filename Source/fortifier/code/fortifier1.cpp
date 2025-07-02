#include <iostream>
#include <string>
#include <windows.h>

void DisableUSBAutorun() {
    HKEY hKey;
    LONG result = RegOpenKeyEx(
        HKEY_LOCAL_MACHINE,
        
"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
        0, KEY_SET_VALUE | KEY_CREATE_SUB_KEY, &hKey
    );

    if (result == ERROR_SUCCESS) {
        DWORD noDriveTypeAutoRun = 145;
        result = RegSetValueEx(
            hKey,
            "NoDriveTypeAutoRun",
            0,
            REG_DWORD,
            reinterpret_cast<BYTE*>(&noDriveTypeAutoRun),
            sizeof(noDriveTypeAutoRun)
        );

        if (result != ERROR_SUCCESS) {
            std::cerr << "Failed to disable USB Autorun.\n";
        } else {
            std::cout << "USB Autorun disabled successfully.\n";
        }

        RegCloseKey(hKey);
    } else {
        std::cerr << "Failed to open registry key for disabling USB Autorun." <<std::endl;
    };
}

void DisableFileSharing() {
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
            std::cerr << "Failed to disable File Sharing.\n";
        } else {
            std::cout << "File Sharing disabled successfully.\n";
        }

        RegCloseKey(hKey);
    } else {
        std::cerr << "Failed to open registry key for disabling File Sharing." <<std::endl;
    };
}

void DisableInternetOnStartup() {
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
            std::cerr << "Failed to disable Internet Connection on Startup."<<std::endl;
        } else {
            std::cout << "Internet Connection on Startup disabled successfully."<<std::endl;
        }

        RegCloseKey(hKey);
    } else {
        std::cerr << "Failed to open registry key for disabling Internet Connection on Startup."<<std::endl;
    };
}

int main() {
    DisableUSBAutorun();
    DisableFileSharing();
    DisableInternetOnStartup();

    system("pause");
    return 0;
}
