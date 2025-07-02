#include <iostream>
#include <string>
#include <vector>
#include <cctype>

// Convert string to lowercase for case-insensitive matching
std::string toLower(const std::string& s) {
    std::string result = s;
    for (size_t i = 0; i < result.size(); ++i)
        result[i] = std::tolower(result[i]);
    return result;
}

// Check if keyword exists in input (simple substring search)
bool containsKeyword(const std::string& input, const std::string& keyword) {
    return input.find(keyword) != std::string::npos;
}

struct QA {
    std::vector<std::string> keywords;
    std::string answer;
};

int main() {
    // Define keyword-answer pairs related to antivirus
    std::vector<QA> knowledgeBase;

    knowledgeBase.push_back(QA{ {"virus", "infection"}, 
        "To remove a virus, run a full system scan with your antivirus software." });

    knowledgeBase.push_back(QA{ {"update", "definition", "database"}, 
        "Make sure your antivirus definitions are up to date for best protection." });

    knowledgeBase.push_back(QA{ {"scan", "full scan"}, 
        "A full scan checks all files on your computer for threats." });

    knowledgeBase.push_back(QA{ {"real-time", "protection"}, 
        "Real-time protection monitors your system continuously for threats." });

    knowledgeBase.push_back(QA{ {"quarantine", "remove"}, 
        "Quarantined files are isolated to prevent harm; you can remove them safely." });

    knowledgeBase.push_back(QA{ {"help", "support"}, 
        "For help, visit our support page or contact customer service." });

    std::cout << "Antivirus Chatbot (type 'exit' to quit)\n";

    while (true) {
        std::cout << "\nYou: ";
        std::string userInput;
        std::getline(std::cin, userInput);

        if (toLower(userInput) == "exit")
            break;

        std::string inputLower = toLower(userInput);
        bool answered = false;

        // Search knowledge base for matching keywords
        for (size_t i = 0; i < knowledgeBase.size(); ++i) {
            for (size_t k = 0; k < knowledgeBase[i].keywords.size(); ++k) {
                if (containsKeyword(inputLower, knowledgeBase[i].keywords[k])) {
                    std::cout << "Bot: " << knowledgeBase[i].answer << "\n";
                    answered = true;
                    break;
                }
            }
            if (answered) break;
        }

        if (!answered) {
            std::cout << "Bot: Sorry, I don't understand. Can you rephrase?\n";
        }
    }

    std::cout << "Goodbye!\n";
    return 0;
}
