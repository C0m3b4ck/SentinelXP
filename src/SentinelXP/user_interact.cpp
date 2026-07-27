#include <iostream>

void greet()
{
    std::cout << "///////------===== SentinelXP =====------////// \n";
    std::cout << "|||| By C0m3b4ck under APL 2.0, ALPHA RELEASE |||| \n";
}

void goodbye()
{
    std::cout << "/> Goodbye from SentinelXP ALPHA /> \n";
    std::cout << ":) Please report any errors, that will greatly help with development :) \n";
}

void aboutapp()
{
    std::cout << "I|I SentinelXP Command Line Interface I|I \n";
    std::cout << "> By C0m3b4ck under APL 2.0, ALPHA release > \n";
    std::cout << "Currently unfinished, might contain a lot of bugs \n";
}

void check_input(short input_to_check, short menu_num)
{
    // a case for each option number per menu
    switch(input_to_check)
    {
        case(0):
            // do nothing so that main() proceeds to return 0
            break;
        case(1):
            localscan_menu();
            break;
        case(2):
            inspectapp_menu();
            break;
        case(3):
            sentinelml_menu();
            break;
        case(4):
            manageservices_menu();
            break;
        case(5):
            manageconnections_menu();
            break;
        case(6):
            onlineprotectionservices_menu();
            break;
        case(7):
            activemonitoring_menu();
            break;
        case(8):
            activemonitoringsettings_menu();
            break;
        case(9):
            onlineprotectionservicessettings_menu();
            break;
        case(10):
            offlineprotectionsettings_menu();
            break;
        case(11):
            generalappsettings_menu();
            break;
        case(12):
            aboutapp();
            main_menu();
            break;
    }
}

void main_menu()
{
    std::cout << "/|/|/| MAIN MENU /|/|/| \n";
    std::cout << "--> Options: \n";
    std::cout << "1> Perform a scan \n";
    std::cout << "2> Inspect application \n";
    std::cout << "3> Start SentinelML \n";
    std::cout << "4> Manage services \n";
    std::cout << "5> Manage connections \n";
    std::cout << "6> Start/stop online protection services \n";
    std::cout << "7> Start/stop active monitoring \n";
    std::cout << "8> Active monitoring settings \n";
    std::cout << "9> Online protection settings \n";
    std::cout << "10> Offline protection settings \n";
    std::cout << "11> General app settings \n";
    std::cout << "12> About application \n";
    std::cout << "0> close application \n";

    short choice;
    std::cout << "[] Select number: " << choice << "\n";
    std::cin>>choice;
    check_input(choice, 0); //main menu num is 0
}


