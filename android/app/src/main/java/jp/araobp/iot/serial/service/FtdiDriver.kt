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
class FtdiDriver: SerialService() {

    companion object {
        private val TAG = javaClass.simpleName
        val READBUF_SIZE = 1024
        val DELIMITER = "\n"
        private val mDelimiter = '\n'
    }

    private var mD2xxManager: D2xxManager? = null
    private var mFtdiDevice: FT_Device? = null

    private val mReadBuf = ByteArray(READBUF_SIZE)
    private val mCharBuf = CharArray(READBUF_SIZE)
    private var mReadLen = 0

    /**
     * Sets FTDI device config
     */
    private fun setConfig(baudrate: Int, dataBits: Byte, stopBits: Byte, parity: Byte, flowControl: Byte) {
        val dataBitsByte: Byte
        val stopBitsByte: Byte
        val parityByte: Byte
        val flowCtrlSetting: Short

        mFtdiDevice!!.setBitMode(0.toByte(), D2xxManager.FT_BITMODE_RESET)
        mFtdiDevice!!.setBaudRate(baudrate)

        when (dataBits) {
            7.toByte() -> dataBitsByte = D2xxManager.FT_DATA_BITS_7
            8.toByte() -> dataBitsByte = D2xxManager.FT_DATA_BITS_8
            else -> dataBitsByte = D2xxManager.FT_DATA_BITS_8
        }

        when (stopBits) {
            1.toByte() -> stopBitsByte = D2xxManager.FT_STOP_BITS_1
            2.toByte() -> stopBitsByte = D2xxManager.FT_STOP_BITS_2
            else -> stopBitsByte = D2xxManager.FT_STOP_BITS_1
        }

        when (parity) {
            0.toByte() -> parityByte = D2xxManager.FT_PARITY_NONE
            1.toByte() -> parityByte = D2xxManager.FT_PARITY_ODD
            2.toByte() -> parityByte = D2xxManager.FT_PARITY_EVEN
            3.toByte() -> parityByte = D2xxManager.FT_PARITY_MARK
            4.toByte() -> parityByte = D2xxManager.FT_PARITY_SPACE
            else -> parityByte = D2xxManager.FT_PARITY_NONE
        }
        mFtdiDevice!!.setDataCharacteristics(dataBitsByte, stopBitsByte, parityByte)

        when (flowControl) {
            0.toByte() -> flowCtrlSetting = D2xxManager.FT_FLOW_NONE
            1.toByte() -> flowCtrlSetting = D2xxManager.FT_FLOW_RTS_CTS
            2.toByte() -> flowCtrlSetting = D2xxManager.FT_FLOW_DTR_DSR
            3.toByte() -> flowCtrlSetting = D2xxManager.FT_FLOW_XON_XOFF
            else -> flowCtrlSetting = D2xxManager.FT_FLOW_NONE
        }
        mFtdiDevice!!.setFlowControl(flowCtrlSetting, 0x0b.toByte(), 0x0d.toByte())
    }

    // reader thread
    private val mReader = Runnable {
        var i: Int
        var len: Int
        var offset = 0
        var c: Char
        while (true) {
            len = mFtdiDevice!!.queueStatus
            if (len > 0) {
                mReadLen = len
                if (mReadLen > READBUF_SIZE) {
                    mReadLen = READBUF_SIZE
                }
                mFtdiDevice!!.read(mReadBuf, mReadLen)
                Log.d("FTDI", mReadBuf.toString())

                i = 0
                while (i < mReadLen) {
                    c = mReadBuf[i].toChar()
                    mCharBuf[offset++] = c
                    if (c == mDelimiter) {
                        rx(String(mCharBuf, 0, offset - 1))
                        offset = 0
                    }
                    i++
                }
            }
        }
    }

    /**
     * Opens FTDI device and start reader thread
     *
     * @parameter baudrate baud rate
     * @return true if FTDI device is opened successfully
     */
    override fun open(baudrate: Int): Boolean {
        var opened = false
        mD2xxManager = D2xxManager.getInstance(this.applicationContext)

        var devCount = mD2xxManager!!.createDeviceInfoList(this)
        Log.d(TAG, "Device number : " + Integer.toString(devCount))

        val deviceList = arrayOfNulls<D2xxManager.FtDeviceInfoListNode>(devCount)
        mD2xxManager!!.getDeviceInfoList(devCount, deviceList)

        if (devCount > 0) {
            mFtdiDevice = mD2xxManager!!.openByIndex(this, 0)
            if (mFtdiDevice!!.isOpen) {
                setConfig(baudrate, 8.toByte(), 1.toByte(), 0.toByte(), 0.toByte())
                mFtdiDevice!!.purge(D2xxManager.FT_PURGE_TX or D2xxManager.FT_PURGE_RX)
                mFtdiDevice!!.restartInTask()
                Thread(mReader).start()
                opened = true
            }
        }
        return opened
    }

    /**
     * Transmits a message to FTDI device
     */
    override fun tx(message: String) {
        val data = message + DELIMITER
        if (mFtdiDevice == null) {
            return
        }

        synchronized(mFtdiDevice as FT_Device) {
            if (!mFtdiDevice!!.isOpen) {
                Log.e(TAG, "onClickWrite : device is not openDevice")
                return
            }

            mFtdiDevice!!.latencyTimer = 16.toByte()

            val writeByte = data.toByteArray()
            mFtdiDevice!!.write(writeByte, data.length)
        }
    }

    /**
     * Stops reader thread and closes FTDI device
     */
    override fun close() {
        if (mFtdiDevice != null) {
            mFtdiDevice!!.close()
        }
    }
}
