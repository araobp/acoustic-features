package jp.araobp.iot.serial.service

import android.util.Log

import com.ftdi.j2xx.D2xxManager
import com.ftdi.j2xx.FT_Device
import jp.araobp.iot.serial.SerialService
import kotlin.experimental.or

/**
 * FTDI device driver
 *
 */
class FtdiSimulator : SerialService() {

    companion object {
        const val NEMA_DATA = "${'$'}PMTK741,24.772816,121.022636,160,2011,8,1,08,00,00\n"
        const val SLEEP = 1000L  // 1sec interval
    }

    private val mCharBuf = NEMA_DATA.toCharArray()

    /**
     * Sets FTDI device config
     */
    private fun setConfig(baudrate: Int, dataBits: Byte, stopBits: Byte, parity: Byte, flowControl: Byte) {
        Log.d("setConfig", "$baudrate, $dataBits, $stopBits, $parity, $flowControl")
    }

    // reader thread
    private val mReader = Runnable {
        var offset = NEMA_DATA.length
        while (true) {
            rx(String(mCharBuf, 0, offset - 1))
            Thread.sleep(SLEEP)
        }
    }

    /**
     * Opens FTDI device and start reader thread
     *
     * @parameter baudrate baud rate
     * @return true if FTDI device is opened successfully
     */
    override fun open(baudrate: Int): Boolean {
        setConfig(baudrate, 8.toByte(), 1.toByte(), 0.toByte(), 0.toByte())
        Thread(mReader).start()
        return true
    }

    /**
     * Transmits a message to FTDI device
     */
    override fun tx(message: String) {
        Log.d("tx", message)
    }

    /**
     * Stops reader thread and closes FTDI device
     */
    override fun close() {
    }
}
