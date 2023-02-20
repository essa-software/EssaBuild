#include <generated/Data.hpp>
#include <iostream>

int main() {
    for (auto const& entry: Data::entries) {
        std::cout << entry.name << " = " << entry.value << std::endl;
    }
}
