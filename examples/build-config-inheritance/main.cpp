#include "lib.h"
#include <iostream>

int main()
{
    std::cout << "lib scope: " << scope() << std::endl;
    std::cout << "main scope: " << SCOPE << std::endl;
}
