#include "ql_api_osi.h"
#include "ql_uart.h"

void app_main(){
    while(1){
        ql_uart_log("Hello world!\n");
        ql_rtos_task_sleep_ms(1000);
    }
}
