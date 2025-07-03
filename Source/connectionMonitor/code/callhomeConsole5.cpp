#include <windows.h>
#include <iphlpapi.h>
#include <tlhelp32.h>
#include <iostream>
#include <map>

#pragma comment(lib, "iphlpapi.lib")

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

        std::cout << processName << " (" << dwProcessId
                  << ") -> " << localAddr << ":" << ntohs(row.dwLocalPort)
                  << " <-> " << remoteAddr << ":" << ntohs(row.dwRemotePort)
                  << std::endl;
    }

    if (pTcpTable) free(pTcpTable);
}

int main() {
    ProcessMap processMap = loadProcessNames();

    while (true) {
        captureConnections(processMap);
        Sleep(5000);  // Poll every 5 seconds
    }

    return 0;
}
