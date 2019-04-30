# Chart GUI SPA (Single Page Application)

## IoT platform

==> **[iot-wireless](https://github.com/araobp/iot-wireless)**

## Architecture

```
  [ChartGUI/HTML5]<--MQTT/WebSocket---[mosquitto]<--MQTT---[gateway.py]<--BLE---[MEMS-mic/STM32]
           ^                               |
           |                               V
           +---------REST------------[API server]--[SQLite]
```

## References

- [C3.js](https://c3js.org/)
- [Vue.js](https://vuejs.org/)
- [MQTT over WebSocket](http://www.steves-internet-guide.com/using-javascript-mqtt-client-websockets/)

