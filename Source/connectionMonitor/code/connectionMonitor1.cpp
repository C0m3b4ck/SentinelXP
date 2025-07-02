#include <windows.h>
#include <iphlpapi.h>
#include <tlhelp32.h>
#include <winsock2.h>  // For ntohs()
#include <iostream>
#include <map>
#include <fstream>
#include <ctime>

#pragma comment(lib, "Iphlpapi.lib")
#pragma comment(lib, "Ws2_32.lib")  // Linking with winsock library

typedef std::map<DWORD, std::string> ProcessMap;

ProcessMap loadProcessNames() {
    ProcessMap processMap;
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) return processMap;

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (!Process32First(hSnapshot, &pe32)) {
        CloseHandle(hSnapshot);
        return processMap;
    }

    do {
        processMap[pe32.th32ProcessID] = std::string(pe32.szExeFile);
    } while (Process32Next(hSnapshot, &pe32));

    CloseHandle(hSnapshot);
    return processMap;
}

DWORD getOwningProcess(DWORD pid) {
    DWORD dwProcessId = 0;

    HANDLE hThreadSnap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
    if (hThreadSnap != INVALID_HANDLE_VALUE) {
        THREADENTRY32 te32;
        te32.dwSize = sizeof(te32);

        if (!Thread32First(hThreadSnap, &te32)) {
            CloseHandle(hThreadSnap);
            return dwProcessId; // If no threads found
        }

        do {
            if (te32.th32OwnerProcessID == pid) {
                dwProcessId = te32.th32OwnerProcessID;
                break;
            }
        } while (Thread32Next(hThreadSnap, &te32));

        CloseHandle(hThreadSnap);
    }

    return dwProcessId;
}

void captureConnections(const ProcessMap& processMap) {
    PMIB_TCPTABLE pTcpTable = NULL;
    DWORD dwSize = 0;

    if (GetTcpTable(pTcpTable, &dwSize, TRUE) == ERROR_INSUFFICIENT_BUFFER) {
        pTcpTable = (PMIB_TCPTABLE)malloc(dwSize);
        if (!pTcpTable) return;
    }

    if (GetTcpTable(pTcpTable, &dwSize, TRUE) != NO_ERROR) {
        free(pTcpTable);
        return;
    }

    std::ofstream logFile("logs/callhome_log.txt", std::ios_base::app);

    if (!logFile.is_open()) {
        std::cerr << "Unable to open log file!" << std::endl;
        free(pTcpTable);
        return;
    }

    time_t now = time(0);
    char* dt = ctime(&now);
    logFile << "---------- " << dt << " ----------" << std::endl;

    for (DWORD i = 0; i < pTcpTable->dwNumEntries; ++i) {
        const MIB_TCPROW& row = pTcpTable->table[i];

        // Get the owning process by using a heuristic or local port
        DWORD dwProcessId = getOwningProcess(row.dwLocalPort);

        std::string processName = "Unknown";
        ProcessMap::const_iterator it = processMap.find(dwProcessId);
        if (it != processMap.end()) {
            processName = it->second;
        }

        char localAddr[16], remoteAddr[16];
        sprintf(localAddr, "%d.%d.%d.%d",
                row.dwLocalAddr & 0xff,
                (row.dwLocalAddr >> 8) & 0xff,
                (row.dwLocalAddr >> 16) & 0xff,
                (row.dwLocalAddr >> 24) & 0xff);

        sprintf(remoteAddr, "%d.%d.%d.%d",
                row.dwRemoteAddr & 0xff,
                (row.dwRemoteAddr >> 8) & 0xff,
                (row.dwRemoteAddr >> 16) & 0xff,
                (row.dwRemoteAddr >> 24) & 0xff);

        char localPort[6], remotePort[6];
        sprintf(localPort, "%u", ntohs(row.dwLocalPort));
        sprintf(remotePort, "%u", ntohs(row.dwRemotePort));

        std::string connectionStr = processName + " (" + localAddr
                                    + ") -> " + localAddr + ":" + localPort
                                    + " <-> " + remoteAddr + ":" + remotePort;

        // Highlight internet connections in red
        const char* colorCode = "\033[1;31m";  // ANSI escape code for bold red text
        const char* resetCode = "\033[0m";

        if (row.dwState != MIB_TCP_STATE_CLOSED) {
            logFile << connectionStr << std::endl;
            std::cout << colorCode << connectionStr << resetCode << std::endl;
        } else {
            logFile << connectionStr << std::endl;
            std::cout << connectionStr << std::endl;
        }
    }

    // Separator line
    logFile << "-------------" << std::endl;

    if (pTcpTable) free(pTcpTable);
}

int main() {
    // Create the logs directory if it doesn't exist
    CreateDirectory("logs", NULL);

    ProcessMap processMap = loadProcessNames();

    while (true) {
        captureConnections(processMap);
        Sleep(5000);  // Poll every 5 seconds
    }

    return 0;
}
