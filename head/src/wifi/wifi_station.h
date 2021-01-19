#ifndef __WIFI_STATION_H__
#define __WIFI_STATION_H__

#include "esp_system.h"

/* The examples use WiFi configuration that you can set via project configuration menu
   If you'd rather not, just change the below entries to strings with
   the config you want - ie #define EXAMPLE_WIFI_SSID "mywifissid"
*/
#define EXAMPLE_ESP_WIFI_SSID      WIFI_SSID
#define EXAMPLE_ESP_WIFI_PASS      WIFI_PASSWORD
#define EXAMPLE_ESP_MAXIMUM_RETRY  3

/* The event group allows multiple bits for each event, but we only care about two events:
 * - we are connected to the AP with an IP
 * - we failed to connect after the maximum amount of retries */
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT      BIT1


void wifi_init();

#endif
