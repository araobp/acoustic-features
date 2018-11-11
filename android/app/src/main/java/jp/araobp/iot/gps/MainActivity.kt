package jp.araobp.iot.gps

import android.content.BroadcastReceiver
import android.content.Context
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.text.method.ScrollingMovementMethod
import android.util.Log
import android.widget.TextView
import jp.araobp.iot.R
import jp.araobp.iot.serial.Message

import org.greenrobot.eventbus.EventBus
import org.greenrobot.eventbus.Subscribe
import org.greenrobot.eventbus.ThreadMode
import android.content.Intent
import android.content.IntentFilter
import android.hardware.usb.UsbManager
import jp.araobp.iot.serial.service.FtdiDriver
import jp.araobp.iot.serial.service.FtdiSimulator
import android.hardware.usb.UsbDevice
import android.os.Parcelable
import android.app.PendingIntent




class MainActivity : AppCompatActivity() {

    private var mTextView: TextView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Register this activity with EventBus
        EventBus.getDefault().register(this)

        // Start SerialService
        // Note: use FtdiSimulator instead of FtdiDriver for testing the code on Android simulator
        // val intent = Intent(application, FtdiSimulator::class.java)
        val intent = Intent(application, FtdiDriver::class.java)
        startService(intent)

        setContentView(R.layout.activity_main)

        mTextView = findViewById(R.id.textView)
        mTextView!!.movementMethod = ScrollingMovementMethod()

    }

    override fun onDestroy() {
        super.onDestroy()
        EventBus.getDefault().unregister(this)
    }


    @Subscribe(threadMode = ThreadMode.MAIN)
    fun onMessage(message: Message) {
        mTextView!!.append(message.message + "\n")
    }

}
