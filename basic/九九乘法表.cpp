#include <iomanip>
#include <iostream>
using namespace std;
int main(){
    int c, r;
    for(c = 1; c <= 9; c++){
        for(r = 1; r <= c; r++){
            printf("%d * %d = %-4d", c, r, c * r);
        }
        printf("\n");
    }
    return 0;
}