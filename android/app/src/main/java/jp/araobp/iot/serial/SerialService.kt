package jp.araobp.iot.serial

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import org.greenrobot.eventbus.EventBus

abstract class SerialService : Service() {

    private val mEventBus = EventBus.getDefault()

    companion object {
        const val BAUDRATE = 9600
        const val SLEEP_TIMER = 1000L
    }

    override fun onCreate() {
        while (true) {
            if(open(BAUDRATE)) {
               break
            } else {
                Thread.sleep(SLEEP_TIMER)
            }
        }
        //mEventBus.register(this)
        super.onCreate()
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onDestroy() {
        close()
        mEventBus.unregister(this)
        super.onDestroy()
    }

    protected abstract fun open(baudrate: Int): Boolean

    abstract fun tx(message: String)

    protected abstract fun close()

    protected fun rx(message: String) {
        mEventBus.post(Message(message))
    }

}

