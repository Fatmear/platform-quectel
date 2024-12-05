#include "ql_api_osi.h"
#include "ql_debug.h"

void app_main(){
    while(1){
        ql_debug("Hello world!\n");
        ql_rtos_task_sleep_ms(1000);
    }
}
